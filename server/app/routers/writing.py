from typing import List
from fastapi import APIRouter, Depends, File, Form, UploadFile
from app.models.ai.writing import DictationExplainInput, DictationResponse, JoiningExplainInput, LetterJoiningResponse, LetterWritingResponse, WritingExplainInput, WritingExplainResponse, WritingPhotoRetakeResponse
from app.services.writing_service import WritingService
from app.utils.di import get_writing_service
from app.utils.enums import LetterPosition
from app.db.enums import AvailableDialect, AvailableLanguage


writing_router = APIRouter()


@writing_router.post("/letter", response_model=LetterWritingResponse | WritingPhotoRetakeResponse)
async def check_letter_writing(
    user_image: UploadFile = File(...), 
    target_image: UploadFile = File(...), 
    letter: str = Form(...), 
    language: AvailableLanguage = Form(...),
    dialect: AvailableDialect | None = Form(None),
    position: LetterPosition | None = Form(None),
    service: WritingService = Depends(get_writing_service)
):
    """Takes in an image of the user's letter writing and evaluates it."""
    return await service.check_letter_writing(user_image, target_image, letter, language, dialect, position)


@writing_router.post("/joining", response_model=LetterJoiningResponse | WritingPhotoRetakeResponse)
async def check_letter_joining(
    user_image: UploadFile = File(...), 
    letter_list: List[str] = Form(...), 
    target_word: str = Form(...),
    language: AvailableLanguage = Form(...),
    dialect: AvailableDialect | None = Form(None),
    service: WritingService = Depends(get_writing_service)
):
    """Takes in an image of the user's writing of joining letters and evaluates it."""
    return await service.check_letter_joining(user_image, letter_list, target_word, language, dialect)


@writing_router.post("/dictation", response_model=DictationResponse | WritingPhotoRetakeResponse)
async def check_dictation(
    user_image: UploadFile = File(...),
    target_word: str = Form(...),
    language: AvailableLanguage = Form(...),
    dialect: AvailableDialect | None = Form(None),
    service: WritingService = Depends(get_writing_service)
):
    """Takes in an image of the user's writing of a dictated word and evaluates it."""
    return await service.check_dictation(user_image, target_word, language, dialect)


@writing_router.post("/letter/explain", response_model=WritingExplainResponse)
async def explain_writing(
    input: WritingExplainInput,
    service: WritingService = Depends(get_writing_service)
) -> WritingExplainResponse:
    """Takes in a reflection on the user's letter writing performance and user question and returns a response."""
    return await service.explain_writing(input)


@writing_router.post("/joining/explain", response_model=WritingExplainResponse)
async def explain_joining(
    input: JoiningExplainInput,
    service: WritingService = Depends(get_writing_service)
) -> WritingExplainResponse:
    """Takes in a reflection on the user's letter joining performance and user question and returns a response."""
    return await service.explain_joining(input)


@writing_router.post("/dictation/explain", response_model=WritingExplainResponse)
async def explain_dictation(
    input: DictationExplainInput,
    service: WritingService = Depends(get_writing_service)
) -> WritingExplainResponse:
    """Takes in a reflection on the user's dictation performance and user question and returns a response."""
    return await service.explain_dictation(input)