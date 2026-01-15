from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware  # Add this import
from sqlalchemy.orm import Session
from sqlalchemy import text
from dotenv import load_dotenv

# This must run first because all the routers will use env variables!
load_dotenv()

from app.routers.letter import letter_router
from app.routers.vocab import vocab_router
from app.routers.auth import auth_router
from app.routers.user import user_router
from app.routers.user_course_progress import user_course_progress_router
from app.routers.module import module_router
from app.routers.language import language_router
from app.db.database import get_db


app = FastAPI()

# Creates a Middleware to allow CORS to accept requests from the client running locally.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",      # Next.js dev server
        "http://127.0.0.1:3000",      # Alternative localhost
    ],
    allow_credentials=True,
    allow_methods=["*"],              # Allow all HTTP methods
    allow_headers=["*"],              # Allow all headers
)

# Makes all the routes from the routers available.
app.include_router(letter_router, prefix="/letter")
app.include_router(vocab_router, prefix="/vocab")
app.include_router(auth_router, prefix="/auth")
app.include_router(user_router, prefix="/user")
app.include_router(user_course_progress_router, prefix="/user-course-progress")
app.include_router(module_router, prefix="/modules")
app.include_router(language_router, prefix="/languages")


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