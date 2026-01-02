from app.services.letter.pronounciation_service import PronounciationService
from app.services.letter.writing_service import WritingService


def get_pronounciation_service() -> PronounciationService:
    return PronounciationService()

def get_writing_service() -> WritingService:
    return WritingService()