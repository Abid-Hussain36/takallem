from fastapi import APIRouter, UploadFile, File, Form, Depends
from app.models.ai.pronounciation import PronounciationResponse, PronounciationExplainInput, PronounciationExplainResponse
from app.services.pronounciation_service import PronounciationService
from app.utils.di import get_pronounciation_service
from app.db.enums import AvailableLanguage, AvailableDialect


pronounciation_router = APIRouter()


@pronounciation_router.post("/check", response_model=PronounciationResponse)
async def check_pronounciation(
    user_audio: UploadFile = File(...), # This is required form field
    phrase: str = Form(...),
    isWord: bool = Form(...),
    language: AvailableLanguage = Form(...),
    dialect: AvailableDialect | None = Form(None), # This is nullable form field
    service: PronounciationService = Depends(get_pronounciation_service)
) -> PronounciationResponse:
    """Take in a user's pronounciation recording and return its evaluation."""
    return await service.check_pronounciation(user_audio, phrase, isWord, language, dialect)


@pronounciation_router.post("/explain", response_model=PronounciationExplainResponse)
async def explain_pronounciation(
    input: PronounciationExplainInput, 
    service: PronounciationService = Depends(get_pronounciation_service)
) -> PronounciationExplainResponse:
    """Takes in a reflection of the user's pronounciation and past questions to generate a response for their query."""
    return await service.explain_pronounciation(input)