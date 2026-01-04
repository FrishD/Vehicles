from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import cv2
import base64
import json
import asyncio
import traceback
import os
from streamer import VideoStreamer
from detector import VehicleDetector

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global instances (lazy load?)
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
async def websocket_endpoint(websocket: WebSocket, source: str = "sample_traffic.mp4"):
    await websocket.accept()
    print(f"WebSocket connected. Source: {source}")
    
    # Get the absolute path to the video file
    script_dir = os.path.dirname(os.path.abspath(__file__))
    video_source = os.path.join(script_dir, source)
    
    streamer = VideoStreamer(source=video_source)
    
    try:
        while True:
            frame = streamer.get_frame()
            if frame is None:
                await asyncio.sleep(0.1)
                continue
            
            # Process
            if detector:
                annotated_frame, violations = detector.process_frame(frame)
            else:
                annotated_frame = frame
                violations = []
            
            # Encode frame
            success, buffer = cv2.imencode('.jpg', annotated_frame)
            if not success:
                continue
            
            # Convert to base64
            frame_b64 = base64.b64encode(buffer).decode('utf-8')
            
            # Send data
            payload = {
                "image": f"data:image/jpeg;base64,{frame_b64}",
                "violations": violations
            }
            
            await websocket.send_text(json.dumps(payload))
            
            # Control frame rate? ~30fps
            await asyncio.sleep(0.033)
            
    except WebSocketDisconnect:
        print("WebSocket disconnected")
    except Exception as e:
        print(f"Error in websocket loop: {e}")
        traceback.print_exc()
    finally:
        streamer.release()

@app.get("/")
def read_root():
    return {"status": "ok", "service": "Vehicle Violation Detection System"}
