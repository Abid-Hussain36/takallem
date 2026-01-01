from fastapi import APIRouter


vocab_router = APIRouter()


@vocab_router.get("/health-check")
def test_vocab():
    return "Vocab router running"