from typing import List
from fastapi import HTTPException, status
from sqlalchemy import or_
from sqlalchemy.orm import Session
from app.db.schemas.module import Module
from app.models.db.general_resource.module_response import ModuleResponse
from app.db.enums import AvailableCourse, AvailableDialect


class ModuleService:
    def get_modules_by_course(self, db: Session, course: AvailableCourse) -> List[ModuleResponse]:
        """
        Gets all modules for a specified course, sorted by number
        """
        modules = db.query(Module).filter(
            Module.course == course,
            Module.dialect.is_(None)
        ).order_by(Module.number).all()
        
        return [module.to_model() for module in modules]


    def get_modules_by_course_and_dialect(self, db: Session, course: AvailableCourse, dialect: AvailableDialect) -> List[ModuleResponse]:
        """
        Gets all modules for a specified course and dialect, sorted by number
        """
        modules = db.query(Module).filter(
            Module.course == course,
            or_(
                Module.dialect == dialect,
                Module.dialect.is_(None)
            )
        ).order_by(Module.number).all()
        
        return [module.to_model() for module in modules]
