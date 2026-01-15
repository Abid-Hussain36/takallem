from typing import List
from fastapi import HTTPException, status
from sqlalchemy.orm import Session, selectinload
from app.db.schemas.module import Module
from app.models.db.general_resource.module_response import ModuleResponse
from app.db.enums import AvailableCourse


class ModuleService:
    def get_modules_by_course(self, db: Session, course: AvailableCourse) -> List[ModuleResponse]:
        """
        Gets all modules for a specified course, sorted by number with resources 
        and all nested relationships eagerly loaded using polymorphic loading
        """
        modules = db.query(Module).options(
            selectinload(Module.resource)
        ).filter(
            Module.course == course
        ).order_by(Module.number).all()
        
        # Access relationships to trigger lazy loading before serialization
        for module in modules:
            resource = module.resource
            # Access all possible relationships based on resource type
            # This triggers lazy loading for nested data
            for attr in ['vocab_words', 'problem_sets', 'problems', 'sequences', 
                        'dialects', 'letter_writing_sequences', 'content']:
                if hasattr(resource, attr):
                    try:
                        val = getattr(resource, attr)
                        # For collections with nested items, access those too
                        if isinstance(val, list):
                            for item in val:
                                # Access nested problems in problem sets
                                if hasattr(item, 'problems'):
                                    _ = item.problems
                    except:
                        pass
        
        return [module.to_model() for module in modules]
