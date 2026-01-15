from typing import List
from fastapi import HTTPException, status
from sqlalchemy.orm import Session, selectinload
from app.db.schemas.language import Language
from app.models.db.general_resource.language_response import LanguageResponse


class LanguageService:
    def get_all_languages(self, db: Session) -> List[LanguageResponse]:
        """Gets all language rows from the language table"""
        # Selectin load basically loads up the relational fields within Language in our DB response
        # This way, we dont need to use lazy loading to get the dialects and courses for each language one at a time
        # Much more efficient for getting and responding with relational fields
        languages = db.query(Language).options(
            selectinload(Language.dialects),
            selectinload(Language.courses)
        ).all()
        
        return [language.to_model() for language in languages]
