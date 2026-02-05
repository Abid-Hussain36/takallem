from typing import List
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage


def build_semantic_eval_messages(
    language: str, 
    dialect: str | None, 
    question: str, 
    vocab_words: str, 
    transcription: str
) -> List[BaseMessage]:

    system = """You are an Arabic language tutor evaluating a student's spoken response. Your job is to analyze their answer and determine:
    1. Did they use any of the target vocabulary words?
    2. Does their answer make logical sense given the question?
    3. Is their Arabic grammar acceptable for a beginner?

    Be encouraging but honest in your evaluation. The following is information on the data you're provided:
    language: The language of the question and expected user response.
    dialect: The dialect of the question and expected user response. Can be of the None type.
    question: The question that the user is trying to answer with their response.
    vocab_words: The list of vocab words that are expected to be used to answer the question. Not all words need to be used however.
    transcription: The user's response to the question.


    IMPORTANT: You MUST respond with ONLY a JSON object in this exact format:
    {
        "vocab_words_used": ["list", "of", "words", "they", "used"],
        "answer_makes_sense": true,
        "grammatical_score": 85.0,
        "grammar_notes": "Comprehensive notes about their grammar",
    }

    Rules:
    - vocab_words_used is a list of the vocab words OUT OF THE vocab_words that the user used in their response.
    - answer_makes_sense: Whether the user's response is a sensible answer to the question asked.
    - grammatical_score: A score representing the grammatical accuracy of the student's response. The score MUST be between 0.0 and 100.0.
    - grammar_notes: Notes about the user's grammar, highlighting grammatical errors honestly and meticulously if present, but also briefly highlighting what grammatical things the user did correctly.
    """.strip()

    human = f"""Given the following data about the question asked and the user's response, evaluate the quality of their answer:
    language: {language}
    dialect: {dialect}
    question: {question}
    vocab_words: {vocab_words}
    transcription: {transcription}
    """

    return [
        SystemMessage(content=system),
        HumanMessage(content=human)
    ]