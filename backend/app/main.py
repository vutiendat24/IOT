
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
import os

from app.routes import detect, roi, events
from app.services.yolo_detector import YoloDetector
from app.services.face_recognizer import FaceRecognizer
from app.services.firebase_service import FirebaseService
from app.websocket.manager import ConnectionManager
from app.utils.config import settings
from app.utils.logger import setup_logging

setup_logging()
logger = logging.getLogger(__name__)

ws_manager = ConnectionManager()


@asynccontextmanager
async def lifespan(app: FastAPI):
    
    logger.info("🚀 Starting Smart Intrusion Detection Backend...")
    
    try:
        # Load YOLOv8 model
        logger.info(f"Loading YOLOv8 model from {settings.YOLO_MODEL_PATH}...")
        if not os.path.exists(settings.YOLO_MODEL_PATH):
            logger.warning(f"  YOLOv8 model not found at {settings.YOLO_MODEL_PATH}")
            yolo_detector = None
        else:
            yolo_detector = YoloDetector(settings.YOLO_MODEL_PATH)
            logger.info("YOLOv8 model loaded successfully!")
        
        logger.info(f"Loading ArcFace model from {settings.ARCFACE_MODEL_PATH}...")
        if not os.path.exists(settings.ARCFACE_MODEL_PATH):
            logger.warning(f"  ArcFace model not found at {settings.ARCFACE_MODEL_PATH}")
            face_recognizer = None
        else:
            face_recognizer = FaceRecognizer(settings.ARCFACE_MODEL_PATH)
            logger.info("ArcFace model loaded successfully!")
        
        logger.info("Initializing Firebase...")
        if not os.path.exists(settings.FIREBASE_CREDENTIALS):
            logger.warning(f" Firebase credentials not found at {settings.FIREBASE_CREDENTIALS}")
            logger.warning("Firebase features will be disabled")
            firebase_service = None
        else:
            firebase_service = FirebaseService(settings.FIREBASE_CREDENTIALS)
            logger.info(" Firebase initialized successfully!")
        
        app.state.yolo_detector = yolo_detector
        app.state.face_recognizer = face_recognizer
        app.state.firebase_service = firebase_service
        app.state.ws_manager = ws_manager
        
        logger.info("All services initialized successfully!")
        
    except Exception as e:
        logger.error(f"❌ Startup error: {str(e)}", exc_info=True)
        logger.warning("⚠️  Server starting with limited functionality")
        # Set None values for missing services
        app.state.yolo_detector = None
        app.state.face_recognizer = None
        app.state.firebase_service = None
        app.state.ws_manager = ws_manager
    
    yield
    
    # Cleanup
    logger.info("Shutting down services...")


# Create FastAPI app
app = FastAPI(
    title="Smart Intrusion Detection API",
    description="Backend for ESP32-CAM intrusion detection with YOLOv8 and ArcFace",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(detect.router, prefix="/api", tags=["Detection"])
app.include_router(roi.router, prefix="/api", tags=["ROI"])
app.include_router(events.router, prefix="/api", tags=["Events"])


@app.get("/")
async def root():
    return {
        "status": "online",
        "service": "Smart Intrusion Detection Backend",
        "version": "1.0.0",
        "models": {
            "yolo": app.state.yolo_detector is not None,
            "arcface": app.state.face_recognizer is not None,
            "firebase": app.state.firebase_service is not None
        }
    }


@app.websocket("/ws/detections")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time detection streaming"""
    await app.state.ws_manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            logger.info(f"Received from client: {data}")
    except WebSocketDisconnect:
        app.state.ws_manager.disconnect(websocket)
        logger.info("Client disconnected from WebSocket")


if __name__ == "__main__":
    import uvicorn
    
    # Create necessary directories
    os.makedirs("logs", exist_ok=True)
    os.makedirs("models", exist_ok=True)
    
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )