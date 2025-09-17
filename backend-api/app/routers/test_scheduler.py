from fastapi import APIRouter
from ..scheduler_service import scheduler_service

router = APIRouter()

@router.get("/test/scheduler/status")
async def test_scheduler_status():
    """Test scheduler status without authentication"""
    try:
        status = scheduler_service.get_scheduler_status()
        return {"success": True, "status": status}
    except Exception as e:
        return {"success": False, "error": str(e)}
