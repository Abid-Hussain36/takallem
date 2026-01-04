from app.services.letter.pronounciation_service import PronounciationService
from app.services.letter.writing_service import LetterWritingService


def get_pronounciation_service() -> PronounciationService:
    return PronounciationService()

def get_writing_service() -> LetterWritingService:
    return LetterWritingService()