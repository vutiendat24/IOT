

from fastapi import APIRouter, Request, HTTPException, Depends, Query
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import logging

from app.utils.auth import verify_token

logger = logging.getLogger(__name__)
router = APIRouter()


class EventResponse(BaseModel):
    event_id: str
    user_id: str
    timestamp: str
    detections: List[dict]
    image_url: Optional[str]
    alert: bool


@router.get("/events", response_model=List[EventResponse])
async def get_events(
    request: Request,
    user_id: str = Depends(verify_token),
    limit: int = Query(50, ge=1, le=100),
    alert_only: bool = Query(False)
):
  
    try:
        firebase_service = request.app.state.firebase_service
        
        events = firebase_service.get_events(
            user_id=user_id,
            limit=limit,
            alert_only=alert_only
        )
        
        return [
            EventResponse(
                event_id=event['id'],
                user_id=event['user_id'],
                timestamp=event['timestamp'],
                detections=event.get('detections', []),
                image_url=event.get('image_url'),
                alert=event.get('alert', False)
            )
            for event in events
        ]
    except Exception as e:
        logger.error(f"Event retrieval error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/events/{event_id}", response_model=EventResponse)
async def get_event(
    request: Request,
    event_id: str,
    user_id: str = Depends(verify_token)
):
    try:
        firebase_service = request.app.state.firebase_service
        event = firebase_service.get_event_by_id(event_id, user_id)
        
        if not event:
            raise HTTPException(status_code=404, detail="Event not found")
        
        return EventResponse(
            event_id=event['id'],
            user_id=event['user_id'],
            timestamp=event['timestamp'],
            detections=event.get('detections', []),
            image_url=event.get('image_url'),
            alert=event.get('alert', False)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Event retrieval error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))