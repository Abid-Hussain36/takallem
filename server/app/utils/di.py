from app.services.letter.pronounciation_service import PronounciationService
from app.services.letter.writing_service import LetterWritingService
from app.services.user_service import UserService
from app.services.auth_service import AuthService


def get_pronounciation_service() -> PronounciationService:
    return PronounciationService()


def get_writing_service() -> LetterWritingService:
    return LetterWritingService()


def get_user_service() -> UserService:
    return UserService()


def get_auth_service() -> AuthService:
    return AuthService()