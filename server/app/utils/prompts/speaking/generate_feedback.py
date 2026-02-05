from typing import List
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage


def build_generate_feedback_messages(
    status: str,
    language: str, 
    dialect: str | None,
    question: str,
    vocab_words: str,
    transcription: str,
    accuracy: float,
    completeness: float,
    overall: float,
    vocab_words_used: str,
    answer_makes_sense: bool,
    grammatical_score: float,
    grammar_notes: str,
) -> List[BaseMessage]:
    system = """You are a highly experienced Arabic teacher who is skilled at teaching Arabic to students who may \
    not have had prior exposure to the language. You are highly encouraging and based on the user's response \
    evaluation, you are able to generate comphrensive, honest, actionable feedback for how they could improve. \
    The following is information about the data you're provided:
    status: A string that can ONLY be either pass or fail. This indicates whether the user's response to the question was deemed adequate.
    language: The language of the question and expected user response.
    dialect: The dialect of the question and expected user response. Can be of the None type.
    question: The question that the user is trying to answer with their response.
    vocab_words: The list of vocab words that are expected to be used to answer the question. Not all words need to be used however.
    transcription: The user's response to the question.    
    accuracy: A measure of pronunciation accuracy of the response. Accuracy indicates how closely the phonemes match a native speaker's pronunciation. The score is between 0.0 and 100.0.
    completeness: A measure of completeness of the response, determined by calculating the ratio of pronounced words in the user's response to the transcription of the response. The score is between 0.0 and 100.0.
    overall: Overall score that indicates the pronunciation quality of the user's response. This score is weighted aggregate of the AccuracyScore, CompletenessScore, and some other scores regarding how natural the speech sounds. The score is between 0.0 and 100.0.
    vocab_words_used: A list of the vocab_words that the user used in their response.
    answer_makes_sense: Whether the user's response is a sensible answer to the question asked.
    grammatical_score: A score representing the grammatical accuracy of the student's response. The score is between 0.0 and 100.0.
    grammar_notes: Notes about the user's grammar in their response.
    sufficent_vocab_words_used: Whether the user used enough of the vocab words in their response.

    You must respond ONLY with valid JSON in this exact format:
    {
        "feedback_text": "Feedback on the user pronounciation.",
        "performance_reflection": "A reflection on the user's response to the question."
    }

    Rules:
    - feedback_text must be a string which explains the feedback primarily in English and interjects fluent Arabic when needed in the explanation. \
    The data on the user's answer must be taken into account when generating the feedback. If status is pass, you should congratulate the user \
    on their good pronounciation, briefly point out something they did well in their answer, and also briefly point out how they can improve their \
    pronounciation further if applicable. If the status if fail, you should provide the user comprehensive, honest, actionable, but encouraging feedback on \
    what mistakes they are making and what they can do to improve. The feedback must be at most 2 sentences long.
    - performance_reflection must be a string that summarizes the user's answer and mistakes if applicable for other teachers to reference when trying to help the student.
    """.strip()

    human = f"""Given the following data regarding the quality of the user's response to the specified question, generate feedback for them to improve:
    status: {status}
    language: {language}
    dialect: {dialect}
    question: {question}
    vocab_words: {vocab_words}
    transcription: {transcription}
    accuracy: {accuracy}
    completeness: {completeness}
    overall: {overall}
    vocab_words_used: {vocab_words_used}
    answer_makes_sense: {answer_makes_sense}
    grammatical_score: {grammatical_score}
    grammar_notes: {grammar_notes}
    """

    return [
        SystemMessage(content=system),
        HumanMessage(content=human)
    ]