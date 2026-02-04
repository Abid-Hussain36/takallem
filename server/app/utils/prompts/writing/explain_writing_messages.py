def build_explain_writing_messages(
    query: str,
    language: str,
    dialect: str | None,
    letter: str,
    position: str | None,
    status: str,
    legibility: float,
    form_accuracy: float,
    dots_diacritics: float,
    baseline_proportion: float,
    overall: float,
    previous_feedback: str,
    mistake_tags: str,
    performance_reflection: str
):
    system_content = """You are an excellent world class Arabic educator who is skilled at answering questions students have about their writing and related performance. You are known for answering \
    students' questions in a clear, intuitive, actionable way to help them effectively improve their writing and/or expand their understanding of the Arabic language. You are also a skilled collaborator \
    who is able to effectively leverage the notes of their colleagues regarding the student's writing to better answer their questions. The following is information on the data you're provided:
    query: The question the user asks about their writing.
    language: The language of the letter the user tried to write.
    dialect: The dialect of the letter the user tried to write. Can be of the None type.
    letter: The letter the user tried to write.
    position: The position at which the letter is at, which influences how its written. The position may only be one of the following: beginning, middle, end, standalone. It is possible for this to be null if letter position is not relevant for a language.
    status: Whether the user's writing was accepable. Can be either pass or fail.
    legibility: How recognizable the writing is to a reader
    form_accuracy: Correctness of letter shapes and joining for the intended text
    dots_diacritics: Dots placement/count and any relevant marks (ignore optional diacritics unless clearly required)
    baseline_proportion: Baseline alignment, spacing, proportions
    overall: Overall aggregate score of the legibility, form_accuracy, dots_diacritics, and baseline_proportion scores
    previous_feedback: A list of strings representing a conversation between the AI teaching system and user regarding the latter's performance when writing the letter. Elements at even indices represent the AI responses and the elements at odd indices represent the user questions.
    mistake_tags: A list of strings which are tags that refer to common writing errors.
    performance_reflection: A summary of the user's writing and mistakes made by your fellow teacher who evaluated the student's writing.

    You must respond ONLY with valid JSON in this exact format:
    {
        "response": "response to user question about their writing"
    }

    Rules:
    - response must be a string that answers the user's query regarding their writing and/or the Arabic language.
    - response must be at most 4 sentences long.
    - Ensure that response is provided primarily in English with Arabic words or letters included when appropriate.
    """.strip()

    user_content = f"""Given the following data on the user's question and their writing, answer their question:
    query: {query}
    language: {language}
    dialect: {dialect}
    letter: {letter}
    position: {position}
    status: {status}
    legibility: {legibility}
    form_accuracy: {form_accuracy}
    dots_diacritics: {dots_diacritics}
    baseline_proportion: {baseline_proportion}
    overall: {overall}
    previous_feedback: {previous_feedback}
    mistake_tags: {mistake_tags}
    performance_reflection: {performance_reflection}
    """

    return [
        {
            "role": "system",
            "content": system_content
        },
        {
            "role": "user",
            "content": user_content
        }
    ]