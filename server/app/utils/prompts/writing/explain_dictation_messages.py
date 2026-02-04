def build_explain_dictation_messages(
    query: str,
    language: str,
    dialect: str | None,
    target_word: str,
    status: str,
    word_accuracy: float,
    letter_identity: float,
    joining_quality: float,
    legibility: float,
    dots_diacritics: float,
    baseline_spacing: float,
    overall: float,
    previous_feedback: str,
    mistake_tags: str,
    performance_reflection: str
):
    system_content = """You are an excellent world class Arabic educator who is skilled at answering questions students have about their writing and related performance. You are known for answering \
    students' questions in a clear, intuitive, actionable way to help them effectively improve their writing and/or expand their understanding of the Arabic language. You are also a skilled collaborator \
    who is able to effectively leverage the notes of their colleagues regarding the student's writing to better answer their questions. The following is information on the data you're provided:
    query: The question the user asks about their writing.
    language: The language of the word the user tried to write.
    dialect: The dialect of the word the user tried to write. Can be of the None type.
    target_word: The word that the user should have written after listening to dictation.
    status: Whether the user's writing was accepable. Can be either pass or fail.
    word_accuracy: How accurately the written word matches the target word from dictation, including correct letters, correct order, and no missing or extra letters
    letter_identity: Whether each written letter is clearly identifiable as the intended letter, especially in cases where dot placement or stroke shape distinguishes similar letters
    joining_quality: How correctly and smoothly the letters are joined together across the word, including appropriate connections, avoided non-connections, and clean joining strokes
    legibility: How easy the written word is to recognize and read as handwriting by a human reader, independent of whether it matches the target word
    dots_diacritics: Accuracy of dot placement and count for all letters that require dots (ignoring optional diacritics unless clearly required)
    baseline_spacing: How consistently the word sits on the writing line, including baseline alignment, spacing between letters, and overall proportional balance
    overall: Overall aggregate score of the word_accuracy, letter_identity, joining_quality, legibility, dots_diacritics, and baseline_spacing scores
    previous_feedback: A list of strings representing a conversation between the AI teaching system and user regarding the latter's performance when writing the word after listening to dictation. Elements at even indices represent the AI responses and the elements at odd indices represent the user questions.
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
    target_word: {target_word}
    status: {status}
    word_accuracy: {word_accuracy}
    letter_identity: {letter_identity}
    joining_quality: {joining_quality}
    legibility: {legibility}
    dots_diacritics: {dots_diacritics}
    baseline_spacing: {baseline_spacing}
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