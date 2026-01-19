from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.models.db.general_resource.module_response import ModuleResponse
from app.db.database import get_db
from app.services.module_service import ModuleService
from app.utils.di import get_module_service
from app.db.enums import AvailableCourse, AvailableDialect
from app.utils.auth import get_current_user_email


module_router = APIRouter()


@module_router.get("/{course}", response_model=List[ModuleResponse])
def get_modules_by_course(
    course: AvailableCourse,
    email: str = Depends(get_current_user_email),
    db: Session = Depends(get_db),
    service: ModuleService = Depends(get_module_service)
) -> List[ModuleResponse]:
    """Gets all modules for the specified course, sorted by number"""
    return service.get_modules_by_course(db, course)


@module_router.get("/{course}/{dialect}", response_model=List[ModuleResponse])
def get_modules_by_course_and_dialect(
    course: AvailableCourse,
    dialect: AvailableDialect,
    email: str = Depends(get_current_user_email),
    db: Session = Depends(get_db),
    service: ModuleService = Depends(get_module_service)
) -> List[ModuleResponse]:
    """Gets all modules for the specified course, sorted by number"""
    return service.get_modules_by_course_and_dialect(db, course, dialect)
