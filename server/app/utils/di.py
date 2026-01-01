from app.services.letter_service import PronounciationService


def get_pronounciation_service() -> PronounciationService:
    return PronounciationService()