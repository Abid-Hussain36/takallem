from fastapi import APIRouter, Depends
from app.models.voice_tutor.voice_tutor import VoiceTutorInput, VoiceTutorOutput, VoiceTutorQuestionOutput, VoiceTutorQuestionInput
from app.services.voice_tutor_service import VoiceTutorService
from app.utils.auth import get_current_user_email
from app.utils.di import get_voice_tutor_service


voice_tutor_router = APIRouter()


@voice_tutor_router.post("/generate-response", response_model=VoiceTutorOutput)
async def generate_response(
    input: VoiceTutorInput,
    email: str = Depends(get_current_user_email),
    service: VoiceTutorService = Depends(get_voice_tutor_service)
) -> VoiceTutorOutput:
    return await service.generate_response(input)


@voice_tutor_router.post("/speak_question", response_model=VoiceTutorQuestionOutput)
async def speak_question(
    input: VoiceTutorQuestionInput,
    email: str = Depends(get_current_user_email),
    service: VoiceTutorService = Depends(get_voice_tutor_service)
) -> VoiceTutorQuestionOutput:
    return await service.speak_question(input)
