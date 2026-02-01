from typing import List
from fastapi import APIRouter, Depends, File, Form, UploadFile
from app.models.ai.writing import DictationResponse, LetterJoiningResponse, LetterWritingResponse, WritingPhotoRetakeResponse
from app.services.writing_service import WritingService
from app.utils.di import get_writing_service
from app.utils.enums import LetterPosition


writing_router = APIRouter()


@writing_router.post("/writing/alphabet", response_model=LetterWritingResponse | WritingPhotoRetakeResponse)
async def check_letter_writing(
    user_image: UploadFile = File(...), 
    target_image: UploadFile = File(...), 
    letter: str = Form(...), 
    position: LetterPosition = Form(...),
    service: WritingService = Depends(get_writing_service)
):
    """Takes in an image of the user's letter writing and evaluates it."""
    return await service.check_letter_writing(user_image, target_image, letter, position)


@writing_router.post("/writing/joining", response_model=LetterJoiningResponse | WritingPhotoRetakeResponse)
async def check_letter_joining(
    user_image: UploadFile = File(...), 
    letter_list: List[str] = Form(...), 
    target_word: str = Form(...),
    service: WritingService = Depends(get_writing_service)
):
    """Takes in an image of the user's writing of joining letters and evaluates it."""
    return await service.check_letter_joining(user_image, letter_list, target_word)


@writing_router.post("/writing/dictation", response_model=DictationResponse | WritingPhotoRetakeResponse)
async def check_dictation(
    user_image: UploadFile = File(...),
    target_word: str = Form(...),
    service: WritingService = Depends(get_writing_service)
):
    """Takes in an image of the user's writing of a dictated word and evaluates it."""
    return await service.check_dictation(user_image, target_word)