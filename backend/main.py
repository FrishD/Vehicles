
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import cv2
import json
import asyncio
import os
from streamer import VideoStreamer
from detector import VehicleDetector
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files from the frontend public directory
# This allows the frontend to access captured images
script_dir = os.path.dirname(os.path.abspath(__file__))
frontend_public_path = os.path.join(script_dir, '..', 'frontend', 'public')
os.makedirs(os.path.join(frontend_public_path, 'captures'), exist_ok=True)
app.mount("/captures", StaticFiles(directory=os.path.join(frontend_public_path, 'captures')), name="captures")


class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"New connection: {websocket.client}. Total: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        logger.info(f"Connection closed: {websocket.client}. Total: {len(self.active_connections)}")

    async def broadcast_bytes(self, data: bytes):
        for connection in self.active_connections:
            await connection.send_bytes(data)

    async def broadcast_json(self, data: dict):
        for connection in self.active_connections:
            await connection.send_json(data)

video_manager = ConnectionManager()
violation_manager = ConnectionManager()
detector = None

@app.on_event("startup")
async def startup_event():
    global detector
    try:
        detector = VehicleDetector()
        logger.info("VehicleDetector loaded successfully.")
    except Exception as e:
        logger.error(f"Failed to load detector: {e}", exc_info=True)

@app.websocket("/ws/video")
async def websocket_video_endpoint(websocket: WebSocket):
    await video_manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text() # Keep connection alive
    except WebSocketDisconnect:
        video_manager.disconnect(websocket)

@app.websocket("/ws/violations")
async def websocket_violation_endpoint(websocket: WebSocket):
    await violation_manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text() # Keep connection alive
    except WebSocketDisconnect:
        violation_manager.disconnect(websocket)

async def processing_loop():
    logger.info("Starting processing loop with live camera feed")
    streamer = VideoStreamer(source=0) # Use camera feed

    while True:
        try:
            frame = streamer.get_frame()
            if frame is None:
                await asyncio.sleep(0.1)
                continue

            if detector:
                annotated_frame, violations = detector.process_frame(frame)

                # Handle violations and LPR
                if violations:
                    for violation in violations:
                        violation_data, lpr_data = detector.handle_violation(frame, violation['car_obj'])
                        # Broadcast violation alert
                        await violation_manager.broadcast_json({
                            "type": "violation",
                            "payload": violation_data
                        })
                        # Broadcast LPR capture if available
                        if lpr_data:
                            await violation_manager.broadcast_json({
                                "type": "lpr",
                                "payload": lpr_data
                            })
            else:
                annotated_frame = frame

            # Encode and broadcast video frame
            success, buffer = cv2.imencode('.jpg', annotated_frame, [cv2.IMWRITE_JPEG_QUALITY, 70])
            if success:
                await video_manager.broadcast_bytes(buffer.tobytes())

            await asyncio.sleep(0.033) # ~30fps

        except Exception as e:
            logger.error(f"Error in processing loop: {e}", exc_info=True)
            await asyncio.sleep(1) # Avoid spamming logs on persistent errors

    streamer.release()

@app.on_event("startup")
async def start_processing_loop():
    # This will run the processing loop in the background
    asyncio.create_task(processing_loop())

@app.get("/")
def read_root():
    return {"status": "ok", "service": "Vehicle Violation Detection System"}
