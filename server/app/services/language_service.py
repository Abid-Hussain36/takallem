from typing import List
from fastapi import HTTPException, status
from sqlalchemy.orm import Session, selectinload
from app.db.schemas.language import LanguageSchema
from app.models.db.general_resource.language_response import LanguageResponse


class LanguageService:
    def get_all_languages(self, db: Session) -> List[LanguageResponse]:
        """Gets all language rows from the language table"""
        # Selectin load basically loads up the relational fields within LanguageSchema in our DB response all at once
        # This way, we dont need to use lazy loading to get the dialects and courses for each language one at a time
        # Much more efficient for getting and responding with relational fields and avoids N + 1 problem
        languages = db.query(LanguageSchema).options(
            selectinload(LanguageSchema.dialects),
            selectinload(LanguageSchema.courses)
        ).all()
        
        return [language.to_model() for language in languages]
