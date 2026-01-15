from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.models.db.general_resource.module_response import ModuleResponse
from app.db.database import get_db
from app.services.module_service import ModuleService
from app.utils.di import get_module_service
from app.db.enums import AvailableCourse


module_router = APIRouter()


@module_router.get("/{course}", response_model=List[ModuleResponse])
def get_modules_by_course(
    course: AvailableCourse,
    db: Session = Depends(get_db),
    service: ModuleService = Depends(get_module_service)
) -> List[ModuleResponse]:
    """Gets all modules for the specified course, sorted by number"""
    return service.get_modules_by_course(db, course)
