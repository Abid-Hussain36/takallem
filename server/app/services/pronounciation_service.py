from app.models.ai.pronounciation import LetterPronounciationResponse, LetterPronounciationExplainInput, LetterPronounciationExplainResponse, LetterWordPronounciationExplainInput, PronounciationExplainInput, PronounciationExplainResponse, PronounciationResponse
from fastapi import HTTPException, UploadFile, status
from pydub import AudioSegment
from app.utils.constants import PRONOUNCIATION_BASE_URL, AZURE_LANGUAGE_CODE
from app.utils.openai import openai_client
from app.db.enums import AvailableLanguage, AvailableDialect
import os, httpx, io, base64, json
from app.utils.prompts.pronounciation.check_pronounciation import build_check_pronounciation_messages
from app.utils.prompts.pronounciation.explain_pronounciation_messages import build_explain_pronounciation_messages


class PronounciationService():
    def _get_language_code(self, language: AvailableLanguage, dialect: AvailableDialect | None) -> str:
        """Get the Azure language code based on language and optional dialect."""
        language_mapping = AZURE_LANGUAGE_CODE.get(language)
        
        if language_mapping is None:
            raise ValueError(f"Unsupported language: {language}")
        
        # If the mapping is a dict (has dialects), get the dialect-specific code
        if isinstance(language_mapping, dict):
            if dialect and dialect in language_mapping:
                return language_mapping[dialect]
            raise ValueError(f"Unsupported {language} dialect: {dialect}")
        
        return language_mapping


    async def check_pronounciation(
        self,
        user_audio: UploadFile,
        phrase: str,
        isWord: bool,
        language: AvailableLanguage,
        dialect: AvailableDialect | None = None
    ) -> PronounciationResponse:
        """Takes in the user audio and letter to be pronounced and evaluates the performance."""
        # 1. Converting the user audio into WAV bytes
        raw_bytes = await user_audio.read()

        audio_bytes = AudioSegment.from_file(io.BytesIO(raw_bytes))
        audio = audio_bytes.set_frame_rate(16000).set_channels(1)

        wav_buffer = io.BytesIO()
        audio.export(wav_buffer, format="wav")
        wav_bytes = wav_buffer.getvalue()

        # 2. Setting up the Azure Pronounciation Assessment request
        if isWord:
            granularity = "Word"
        else:
            granularity = "Phoneme"

        pronounciation_config = {
            "ReferenceText": phrase,
            "GradingSystem": "HundredMark",
            "Granularity": granularity,
            "Dimension": "Comprehensive",
        }

        # Creates a base64 object out of the config object
        pronounciation_config_json = json.dumps(pronounciation_config).encode("utf-8") # Converts config object to JSON string
        pronounciation_config_base64 = base64.b64encode(pronounciation_config_json).decode() # Converts JSON string to base64 string
        
        AZURE_SUBSCRIPTION_KEY = os.getenv("AZURE_SUBSCRIPTION_KEY")
        if not AZURE_SUBSCRIPTION_KEY:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid Azure subscription key."
            )

        headers = {
            "Ocp-Apim-Subscription-Key": AZURE_SUBSCRIPTION_KEY,
            "Pronunciation-Assessment": pronounciation_config_base64,
            "Content-type": "audio/wav; codecs=audio/pcm; samplerate=16000",
        }

        # Get the appropriate language code based on user's language and dialect
        language_code = self._get_language_code(language, dialect)
        azure_speech_url = f"{PRONOUNCIATION_BASE_URL}?language={language_code}&format=detailed"
        
        # 3. Scoring the user's pronounciation of the letter
        try:
            async with httpx.AsyncClient() as client:
                pronounciation_response = await client.post(
                    azure_speech_url,
                    headers=headers,
                    content=wav_bytes,
                    timeout=30.0
                )

                pronounciation_response.raise_for_status() # If there is a 400 or 500 response, we raise an HTTPStatusError
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to make pronounciation assessment request to Azure"
            )

        # 4. Parsing pronounciation scoring response and determining status
        pronounciation_response_json = pronounciation_response.json()
        nbest = pronounciation_response_json.get("NBest") or []
        scores = nbest[0] if nbest else {}
        transcription = scores.get("Lexical", "")
        accuracy = scores.get("AccuracyScore", 0.0)
        completeness = scores.get("CompletenessScore", 0.0)
        overall_score = scores.get("PronScore", 0.0)
        
        status = "fail"

        if(
            overall_score >= 88
            and accuracy >= 85
            and completeness >= 95
        ):
            status = "pass"
        
        # 5. Generating pronounciation feedback with OpenAI API and parsing response
        pronounciation_messages = build_check_pronounciation_messages(phrase, transcription, accuracy, completeness, overall_score, status)

        try:
            chat_response = await openai_client.chat.completions.create(
                model=os.getenv("PRIMARY_MODEL") or "gpt-5.2-chat-latest",
                messages=pronounciation_messages,
                response_format={"type": "json_object"},
            )

            chat_response_content = chat_response.choices[0].message.content
            chat_response_obj = json.loads(chat_response_content)
            pronounciation_check_response = LetterPronounciationResponse(
                status=status,
                transcription=transcription,
                feedback=chat_response_obj["feedback"],
                mistake_tags=chat_response_obj["mistake_tags"],
                performance_reflection=chat_response_obj["performance_reflection"],
            )

            return pronounciation_check_response
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error in fetching or parsing pronounciation chat response: {e}"
            )


    async def explain_pronounciation(self, input: PronounciationExplainInput) -> PronounciationExplainResponse:
        query = input.query
        phrase = input.phrase
        status = input.status
        transcription = input.transcription
        previous_feedback = str(input.previous_feedback)
        mistake_tags_string = str(input.mistake_tags)
        performance_reflection = input.performance_reflection

        explain_messages = build_explain_pronounciation_messages(query, phrase, status, transcription, previous_feedback, mistake_tags_string, performance_reflection)

        try:
            chat_response = await openai_client.chat.completions.create(
                model=os.getenv("PRIMARY_MODEL") or "gpt-5.2-chat-latest",
                messages=explain_messages,
                response_format={"type": "json_object"},
            )

            chat_response_content = chat_response.choices[0].message.content
            chat_response_obj = json.loads(chat_response_content)
            explain_response = LetterPronounciationExplainResponse(
                feedback=chat_response_obj["feedback"]
            )

            return explain_response
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error in fetching or parsing pronounciation explanation chat response: {e}"
            )