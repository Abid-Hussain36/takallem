import os # Helps us read env variables
import io # Helps us use data streams like audio files
import json
import base64 # Helps us encode and decode binary data as strings
from fastapi import HTTPException, status as http_status
import httpx # Allows us to make async API requests
from typing import Dict, Any
from langgraph.graph import StateGraph, END # Helps us build graphs
from langchain_openai import ChatOpenAI # Helps us easily make GPT calls
from app.models.ai.speaking import VoiceTutorExplainInput, VoiceTutorExplainOutput, VoiceTutorState, VoiceTutorInput, VoiceTutorOutput, PronounciationScores, SemanticEvaluation, VocabWordResponse, VoiceTutorTTSInput, VoiceTutorTTSOutput
from pydub import AudioSegment
from app.utils.constants import AZURE_LANGUAGE_CODE, PRONOUNCIATION_BASE_URL, TTS_BASE_URL
from app.utils.prompts.speaking.generate_feedback import build_generate_feedback_messages
from app.db.enums import AvailableDialect, AvailableLanguage
from app.utils.prompts.speaking.semantic_eval import build_semantic_eval_messages
from app.utils.prompts.speaking.explain_speaking import build_explain_speaking_messages


class SpeakingService:
    """This class runs the voice tutor langchain workflow and returns the result to the user."""

    def __init__(self):
        # Setup GPT
        self.llm = ChatOpenAI(
            model=os.getenv("PRIMARY_MODEL"),
            temperature=0.7,
            api_key=os.getenv("OPENAI_API_KEY")
        )

        # Get API Keys and Data
        self.azure_key = os.getenv("AZURE_SUBSCRIPTION_KEY")
        self.openai_key = os.getenv("OPENAI_API_KEY")
        self.eleven_labs_key = os.getenv("ELEVEN_LABS_KEY")
        self.eleven_labs_voice_id = os.getenv("ELEVEN_LABS_VOICE_ID")

        # Build LangGraph Workflow
        self.workflow = self._build_workflow()

    
    def _build_workflow(self):
        """Builds the LangGraph workflow to generate the voice tutor response"""
        # 1. We create a blank workflow that uses this state
        workflow = StateGraph(VoiceTutorState)

        # 2. Add needed nodes to graph
        # A node just takes the state as input -> does stuff -> updates the state
        workflow.add_node("transcribe", self._transcribe_node)
        workflow.add_node("pronounciation_eval", self._pronounciation_eval_node)
        workflow.add_node("semantic_eval", self._semantic_eval_node)
        workflow.add_node("generate_feedback", self._generate_feedback_node)
        workflow.add_node("speak", self._speak_node)

        workflow.set_entry_point("transcribe")

        # 3. Add edges between nodes
        workflow.add_edge("transcribe", "pronounciation_eval")
        workflow.add_edge("pronounciation_eval", "semantic_eval")
        workflow.add_edge("semantic_eval", "generate_feedback")
        workflow.add_edge("generate_feedback", "speak")
        workflow.add_edge("speak", END)

        # 4. We compile the workflow so we can use it
        return workflow.compile()


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


    async def _transcribe_node(self, state: VoiceTutorState) -> Dict[str, Any]:
        """Makes call to Azure Speech SDK to get transcription of user audio"""
        
        function_code = "VoiceTutorService/_transcribe_node"

        try:
            # 1. Convert bytes to WAV
            audio_bytes = base64.b64decode(state.user_audio_base64) # Decodes audio string into binary audio data
            
            # We take the bytes and covert it into the right format for Azure
            audio_segment = AudioSegment.from_file(io.BytesIO(audio_bytes))
            audio = audio_segment.set_frame_rate(16000).set_channels(1) # 16 kHz

            # We create a buffer and load up the audio segment and extract it as WAV bytes
            wav_buffer = io.BytesIO()
            audio.export(wav_buffer, format="wav")
            wav_bytes = wav_buffer.getvalue()
            
            # 2. Get transcription
            language = state.language
            dialect = state.dialect

            language_code = self._get_language_code(language, dialect)

            azure_url = f"{PRONOUNCIATION_BASE_URL}?language={language_code}"

            headers = {
                "Ocp-Apim-Subscription-Key": self.azure_key,
                "Content-type": "audio/wav; codecs=audio/pcm; samplerate=16000",
            }

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    azure_url,
                    headers=headers,
                    content=wav_bytes,
                    timeout=30.0
                )

                response.raise_for_status() # This raises an HTTP error if we get a 400 or 500 status code
            
            result = response.json()
            transcription = result["DisplayText"]
            
            if not transcription:
                raise HTTPException(
                    status_code=http_status.HTTP_404_NOT_FOUND,
                    detail=f"{function_code}: Failed to generate transcription with Azure."
                )

            return {"transcription": transcription}
        except HTTPException:
            raise
        except ValueError as e:
            raise HTTPException(
                status_code=http_status.HTTP_400_BAD_REQUEST,
                detail=f"{function_code}: {str(e)}"
            )
        except Exception as e:
            raise HTTPException(
                status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"{function_code}: Error in generating transcription for user audio: {str(e)}"
            )


    async def _pronounciation_eval_node(self, state: VoiceTutorState) -> Dict[str, Any]:
        """Generates pronounciation scores for user audio using the Azure API."""

        function_code = "VoiceTutorService/_pronounciation_eval_node"

        try:
            # 1. Covert audio file to WAV
            audio_bytes = base64.b64decode(state.user_audio_base64)
            
            audio_segment = AudioSegment.from_file(io.BytesIO(audio_bytes))
            audio_segment = audio_segment.set_frame_rate(16000) # 16 kHz
            audio_segment = audio_segment.set_channels(1) # Mono

            wav_buffer = io.BytesIO()
            audio_segment.export(wav_buffer, format="wav")
            wav_bytes = wav_buffer.getvalue()

            # 2. Get pronounciation scores
            language = state.language
            dialect = state.dialect

            language_code = self._get_language_code(language, dialect)

            azure_url = f"{PRONOUNCIATION_BASE_URL}?language={language_code}&format=detailed"

            pron_params = {
                "ReferenceText": state.transcription,
                "GradingSystem": "HundredMark",
                "Granularity": "Word",
                "Dimension": "Comprehensive"
            }

            config_json = json.dumps(pron_params).encode("utf-8")
            config_base64 = base64.b64encode(config_json).decode()

            headers = {
                "Ocp-Apim-Subscription-Key": self.azure_key,
                "Pronunciation-Assessment": config_base64,
                "Content-type": "audio/wav; codecs=audio/pcm; samplerate=16000",
            }

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    azure_url,
                    headers=headers,
                    content=wav_bytes,
                    timeout=30.0
                )

                response.raise_for_status()

            result = response.json()
            nbest = result.get("NBest", [])
            best_result = nbest[0] if nbest else {}
            scores = PronounciationScores(
                accuracy=best_result.get("AccuracyScore", 0.0),
                completeness=best_result.get("CompletenessScore", 0.0),
                overall=best_result.get("PronScore", 0.0)
            )

            return {"pronounciation_scores": scores}
        except HTTPException:
            raise
        except ValueError as e:
            raise HTTPException(
                status_code=http_status.HTTP_400_BAD_REQUEST,
                detail=f"{function_code}: {str(e)}"
            )
        except Exception as e:
            raise HTTPException(
                status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"{function_code}: Pronounciation scoring failed: {str(e)}"
            )

    
    async def _semantic_eval_node(self, state: VoiceTutorState) -> Dict[str, Any]:
        """Determines if the user answer makes sense for the question asked and evaluates the answer's grammatical accuracy."""

        function_code = "VoiceTutorService/_semantic_eval_node"

        try:
            # 1. We get semantic evaluation of user's response
            vocab_words_list = [f"{vocab_word.word} ({vocab_word.meaning})" for vocab_word in state.vocab_words]
            vocab_words_str = "\n".join(vocab_words_list)

            language = state.language.value
            dialect = state.dialect.value if state.dialect else None
            question = state.question
            transcription = state.transcription
             
            messages = build_semantic_eval_messages(
                language=language, 
                dialect=dialect, 
                question=question, 
                vocab_words=vocab_words_str, 
                transcription=transcription
            )

            response = await self.llm.ainvoke(messages)
            response_data = json.loads(response.content)

            semantic_evaluation = SemanticEvaluation(
                vocab_words_used=response_data["vocab_words_used"],
                answer_makes_sense=response_data["answer_makes_sense"],
                grammatical_score=response_data["grammatical_score"],
                grammar_notes=response_data["grammar_notes"],
            )

            return {
                "semantic_evaluation": semantic_evaluation,
            }
        except Exception as e:
            raise HTTPException(
                status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"{function_code}: Semantic eval failed: {str(e)}"
            )


    async def _generate_feedback_node(self, state: VoiceTutorState) -> Dict[str, Any]:
        """Takes in all the user audio evaluation data, determines if the user audio passes, and generates feedback."""

        function_code = "VoiceTutorService/_generate_feedback_node"

        try:
            vocab_words_list = [f"{vocab_word.word} ({vocab_word.meaning})" for vocab_word in state.vocab_words]
            vocab_words_str = "\n".join(vocab_words_list)
            vocab_words_used_str = "\n".join(state.semantic_evaluation.vocab_words_used)

            # 2. We determine the pass/fail status of the user's response
            overall_pron_score = state.pronounciation_scores.overall
            grammatical_score = state.semantic_evaluation.grammatical_score
            answer_makes_sense = state.semantic_evaluation.answer_makes_sense
            vocab_words_used_len = len(state.semantic_evaluation.vocab_words_used)
            
            # Thresholds
            overall_pron_score_threshold = 70.0
            grammatical_score_threshold = 70.0
            min_vocab_words_used = max(len(state.vocab_words) - 1, 1)

            if(
                overall_pron_score > overall_pron_score_threshold 
                and grammatical_score > grammatical_score_threshold
                and vocab_words_used_len >= min_vocab_words_used 
                and answer_makes_sense
            ):
                status = "pass"
            else:
                status = "fail"

            language = state.language.value
            dialect = state.dialect.value
            question = state.question
            transcription = state.transcription
            accuracy = state.pronounciation_scores.accuracy
            completeness = state.pronounciation_scores.completeness
            overall = state.pronounciation_scores.overall
            grammar_notes = state.semantic_evaluation.grammar_notes
            sufficent_vocab_words_used = vocab_words_used_len >= min_vocab_words_used

            messages = build_generate_feedback_messages(
                status=status, 
                language=language, 
                dialect=dialect,
                question=question,
                vocab_words=vocab_words_str,
                transcription=transcription,
                accuracy=accuracy,
                completeness=completeness,
                overall=overall,
                vocab_words_used=vocab_words_used_str,
                answer_makes_sense=answer_makes_sense,
                grammatical_score=grammatical_score,
                grammar_notes=grammar_notes,
                sufficent_vocab_words_used=sufficent_vocab_words_used
            )

            response = await self.llm.ainvoke(messages)
            response_data = json.loads(response.content)

            feedback_text = response_data["feedback_text"]
            performance_reflection = response_data["performance_reflection"]

            if not feedback_text:
                raise HTTPException(
                    status_code=http_status.HTTP_404_NOT_FOUND,
                    detail=f"{function_code}: Failed to generate feedback with OpenAI API."
                )
            
            return {
                "status": status,
                "feedback_text": feedback_text,
                "performance_reflection": performance_reflection
            }
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"{function_code}: Generate feedback failed: {str(e)}"
            )


    async def _speak_node(self, state: VoiceTutorState) -> Dict[str, Any]:
        """Performs TTS on the feedback text and generates the resulting audio file."""

        function_code = "VoiceTutorService/_speak_node"

        try:
            headers = {
                "Accept": "audio/mpeg", # We want to get MP3 audio back. Might cause issues
                "Content-Type": "application/json",
                "xi-api-key": os.getenv("ELEVEN_LABS_KEY")
            }

            payload = {
                "text": state.feedback_text,
                "model_id": "eleven_multilingual_v2",
                "voice_settings": {
                    "stability": 0.5, # How emotive the voice is
                    "use_speaker_boost": True, # Boosts similarity of the voice of the response to the selected voice
                    "similarity_boost": 0.75, # Determines how closely response follows specified voice
                    "style": 0.3, # How exaggerated the response voice is
                    "speed": 0.8 # Controls the speed of the voice
                }
            }

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    TTS_BASE_URL,
                    headers=headers,
                    json=payload,
                    timeout=30.0
                )

                response.raise_for_status()

            audio_bytes = response.content
            audio_base64 = base64.b64encode(audio_bytes).decode()
            feedback_audio_base64 = f"data:audio/mpeg;base64,{audio_base64}" # This is the format we need to play audio on browser

            if not feedback_audio_base64:
                raise HTTPException(
                    status_code=http_status.HTTP_404_NOT_FOUND,
                    detail=f"{function_code}: Failed to perform TTS with ElevenLabs API."
                )

            return {"feedback_audio_base64": feedback_audio_base64}
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"{function_code}: Generating feedback audio failed: {str(e)}"
            )


    async def speak(self, input: VoiceTutorTTSInput) -> VoiceTutorTTSOutput:
        """Performs TTS on the feedback text and generates the resulting audio file."""

        try:
            text = input.text

            headers = {
                "Accept": "audio/mpeg", # We want to get MP3 audio back. Might cause issues
                "Content-Type": "application/json",
                "xi-api-key": os.getenv("ELEVEN_LABS_KEY")
            }

            payload = {
                "text": text,
                "model_id": "eleven_multilingual_v2",
                "voice_settings": {
                    "stability": 0.5, # How emotive the voice is
                    "use_speaker_boost": True, # Boosts similarity of the voice of the response to the selected voice
                    "similarity_boost": 0.75, # Determines how closely response follows specified voice
                    "style": 0.3, # How exaggerated the response voice is
                    "speed": 0.8 # Controls the speed of the voice
                }
            }

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    TTS_BASE_URL,
                    headers=headers,
                    json=payload,
                    timeout=30.0
                )

                response.raise_for_status()

            audio_bytes = response.content
            audio_base64 = base64.b64encode(audio_bytes).decode()
            response_audio_base64 = f"data:audio/mpeg;base64,{audio_base64}" # This is the format we need to play audio on browser

            if not response_audio_base64:
                raise HTTPException(
                    status_code=http_status.HTTP_404_NOT_FOUND,
                    detail=f"Failed to perform TTS with ElevenLabs API."
                )

            return VoiceTutorTTSOutput(response_audio_base64=response_audio_base64)
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Generating response audio failed: {str(e)}"
            )


    async def generate_response(self, input: VoiceTutorInput) -> VoiceTutorOutput:
        """Generates feedback on the user's speaking performance based on the question details."""

        # 1. Creating the initial graph state
        initial_state = VoiceTutorState(
            question=input.question,
            language=input.language,
            dialect=input.dialect,
            vocab_words=input.vocab_words,
            user_audio_base64=input.user_audio_base64
        )

        # 2. Run workflow on initial state
        final_state = await self.workflow.ainvoke(initial_state)

        # 3. Create and return the output object
        output = VoiceTutorOutput(
            transcription=final_state["transcription"],
            pronounciation_scores=final_state["pronounciation_scores"],
            semantic_evaluation=final_state["semantic_evaluation"],
            status=final_state["status"],
            performance_reflection=final_state["performance_reflection"],
            feedback_text=final_state.get("feedback_text", None),
            feedback_audio_base64=final_state.get("feedback_audio_base64", None)
        )

        return output


    async def explain_response(self, input: VoiceTutorExplainInput) -> VoiceTutorExplainOutput:
        """Takes in previous eval data regarding user performance and generates an audio response."""

        try:
            query = input.query
            question = input.question
            language = input.language.value
            dialect = input.dialect.value if input.dialect else None
            vocab_words = input.vocab_words

            transcription = input.transcription
            accuracy = input.pronounciation_scores.accuracy
            completeness = input.pronounciation_scores.completeness
            overall = input.pronounciation_scores.overall

            vocab_words_used = str(input.semantic_evaluation.vocab_words_used)
            answer_makes_sense = input.semantic_evaluation.answer_makes_sense
            grammatical_score = input.semantic_evaluation.grammatical_score
            grammar_notes = input.semantic_evaluation.grammar_notes

            status = input.status
            performance_reflection = input.performance_reflection
            previous_feedback = str(input.previous_feedback)


            vocab_words_list = [f"{vocab_word.word} ({vocab_word.meaning})" for vocab_word in vocab_words]
            vocab_words_str = "\n".join(vocab_words_list)

            messages = build_explain_speaking_messages(
                query=query,
                question=question,
                language=language,
                dialect=dialect,
                vocab_words=vocab_words_str,
                transcription=transcription,
                accuracy=accuracy,
                completeness=completeness,
                overall=overall,
                vocab_words_used=vocab_words_used,
                answer_makes_sense=answer_makes_sense,
                grammatical_score=grammatical_score,
                grammar_notes=grammar_notes,
                status=status,
                performance_reflection=performance_reflection,
                previous_feedback=previous_feedback
            )

            response = await self.llm.ainvoke(messages)
            response_data = json.loads(response.content)
            response_text = response_data["response_text"]

            if not response_text:
                raise HTTPException(
                    status_code=http_status.HTTP_404_NOT_FOUND,
                    detail="Failed to generate speaking query response with OpenAI API."
                )

            return VoiceTutorExplainOutput(response_text=response_text)
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Generating speaking query response failed: {str(e)}"
            )