from fastapi import FastAPI
from dotenv import load_dotenv

# This must run first because all the routers will use env variables!
load_dotenv()

from app.routers.letter import letter_router
from app.routers.vocab import vocab_router


app = FastAPI()

app.include_router(letter_router, prefix="/letter")
app.include_router(vocab_router, prefix="/vocab")

@app.get("/")
def health_check():
    return "App running"