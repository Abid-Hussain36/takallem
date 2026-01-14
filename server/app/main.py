from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from dotenv import load_dotenv

# This must run first because all the routers will use env variables!
load_dotenv()

from app.routers.letter import letter_router
from app.routers.vocab import vocab_router
from app.routers.auth import auth_router
from app.routers.user import user_router
from app.db.database import get_db


app = FastAPI()

app.include_router(letter_router, prefix="/letter")
app.include_router(vocab_router, prefix="/vocab")
app.include_router(auth_router, prefix="/auth")
app.include_router(user_router, prefix="/user")


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