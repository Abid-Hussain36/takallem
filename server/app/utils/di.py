from app.services.auth_service import AuthService
from app.services.user_service import UserService
from app.services.user_course_progress_service import UserCourseProgressService
from app.services.module_service import ModuleService
from app.services.language_service import LanguageService
from app.services.letter.pronounciation_service import PronounciationService
from app.services.letter.writing_service import LetterWritingService


# Defines functions we use to build the objects for injection.
def get_auth_service() -> AuthService:
    return AuthService()


def get_user_service() -> UserService:
    return UserService()


def get_user_course_progress_service() -> UserCourseProgressService:
    return UserCourseProgressService()


def get_module_service() -> ModuleService:
    return ModuleService()


def get_language_service() -> LanguageService:
    return LanguageService()


def get_pronounciation_service() -> PronounciationService:
    return PronounciationService()


def get_writing_service() -> LetterWritingService:
    return LetterWritingService()
