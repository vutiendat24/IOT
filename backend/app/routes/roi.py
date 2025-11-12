
from fastapi import APIRouter, Request, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
import logging

from app.utils.auth import verify_token

logger = logging.getLogger(__name__)
router = APIRouter()


class ROI(BaseModel):
    x: int
    y: int
    width: int
    height: int
    name: Optional[str] = "default"


class ROIResponse(BaseModel):
    roi_id: str
    user_id: str
    roi: ROI
    active: bool


@router.post("/roi", response_model=ROIResponse)
async def create_roi(
    request: Request,
    roi: ROI,
    user_id: str = Depends(verify_token)
):
    try:
        firebase_service = request.app.state.firebase_service
        
        roi_data = {
            "user_id": user_id,
            "x": roi.x,
            "y": roi.y,
            "width": roi.width,
            "height": roi.height,
            "name": roi.name,
            "active": True
        }
        
        roi_id = firebase_service.save_roi(roi_data)
        
        return ROIResponse(
            roi_id=roi_id,
            user_id=user_id,
            roi=roi,
            active=True
        )
    except Exception as e:
        logger.error(f"ROI creation error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/roi", response_model=List[ROIResponse])
async def get_rois(
    request: Request,
    user_id: str = Depends(verify_token)
):
    try:
        firebase_service = request.app.state.firebase_service
        rois = firebase_service.get_user_rois(user_id)
        
        return [
            ROIResponse(
                roi_id=roi_data['id'],
                user_id=user_id,
                roi=ROI(**{k: v for k, v in roi_data.items() if k in ['x', 'y', 'width', 'height', 'name']}),
                active=roi_data.get('active', True)
            )
            for roi_data in rois
        ]
    except Exception as e:
        logger.error(f"ROI retrieval error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/roi/{roi_id}")
async def delete_roi(
    request: Request,
    roi_id: str,
    user_id: str = Depends(verify_token)
):
    try:
        firebase_service = request.app.state.firebase_service
        firebase_service.delete_roi(roi_id, user_id)
        
        return {"status": "success", "roi_id": roi_id}
    except Exception as e:
        logger.error(f"ROI deletion error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))