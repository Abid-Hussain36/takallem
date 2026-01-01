from fastapi import APIRouter, UploadFile, File, Form, Depends
from app.models.letter.pronounciation import LetterPronounciationResponse, LetterPronounciationExplainInput, LetterPronounciationExplainResponse
from app.services.letter_service import PronounciationService
from app.utils.di import get_pronounciation_service


letter_router = APIRouter()


@letter_router.post("/pronounciation/check", response_model=LetterPronounciationResponse)
async def check_pronounciation(
    user_audio: UploadFile = File(...),
    word: str = Form(...),
    service: PronounciationService = Depends(get_pronounciation_service)
):
    """
        Takes in a user's recording of pronouncing a particular word and the word itself 
        and returns feedback on the user's attempt
    """
    return await service.check_pronounciation(user_audio, word)


@letter_router.post("/pronounciation/check-test")
async def check_pronounciation(
    user_audio: UploadFile = File(...),
    word: str = Form(...),
    service: PronounciationService = Depends(get_pronounciation_service)
):
    """
        Takes in a user's recording of pronouncing a particular word and the word itself 
        and returns feedback on the user's attempt
    """
    await service.check_pronounciation_test(user_audio, word)


@letter_router.get("/health-check")
def test_letter():
    return "Letter router running"