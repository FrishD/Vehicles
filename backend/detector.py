import cv2
import numpy as np
import os
import time
import json
from processing.stabilization import ObjectTracker
from processing.enhancement import ImageEnhancer
from logic.traffic_light import TrafficLightLogic
from logic.pedestrian import PedestrianLogic
from logic.infrastructure import InfrastructureLogic
from concurrent.futures import ThreadPoolExecutor

class VehicleDetector:
    def __init__(self, model_path='yolov8n.pt'):
        print("Initializing VehicleDetector...")
        self.tracker = ObjectTracker(model_path)
        self.enhancer = ImageEnhancer()
        self.gmc = None # Delayed init
        self.tl_logic = TrafficLightLogic()
        self.ped_logic = PedestrianLogic()
        self.infra_logic = InfrastructureLogic(frame_size=(1920, 1080)) # Default, will re-init if needed
        
        # Thread Pool for background tasks (Report Gen, LPR)
        self.executor = ThreadPoolExecutor(max_workers=2)
        
        # Classes COCO: 2=car, 3=motorcycle, 5=bus, 7=truck, 0=person, 9=traffic light
        self.vehicle_classes = [2, 3, 5, 7]
        self.person_class = 0
        self.traffic_light_class = 9
        
        # State used to prevent duplicate reporting
        self.reported_violations = {} 
        self.REPORT_COOLDOWN = 15.0 # Seconds before reporting same car again
        
        # BEHAVIORAL LEARNING STATE
        self.vehicle_history = {} # id -> {'last_pos': (x,y), 'last_time': t, 'velocity': v}
        self.last_frame_time = time.time()

    def _log_plate(self, plate, timestamp):
        """Logs a successfully read plate to a JSON file."""
        log_file = "backend/reports/plates.json"
        try:
            # Read existing data
            if os.path.exists(log_file) and os.path.getsize(log_file) > 0:
                with open(log_file, 'r') as f:
                    data = json.load(f)
            else:
                data = {"plates": []}

            # Append new plate
            new_entry = {
                "plate": plate,
                "time": timestamp.strftime("%H:%M:%S")
            }

            # Avoid duplicates
            if new_entry not in data["plates"]:
                data["plates"].insert(0, new_entry) # Prepend to keep it sorted by most recent
                data["plates"] = data["plates"][:20] # Keep only the last 20 entries

                # Write data back
                with open(log_file, 'w') as f:
                    json.dump(data, f, indent=4)

        except (IOError, json.JSONDecodeError) as e:
            print(f"Error logging plate: {e}")

    def _process_violation_task(self, frame, car_obj, violation_type, timestamp, filename_base):
        """
        Background task:
        1. Run LPR on the car crop.
        2. Generate PDF with the found ID.
        """
        try:
            # Crop car for LPR
            x1, y1, x2, y2 = car_obj['box']
            # Clamp coords
            h, w = frame.shape[:2]
            x1, y1 = max(0, x1), max(0, y1)
            x2, y2 = min(w, x2), min(h, y2)
            
            car_crop = frame[y1:y2, x1:x2]
            
            # 1. OCR (Safe import inside thread)
            from lpr import read_license_plate
            lpr_text = read_license_plate(car_crop)
            print(f"LPR Result for {car_obj['id']}: {lpr_text}")
            
            # If a valid plate is found, log it
            if lpr_text != "Unknown" and lpr_text != "LPR Error":
                self._log_plate(lpr_text, timestamp)

            # Save the crop for the report
            crop_path = f"backend/reports/images/{filename_base}_crop.jpg"
            cv2.imwrite(crop_path, car_crop)
            
            # 2. Logic: If valid LPR, use it. Else fall back to Tracker ID.
            display_id = lpr_text if lpr_text != "Unknown" else str(car_obj['id'])
            
            # 3. Save Image (Annotated with LPR result)
            report_img = frame.copy()
            cv2.rectangle(report_img, (x1, y1), (x2, y2), (0, 0, 255), 2)
            cv2.putText(report_img, f"LPR: {display_id}", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)
            
            img_path = f"backend/reports/images/{filename_base}.jpg"
            cv2.imwrite(img_path, report_img)

            # 4. PDF
            from reporting.pdf_generator import generate_violation_report
            
            date_str = timestamp.strftime("%Y-%m-%d")
            time_str = timestamp.strftime("%H:%M:%S")

            violation_data = {
                'date': date_str,
                'time': time_str,
                'vehicle_id': display_id, 
                'type': violation_type
            }
            pdf_path = f"backend/reports/pdfs/{filename_base}.pdf"
            generate_violation_report(violation_data, img_path, pdf_path, plate_image_path=crop_path)
            print(f"Report generated: {pdf_path}")
            
        except Exception as e:
            print(f"Error in background violation task: {e}")

    def handle_violation(self, frame, car_obj, violation_type):
        """
        Handles violation. Returns immediate data for UI, 
        and launches background task for heavy LPR/PDF.
        """
        from datetime import datetime
        
        timestamp = datetime.now()
        date_str = timestamp.strftime("%Y-%m-%d")
        time_str = timestamp.strftime("%H:%M:%S")
        
        # Ensure dirs
        if not os.path.exists("backend/reports/images"): os.makedirs("backend/reports/images")
        if not os.path.exists("backend/reports/pdfs"): os.makedirs("backend/reports/pdfs")
        
        filename_base = f"{timestamp.strftime('%Y%m%d_%H%M%S')}_{car_obj['id']}"
        
        # Launch background task
        # We pass a COPY of the frame to avoid race conditions
        self.executor.submit(self._process_violation_task, frame.copy(), car_obj, violation_type, timestamp, filename_base)
        
        # Return immediate object for UI (with Tracker ID)
        return {
            'id': car_obj['id'],
            'type': violation_type,
            'date': date_str,
            'time': time_str,
            'status': 'processing_report',
            'car_id': car_obj['id'], # Duplicate for compatibility
            'message': f"Processing violation for Vehicle {car_obj['id']}"
        }

    def process_frame(self, frame):
        current_time = time.time()
        dt = current_time - self.last_frame_time
        self.last_frame_time = current_time

        # Lazy init GMC
        from processing.stabilization import GMC
        if self.gmc is None:
            self.gmc = GMC()

        # 0. Measure Ego-Motion
        dx, dy = self.gmc.apply(frame)
        
        # 1. Enhancement
        enhanced_frame = self.enhancer.preprocess(frame)
        
        # 2. Tracking
        results = self.tracker.track(enhanced_frame)
        
        cars = []
        pedestrians = []
        traffic_lights = []
        
        if results.boxes:
            box_data = zip(
                results.boxes.xyxy, 
                results.boxes.cls, 
                results.boxes.id if results.boxes.id is not None else [None]*len(results.boxes.cls),
                results.boxes.conf
            )

            for box, cls, id_raw, conf in box_data:
                x1, y1, x2, y2 = map(int, box)
                cls = int(cls)
                conf = float(conf)
                obj_id = int(id_raw) if id_raw is not None else -1
                
                # Class-specific confidence filtering
                if cls in self.vehicle_classes:
                    if conf < 0.25: continue # Standard confidence for vehicles
                elif cls == self.traffic_light_class:
                    if conf < 0.15: continue # More aggressive for traffic lights
                else:
                    if conf < 0.2: continue # Pedestrians and others

                obj = {'box': [x1, y1, x2, y2], 'class': cls, 'id': obj_id, 'conf': conf}
                
                if cls in self.vehicle_classes:
                    # CALCULATE VELOCITY
                    cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
                    velocity = 999.0 # Default for new
                    if obj_id != -1 and obj_id in self.vehicle_history:
                        prev = self.vehicle_history[obj_id]
                        dist = np.sqrt((cx - prev['last_pos'][0])**2 + (cy - prev['last_pos'][1])**2)
                        if dt > 0:
                            velocity = dist / dt
                    
                    self.vehicle_history[obj_id] = {'last_pos': (cx, cy), 'last_time': current_time, 'velocity': velocity}
                    obj['velocity'] = velocity
                    cars.append(obj)
                elif cls == self.person_class:
                    pedestrians.append(obj)
                elif cls == self.traffic_light_class:
                    # Detect state using logic
                    tl_crop = frame[y1:y2, x1:x2] 
                    state = self.tl_logic.get_state(obj['id'], tl_crop)
                    obj['state'] = state
                    traffic_lights.append(obj)

        violations = []
        h, w = frame.shape[:2]
        current_time = time.time()
        
        # 3. Infrastructure Detection
        detected_objects = cars + pedestrians
        stop_lines, crosswalks = self.infra_logic.detect_infrastructure(frame, objects_to_mask=detected_objects)

        # 4. Pedestrian Violations
        ped_violations = self.ped_logic.check_yield_violations(cars, pedestrians, crosswalks)
        for pv in ped_violations:
            car_id = pv['car_id']
            if car_id in self.reported_violations and current_time - self.reported_violations[car_id] < self.REPORT_COOLDOWN:
                continue
            
            car_obj = next((c for c in cars if c['id'] == car_id), None)
            if car_obj:
               v_data = self.handle_violation(frame, car_obj, "Yield Violation")
               self.reported_violations[car_id] = current_time
               pv['date'] = v_data['date']
               pv['time'] = v_data['time']
               violations.append(pv)
        
        # 5. Red Light Violations
        for car in cars:
            car_id = car['id']
            if car_id in self.reported_violations:
                 if current_time - self.reported_violations[car_id] < self.REPORT_COOLDOWN:
                     continue 
            
            if car.get('velocity', 0) < 30:
                continue

            for tl in traffic_lights:
                if tl['state'] == 'red':
                    cx, cy = (car['box'][0] + car['box'][2]) / 2, car['box'][3]
                    
                    if self.tl_logic.is_associated(tl['id'], cx, cy, w, h):
                        v_data = self.handle_violation(frame, car, "Red Light Violation")
                        self.reported_violations[car_id] = current_time
                        
                        violations.append({
                            'type': 'red_light_violation',
                            'car_id': car['id'],
                            'tl_id': tl['id'],
                            'vehicle_id': car['id'],
                            'message': f"Car {car['id']} crossed Red Light {tl['id']}",
                            'date': v_data['date'],
                            'time': v_data['time']
                        })
        
        # 6. Annotation
        annotated_frame = enhanced_frame.copy()
        
        # Annotate crosswalks
        for poly in crosswalks:
            cv2.polylines(annotated_frame, [poly], isClosed=True, color=(255, 255, 0), thickness=2)
            cv2.putText(annotated_frame, "CROSSWALK", (poly[0][0], poly[0][1] - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)

        # Annotate other objects (cars, pedestrians, etc.)
        for ped in pedestrians:
            x1, y1, x2, y2 = ped['box']
            cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(annotated_frame, f"Ped {ped['id']}", (x1, y1-10), 0, 0.5, (0, 255, 0), 2)
            
        for car in cars:
            x1, y1, x2, y2 = car['box']
            color = (255, 0, 0) # Blue for cars
            
            is_violator = any(v['car_id'] == car['id'] for v in violations)
            if is_violator:
                color = (0, 0, 255) # Red for violators
                
            cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), color, 2)
            cv2.putText(annotated_frame, f"Car {car['id']}", (x1, y1-10), 0, 0.5, color, 2)
            
            if is_violator:
                 cv2.putText(annotated_frame, "VIOLATION!", (x1, y1-30), 0, 0.7, (0, 0, 255), 2)

        for tl in traffic_lights:
            x1, y1, x2, y2 = tl['box']
            state = tl['state']
            c = (200, 200, 200) 
            if state == 'red': c = (0, 0, 255)
            elif state == 'green': c = (0, 255, 0)
            elif state == 'yellow': c = (0, 255, 255)
            
            cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), c, 2)
            label = f"TL: {state} ({tl['conf']:.2f})"
            cv2.putText(annotated_frame, label, (x1, y1-10), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, c, 2)

        return annotated_frame, violations
