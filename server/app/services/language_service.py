from typing import List
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.db.schemas.language import Language
from app.models.db.general_resource.language_response import LanguageResponse


class LanguageService:
    def get_all_languages(self, db: Session) -> List[LanguageResponse]:
        """Gets all language rows from the language table"""
        languages = db.query(Language).all()
        
        return [language.to_model() for language in languages]
