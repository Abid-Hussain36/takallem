from app.models.letter.pronounciation import LetterPronounciationResponse, LetterPronounciationExplainInput, LetterPronounciationExplainResponse, LetterWordPronounciationExplainInput
from fastapi import UploadFile
from pydub import AudioSegment
from app.utils.constants import PRONOUNCIATION_BASE_URL, MSA
from app.utils.prompts.pronounciation.check_word_pronounciation import build_check_word_pronounciation_messages
from app.utils.openai import openai_client
import os, httpx, io, base64, json
from app.utils.prompts.pronounciation.check_letter_pronounciation import build_check_letter_pronounciation_messages
from app.utils.prompts.pronounciation.explain_letter_pronounciation_messages import build_explain_letter_pronounciation_messages
from app.utils.prompts.pronounciation.explain_word_pronounciation import build_explain_word_pronounciation_messages


class PronounciationService():
    async def check_letter_pronounciation(
        self,
        user_audio: UploadFile,
        letter: str
    ) -> LetterPronounciationResponse:
        # Gets the bytes of the audio file
        raw_bytes = await user_audio.read()
        print("Got file")

        # Converts the audio bytes into wav bytes
        audio_bytes = AudioSegment.from_file(io.BytesIO(raw_bytes))
        audio = audio_bytes.set_frame_rate(16000).set_channels(1)
        wav_buffer = io.BytesIO()
        audio.export(wav_buffer, format="wav")
        wav_bytes = wav_buffer.getvalue()
        print("Converted file to WAV")

        pronounciation_config = {
            "ReferenceText": letter,
            "GradingSystem": "HundredMark",
            "Granularity": "Phoneme",
            "Dimension": "Comprehensive",
        }

        # Creates a base64 object out of the config object
        pronounciation_config_json = json.dumps(pronounciation_config).encode("utf-8")
        pronounciation_config_base64 = base64.b64encode(pronounciation_config_json).decode()

        AZURE_SUBSCRIPTION_KEY = os.getenv("AZURE_SUBSCRIPTION_KEY")
        if not AZURE_SUBSCRIPTION_KEY:
            raise ValueError("AZURE_SUBSCRIPTION_KEY environment variable is not set")

        headers = {
            "Ocp-Apim-Subscription-Key": AZURE_SUBSCRIPTION_KEY,
            "Pronunciation-Assessment": pronounciation_config_base64,
            "Content-type": "audio/wav; codecs=audio/pcm; samplerate=16000",
        }

        azure_speech_url = f"{PRONOUNCIATION_BASE_URL}?language={MSA}&format=detailed"
        
        # Scores the user's pronounciation of the letter
        try:
            async with httpx.AsyncClient() as client:
                print(f"Headers: {headers}")
                pronounciation_response = await client.post(
                    azure_speech_url,
                    headers=headers,
                    content=wav_bytes,
                    timeout=30.0
                )
                print("Made Azure API request")
                print(f"Status: {pronounciation_response.status_code}")
                print(f"Headers: {pronounciation_response.headers}")
                print(f"Body: {pronounciation_response.text}")

            pronounciation_response.raise_for_status()
        except httpx.HTTPStatusError as e:
            print(f"Azure API error: {e.response.status_code} - {e.response.text}")
            return LetterPronounciationResponse(
                status="fail",
                transcription="",
                feedback="Unable to process pronunciation at this time. Please try again.",
                mistake_tags=["SYSTEM_ERROR"],
                performance_reflection="API request failed"
            )
        except Exception as e:
            print(f"Unexpected error during Azure API call: {e}")
            return LetterPronounciationResponse(
                status="fail",
                transcription="",
                feedback="An unexpected error occurred. Please try again.",
                mistake_tags=["SYSTEM_ERROR"],
                performance_reflection="Unexpected error during pronunciation assessment"
            )

        pronounciation_response_json = pronounciation_response.json()
        nbest = pronounciation_response_json.get("NBest") or []
        scores = nbest[0] if nbest else {}
        transcription = scores.get("Lexical", "")
        accuracy = scores.get("AccuracyScore", 0.0)
        completeness = scores.get("CompletenessScore", 0.0)
        overall_score = scores.get("PronScore", 0.0)
        status = "fail"
        print("Got pronounciation score data")
        print(pronounciation_response_json)

        # Provides a threshold for acceptable pronounciation
        if(
            overall_score >= 88
            and accuracy >= 85
            and completeness >= 95
        ):
            status = "pass"
        else:
            status = "fail"

        pronounciation_messages = build_check_letter_pronounciation_messages(letter, transcription, accuracy, completeness, overall_score, status)

        # Generates feedback for the student based on the scores
        chat_response = await openai_client.chat.completions.create(
            model=os.getenv("LETTER_PRONOUNCIATION_MODEL") or "gpt-5.1-chat-latest",
            messages=pronounciation_messages,
            response_format={"type": "json_object"},
        )
        print("Made chat request")
        print(chat_response)

        # Initialize with default error response
        pronounciation_check_response = LetterPronounciationResponse(
            status=status,
            transcription=transcription,
            feedback="An error occurred while processing your pronunciation feedback. Please try again.",
            mistake_tags=[],
            performance_reflection=""
        )

        try:
            chat_response_content = chat_response.choices[0].message.content
            chat_response_obj = json.loads(chat_response_content)
            pronounciation_check_response = LetterPronounciationResponse(
                status=status,
                transcription=transcription,
                feedback=chat_response_obj["feedback"],
                mistake_tags=chat_response_obj["mistake_tags"],
                performance_reflection=chat_response_obj["performance_reflection"],
            )
            print("Parsed chat output")
            print(pronounciation_check_response)
        except Exception as e:
            print(f"Error parsing pronounciation chat response: {e}")
        
        return pronounciation_check_response


    async def check_word_pronounciation(
        self,
        user_audio: UploadFile,
        word: str
    ) -> LetterPronounciationResponse:
        # Gets the bytes of the audio file
        raw_bytes = await user_audio.read()
        print("Got file")

        # Converts the audio bytes into wav bytes
        audio_bytes = AudioSegment.from_file(io.BytesIO(raw_bytes))
        audio = audio_bytes.set_frame_rate(16000).set_channels(1)
        wav_buffer = io.BytesIO()
        audio.export(wav_buffer, format="wav")
        wav_bytes = wav_buffer.getvalue()
        print("Converted file to WAV")

        pronounciation_config = {
            "ReferenceText": word,
            "GradingSystem": "HundredMark",
            "Granularity": "Word",
            "Dimension": "Comprehensive",
        }

        # Creates a base64 object out of the config object
        pronounciation_config_json = json.dumps(pronounciation_config).encode("utf-8")
        pronounciation_config_base64 = base64.b64encode(pronounciation_config_json).decode()

        AZURE_SUBSCRIPTION_KEY = os.getenv("AZURE_SUBSCRIPTION_KEY")
        if not AZURE_SUBSCRIPTION_KEY:
            raise ValueError("AZURE_SUBSCRIPTION_KEY environment variable is not set")

        headers = {
            "Ocp-Apim-Subscription-Key": AZURE_SUBSCRIPTION_KEY,
            "Pronunciation-Assessment": pronounciation_config_base64,
            "Content-type": "audio/wav; codecs=audio/pcm; samplerate=16000",
        }

        azure_speech_url = f"{PRONOUNCIATION_BASE_URL}?language={MSA}&format=detailed"
        
        # Scores the user's pronounciation of the word
        try:
            async with httpx.AsyncClient() as client:
                print(f"Headers: {headers}")
                pronounciation_response = await client.post(
                    azure_speech_url,
                    headers=headers,
                    content=wav_bytes,
                    timeout=30.0
                )
                print("Made Azure API request")
                print(f"Status: {pronounciation_response.status_code}")
                print(f"Headers: {pronounciation_response.headers}")
                print(f"Body: {pronounciation_response.text}")

            pronounciation_response.raise_for_status()
        except httpx.HTTPStatusError as e:
            print(f"Azure API error: {e.response.status_code} - {e.response.text}")
            return LetterPronounciationResponse(
                status="fail",
                transcription="",
                feedback="Unable to process pronunciation at this time. Please try again.",
                mistake_tags=["SYSTEM_ERROR"],
                performance_reflection="API request failed"
            )
        except Exception as e:
            print(f"Unexpected error during Azure API call: {e}")
            return LetterPronounciationResponse(
                status="fail",
                transcription="",
                feedback="An unexpected error occurred. Please try again.",
                mistake_tags=["SYSTEM_ERROR"],
                performance_reflection="Unexpected error during pronunciation assessment"
            )

        pronounciation_response_json = pronounciation_response.json()
        nbest = pronounciation_response_json.get("NBest") or []
        scores = nbest[0] if nbest else {}
        transcription = scores.get("Lexical", "")
        accuracy = scores.get("AccuracyScore", 0.0)
        completeness = scores.get("CompletenessScore", 0.0)
        overall_score = scores.get("PronScore", 0.0)
        status = "fail"
        print("Got pronounciation score data")
        print(pronounciation_response_json)

        # Provides a threshold for acceptable pronounciation
        if(
            overall_score >= 88
            and accuracy >= 85
            and completeness >= 95
        ):
            status = "pass"
        else:
            status = "fail"

        pronounciation_messages = build_check_word_pronounciation_messages(word, transcription, accuracy, completeness, overall_score, status)

        # Generates feedback for the student based on the scores
        chat_response = await openai_client.chat.completions.create(
            model=os.getenv("LETTER_PRONOUNCIATION_MODEL") or "gpt-5.1-chat-latest",
            messages=pronounciation_messages,
            response_format={"type": "json_object"},
        )
        print("Made chat request")
        print(chat_response)

        # Initialize with default error response
        pronounciation_check_response = LetterPronounciationResponse(
            status=status,
            transcription=transcription,
            feedback="An error occurred while processing your pronunciation feedback. Please try again.",
            mistake_tags=[],
            performance_reflection=""
        )

        try:
            chat_response_content = chat_response.choices[0].message.content
            chat_response_obj = json.loads(chat_response_content)
            pronounciation_check_response = LetterPronounciationResponse(
                status=status,
                transcription=transcription,
                feedback=chat_response_obj["feedback"],
                mistake_tags=chat_response_obj["mistake_tags"],
                performance_reflection=chat_response_obj["performance_reflection"],
            )
            print("Parsed chat output")
            print(pronounciation_check_response)
        except Exception as e:
            print(f"Error parsing pronounciation chat response: {e}")
        
        return pronounciation_check_response


    async def explain_letter_pronounciation(self, input: LetterPronounciationExplainInput) -> LetterPronounciationExplainResponse:
        query = input.query
        letter = input.letter
        status = input.status
        transcription = input.transcription
        previous_feedback = input.previous_feedback
        mistake_tags_string = str(input.mistake_tags)
        performance_reflection = input.performance_reflection

        explain_messages = build_explain_letter_pronounciation_messages(query, letter, status, transcription, previous_feedback, mistake_tags_string, performance_reflection)

        chat_response = await openai_client.chat.completions.create(
            model=os.getenv("LETTER_PRONOUNCIATION_MODEL") or "gpt-5.2-chat-latest",
            messages=explain_messages,
            response_format={"type": "json_object"},
        )

        # Initialize with default error response
        explain_response = LetterPronounciationExplainResponse(
            feedback="An error occurred while processing your question. Please try again."
        )

        try:
            chat_response_content = chat_response.choices[0].message.content
            chat_response_obj = json.loads(chat_response_content)
            explain_response = LetterPronounciationExplainResponse(
                feedback=chat_response_obj["feedback"]
            )
        except Exception as e:
            print(f"Error parsing explain chat response: {e}")

        return explain_response

    
    async def explain_word_pronounciation(self, input: LetterWordPronounciationExplainInput) -> LetterPronounciationExplainResponse:
        query = input.query
        word = input.word
        status = input.status
        transcription = input.transcription
        previous_feedback = input.previous_feedback
        mistake_tags_string = str(input.mistake_tags)
        performance_reflection = input.performance_reflection

        explain_messages = build_explain_word_pronounciation_messages(query, word, status, transcription, previous_feedback, mistake_tags_string, performance_reflection)

        chat_response = await openai_client.chat.completions.create(
            model=os.getenv("LETTER_PRONOUNCIATION_MODEL") or "gpt-5.2-chat-latest",
            messages=explain_messages,
            response_format={"type": "json_object"},
        )

        # Initialize with default error response
        explain_response = LetterPronounciationExplainResponse(
            feedback="An error occurred while processing your question. Please try again."
        )

        try:
            chat_response_content = chat_response.choices[0].message.content
            chat_response_obj = json.loads(chat_response_content)
            explain_response = LetterPronounciationExplainResponse(
                feedback=chat_response_obj["feedback"]
            )
        except Exception as e:
            print(f"Error parsing explain chat response: {e}")

        return explain_response