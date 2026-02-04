from fastapi import APIRouter, Depends
from app.models.ai.speaking import VoiceTutorExplainInput, VoiceTutorExplainOutput, VoiceTutorInput, VoiceTutorOutput, VoiceTutorTTSInput, VoiceTutorTTSOutput
from app.services.speaking_service import SpeakingService
from app.utils.auth import get_current_user_email
from app.utils.di import get_speaking_service


speaking_router = APIRouter()


@speaking_router.post("/speak-question", response_model=VoiceTutorTTSOutput)
async def speak_question(
    input: VoiceTutorTTSInput,
    email: str = Depends(get_current_user_email),
    service: SpeakingService = Depends(get_speaking_service)
) -> VoiceTutorTTSOutput:
    """Generates a web playable audio file from TTS on the question text."""
    return await service.speak(input)


@speaking_router.post("/generate-response", response_model=VoiceTutorOutput)
async def generate_response(
    input: VoiceTutorInput,
    email: str = Depends(get_current_user_email),
    service: SpeakingService = Depends(get_speaking_service)
) -> VoiceTutorOutput:
    """Generates feedback on the user's speaking performance based on the question details."""
    return await service.generate_response(input)


@speaking_router.post("/explain", response_model=VoiceTutorExplainOutput)
async def explain_speaking(
    input: VoiceTutorExplainInput,
    email: str = Depends(get_current_user_email),
    service: SpeakingService = Depends(get_speaking_service)
) -> VoiceTutorExplainOutput:
    """Answers questions regarding user speaking performance based on previous evaluation."""
    return await service.explain_response(input)