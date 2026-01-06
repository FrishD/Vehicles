from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import cv2
import base64
import json
import asyncio
import traceback
import os
from fastapi.responses import JSONResponse
from detector import VehicleDetector

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global instances
detector = None

@app.on_event("startup")
async def startup_event():
    global detector
    # Load model on startup
    try:
        detector = VehicleDetector()
    except Exception as e:
        print(f"Failed to load detector: {e}")
        traceback.print_exc()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, camera_id: int = 0):
    """
    WebSocket endpoint for live camera feed
    camera_id: 0 for default camera, 1, 2, etc. for other cameras
    """
    await websocket.accept()
    print(f"WebSocket connected. Camera ID: {camera_id}")

    # Open camera
    cap = cv2.VideoCapture(camera_id)

    if not cap.isOpened():
        error_msg = {"error": f"Failed to open camera {camera_id}"}
        await websocket.send_text(json.dumps(error_msg))
        await websocket.close()
        return

    # Set camera properties (optional)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    cap.set(cv2.CAP_PROP_FPS, 30)

    print(f"Camera {camera_id} opened successfully")

    try:
        while True:
            # Read frame from camera
            ret, frame = cap.read()

            if not ret:
                print("Failed to read frame from camera")
                await asyncio.sleep(0.1)
                continue

            # Process frame
            if detector:
                annotated_frame, violations = detector.process_frame(frame)
            else:
                annotated_frame = frame
                violations = []

            # Encode frame to JPEG
            success, buffer = cv2.imencode('.jpg', annotated_frame,
                                           [cv2.IMWRITE_JPEG_QUALITY, 85])
            if not success:
                continue

            # Convert to base64
            frame_b64 = base64.b64encode(buffer).decode('utf-8')

            # Send data
            payload = {
                "image": f"data:image/jpeg;base64,{frame_b64}",
                "violations": violations,
                "camera_id": camera_id
            }

            await websocket.send_text(json.dumps(payload))

            # Control frame rate (~30fps)
            await asyncio.sleep(0.033)

    except WebSocketDisconnect:
        print("WebSocket disconnected")
    except Exception as e:
        print(f"Error in websocket loop: {e}")
        traceback.print_exc()
    finally:
        # Release camera
        cap.release()
        print(f"Camera {camera_id} released")

@app.get("/")
def read_root():
    return {"status": "ok", "service": "Vehicle Violation Detection System (Live Camera)"}

@app.get("/cameras")
def list_cameras():
    """Check available cameras"""
    available = []
    for i in range(10):  # Check first 10 camera indices
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            available.append(i)
            cap.release()
    return {"available_cameras": available}

@app.get("/plates")
def get_plates():
    """Returns a list of previously scanned plates"""
    log_file = "backend/reports/plates.json"
    if not os.path.exists(log_file):
        return JSONResponse(content={"plates": []})

    with open(log_file, 'r') as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            data = {"plates": []} # Or handle error appropriately

    return JSONResponse(content=data)

@app.get("/violations")
def get_violations():
    """Returns a list of all recorded violations"""
    log_file = "backend/reports/violations.json"
    if not os.path.exists(log_file):
        return JSONResponse(content={"violations": []})

    with open(log_file, 'r') as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            data = {"violations": []}

    return JSONResponse(content=data)