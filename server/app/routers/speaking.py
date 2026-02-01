from fastapi import APIRouter, Depends
from app.models.ai.speaking import VoiceTutorInput, VoiceTutorOutput, VoiceTutorQuestionOutput, VoiceTutorQuestionInput
from app.services.speaking_service import SpeakingService, VoiceTutorService
from app.utils.auth import get_current_user_email
from app.utils.di import get_speaking_service


speaking_router = APIRouter()


@speaking_router.post("/generate-response", response_model=VoiceTutorOutput)
async def generate_response(
    input: VoiceTutorInput,
    email: str = Depends(get_current_user_email),
    service: SpeakingService = Depends(get_speaking_service)
) -> VoiceTutorOutput:
    return await service.generate_response(input)


@speaking_router.post("/speak-question", response_model=VoiceTutorQuestionOutput)
async def speak_question(
    input: VoiceTutorQuestionInput,
    email: str = Depends(get_current_user_email),
    service: SpeakingService = Depends(get_speaking_service)
) -> VoiceTutorQuestionOutput:
    return await service.speak_question(input)
