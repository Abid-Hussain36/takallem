from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.models.db.general_resource.language_response import LanguageResponse
from app.db.database import get_db
from app.services.language_service import LanguageService
from app.utils.di import get_language_service


language_router = APIRouter()


@language_router.get("/", response_model=List[LanguageResponse])
def get_all_languages(
    db: Session = Depends(get_db),
    service: LanguageService = Depends(get_language_service)
) -> List[LanguageResponse]:
    """Gets all language rows from the language table"""
    return service.get_all_languages(db)
