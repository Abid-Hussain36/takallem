from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware  # Add this import
from sqlalchemy.orm import Session
from sqlalchemy import text
from dotenv import load_dotenv

# This must run first because all the routers will use env variables!
load_dotenv()

# Import all schemas to ensure they're registered with SQLAlchemy before any DB operations
# Import order matters: base classes first, then dependencies
from app.db.schemas.resource import Resource
from app.db.schemas.language import LanguageSchema
from app.db.schemas.dialect import DialectSchema
from app.db.schemas.course import CourseSchema
from app.db.schemas.module import Module
from app.db.schemas.user import User
from app.db.schemas.user_course_progress import UserCourseProgress

# Import dependent schemas first (those that other schemas reference)
from app.db.schemas.letter_writing_sequence import LetterWritingSequence
from app.db.schemas.vocab_word import VocabWord

# Import all resource subclasses
from app.db.schemas.info_lecture import InfoLecture
from app.db.schemas.letter_speaking_lecture import LetterSpeakingLecture
from app.db.schemas.letter_writing_lecture import LetterWritingLecture
from app.db.schemas.vocab_lecture import VocabLecture

# Problem sets and problems (import problems before problem sets)
from app.db.schemas.letter_pronounciation_problem import LetterPronounciationProblem
from app.db.schemas.word_pronounciation_problem import WordPronounciationProblem
from app.db.schemas.word_pronounciation_problem_set import WordPronounciationProblemSet
from app.db.schemas.letter_recognition_problem import LetterRecognitionProblem
from app.db.schemas.letter_recognition_problem_set import LetterRecognitionProblemSet
from app.db.schemas.letter_writing_problem import LetterWritingProblem
from app.db.schemas.letter_writing_problem_set import LetterWritingProblemSet
from app.db.schemas.letter_joining_problem import LetterJoiningProblem
from app.db.schemas.letter_joining_problem_set import LetterJoiningProblemSet
from app.db.schemas.dictation_problem import DictationProblem
from app.db.schemas.dictation_problem_set import DictationProblemSet
from app.db.schemas.discrimination_problem import DiscriminationProblem
from app.db.schemas.discrimination_problem_set import DiscriminationProblemSet

# Vocab problem sets (import in dependency order: problems -> sets -> collections)
from app.db.schemas.vocab_speaking_problem_word import vocab_speaking_problem_word
from app.db.schemas.vocab_reading_problem import VocabReadingProblem
from app.db.schemas.vocab_listening_problem import VocabListeningProblem
from app.db.schemas.vocab_speaking_problem import VocabSpeakingProblem
from app.db.schemas.vocab_reading_problem_set import VocabReadingProblemSet
from app.db.schemas.vocab_listening_problem_set import VocabListeningProblemSet
from app.db.schemas.vocab_speaking_problem_set import VocabSpeakingProblemSet
from app.db.schemas.vocab_reading_problem_sets import VocabReadingProblemSets
from app.db.schemas.vocab_listening_problem_sets import VocabListeningProblemSets
from app.db.schemas.vocab_speaking_problem_sets import VocabSpeakingProblemSets

# Reading comprehension (import text first, then problems, then problem sets)
from app.db.schemas.reading_comprehension_text import ReadingComprehensionText
from app.db.schemas.reading_comprehension_mcq_problem import ReadingComprehensionMCQProblem
from app.db.schemas.reading_comprehension_mcq_problem_set import ReadingComprehensionMCQProblemSet
from app.db.schemas.reading_comprehension_writing_problem import ReadingComprehensionWritingProblem
from app.db.schemas.reading_comprehension_writing_problem_set import ReadingComprehensionWritingProblemSet

# Dialect selection
from app.db.schemas.dialect_selection import DialectSelection
from app.db.schemas.dialect_selection_dialects import dialect_selection_dialects

from app.routers.auth import auth_router
from app.routers.user import user_router
from app.routers.user_course_progress import user_course_progress_router
from app.routers.module import module_router
from app.routers.resource import resource_router
from app.routers.language import language_router
from app.routers.pronounciation import pronounciation_router
from app.routers.speaking import speaking_router
from app.routers.writing import writing_router

from app.db.database import get_db


app = FastAPI()


# Creates a Middleware to allow CORS to accept requests from the client running locally.
# We only accept requests coming from these clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",      # Next.js dev server
        "http://127.0.0.1:3000",      # Alternative localhost
    ],
    allow_credentials=True,           # Allow usage of authentication headers
    allow_methods=["*"],              # Allow all HTTP methods
    allow_headers=["*"],              # Allow all headers
)

# Makes all the routes from the routers available.
app.include_router(auth_router, prefix="/auth")
app.include_router(user_router, prefix="/user")
app.include_router(user_course_progress_router, prefix="/user-course-progress")
app.include_router(module_router, prefix="/modules")
app.include_router(resource_router, prefix="/resource")
app.include_router(language_router, prefix="/languages")
app.include_router(pronounciation_router, "/pronounciation")
app.include_router(writing_router, prefix="/writing")
app.include_router(speaking_router, prefix="/speaking")


@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    """Health check for DB"""
    try:
        result = db.execute(text("SELECT 1")).scalar()
        
        return {
            "status": "healthy",
            "test_query_result": result
        }
        
    except Exception as e:
         return {
            "status": "unhealthy",
            "test_query_result": str(e)
        }