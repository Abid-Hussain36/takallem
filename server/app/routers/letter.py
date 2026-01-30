from typing import Union, List, Optional
from fastapi import APIRouter, UploadFile, File, Form, Depends
from app.models.letter.pronounciation import LetterPronounciationExplainInput, LetterPronounciationResponse, LetterWordPronounciationExplainInput, LetterPronounciationExplainResponse
from app.services.letter.pronounciation_service import PronounciationService
from app.utils.di import get_pronounciation_service, get_writing_service
from app.models.letter.writing import DictationResponse, LetterJoiningResponse, LetterWritingResponse, WritingPhotoRetakeResponse
from app.services.letter.writing_service import LetterWritingService
from app.utils.enums import LetterPosition
from app.db.enums import AvailableLanguage, AvailableDialect


letter_router = APIRouter()


@letter_router.post("/pronounciation/letter/check", response_model=LetterPronounciationResponse)
async def check_letter_pronounciation(
    user_audio: UploadFile = File(...),
    letter: str = Form(...),
    language: AvailableLanguage = Form(...),
    dialect: Optional[AvailableDialect] = Form(None),
    service: PronounciationService = Depends(get_pronounciation_service)
):
    return await service.check_letter_pronounciation(user_audio, letter, language, dialect)


@letter_router.post("/pronounciation/word/check", response_model=LetterPronounciationResponse)
async def check_word_pronounciation(
    user_audio: UploadFile = File(...),
    word: str = Form(...),
    language: AvailableLanguage = Form(...),
    dialect: Optional[AvailableDialect] = Form(None),
    service: PronounciationService = Depends(get_pronounciation_service)
):
    """
        Takes in a user's recording of pronouncing a particular word and the word itself 
        and returns feedback on the user's attempt.
    """
    return await service.check_word_pronounciation(user_audio, word, language, dialect)


@letter_router.post("/pronounciation/letter/explain", response_model=LetterPronounciationExplainResponse)
async def explain_letter_pronounciation(input: LetterPronounciationExplainInput, service: PronounciationService = Depends(get_pronounciation_service)):
    """
        Takes in a reflection on the user's pronounciation and a user query and answers the query based on the reflection.
    """
    return await service.explain_letter_pronounciation(input)


@letter_router.post("/pronounciation/word/explain", response_model=LetterPronounciationExplainResponse)
async def explain_word_pronounciation(input: LetterWordPronounciationExplainInput, service: PronounciationService = Depends(get_pronounciation_service)):
    """
        Takes in a reflection on the user's pronounciation and a user query and answers the query based on the reflection.
    """
    return await service.explain_word_pronounciation(input)


@letter_router.post("/writing/alphabet", response_model=Union[LetterWritingResponse, WritingPhotoRetakeResponse])
async def check_letter_writing(
    user_image: UploadFile = File(...), 
    target_image: UploadFile = File(...), 
    letter: str = Form(...), 
    position: LetterPosition = Form(...),
    service: LetterWritingService = Depends(get_writing_service)
):
    """Takes in an image of the user's writing of a letter and evaluates it."""
    return await service.check_letter_writing(user_image, target_image, letter, position)


@letter_router.post("/writing/joining", response_model=Union[LetterJoiningResponse, WritingPhotoRetakeResponse])
async def check_letter_joining(
    user_image: UploadFile = File(...), 
    letter_list: List[str] = Form(...), 
    target_word: str = Form(...),
    service: LetterWritingService = Depends(get_writing_service)
):
    """Takes in an image of the user writing the joining of letters and evaluates it."""
    return await service.check_letter_joining(user_image, letter_list, target_word)


@letter_router.post("/writing/dictation", response_model=Union[DictationResponse, WritingPhotoRetakeResponse])
async def check_dictation(
    user_image: UploadFile = File(...),
    target_word: str = Form(...),
    service: LetterWritingService = Depends(get_writing_service)
):
    """Takes in an image of the user's writing of a dictated word and evaluates it."""
    return await service.check_dictation(user_image, target_word)