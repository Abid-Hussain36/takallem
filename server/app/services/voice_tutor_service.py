import os # Helps us read env variables
import io # Helps us use data streams like audio files
import json
import base64 # Helps us encode and decode binary data as strings
import httpx # Allows us to make async API requests
from typing import Dict, Any
from langgraph.graph import StateGraph, END # Helps us build graphs
from langchain_openai import ChatOpenAI # Helps us easily make GPT calls
from langchain_core.messages import SystemMessage, HumanMessage
from app.models.voice_tutor.voice_tutor import VoiceTutorQuestionInput, VoiceTutorQuestionOutput, VoiceTutorState, VoiceTutorInput, VoiceTutorOutput, PronounciationScores, SemanticEvaluation, VocabWordResponse
from pydub import AudioSegment
from app.utils.constants import AZURE_LANGUAGE_CODE, PRONOUNCIATION_BASE_URL, TTS_BASE_URL
from app.utils.prompts.voice_tutor.voice_tutor_generate_feedback import build_voice_tutor_generate_feedback_messages
from app.utils.prompts.voice_tutor.voice_tutor_semantic_eval import build_vocab_semantic_eval_messages # Helps us convert between audio formats like webm -> wav


class VoiceTutorService:
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
        workflow.add_node("transcription", self._transcribe_node)
        workflow.add_node("pronounciation_eval", self._pronounciation_eval_node)
        workflow.add_node("semantic_eval", self._semantic_eval_node)
        workflow.add_node("generate_feedback", self._generate_feedback_node)
        workflow.add_node("speak", self._speak_node)

        workflow.set_entry_point("transcription")

        # 3. Add edges between nodes
        workflow.add_edge("transcription", "pronounciation_eval")
        workflow.add_edge("pronounciation_eval", "semantic_eval")
        workflow.add_edge("semantic_eval", "generate_feedback")
        workflow.add_edge("generate_feedback", "speak")
        workflow.add_edge("speak", END)

        # 4. We compile the workflow so we can use it
        return workflow.compile()


    async def _transcribe_node(self, state: VoiceTutorState) -> Dict[str, Any]:
        """Makes call to Azure Speech SDK to get transcription of user audio"""
        function_code = "VoiceTutorService/_transcribe_node"

        try:
            # 1. Convert bytes to WAV
            audio_bytes = base64.b64decode(state.user_audio_base64) # Decodes audio string into binary audio data
            
            # We take the bytes and covert it into the right format for Azure
            audio_segment = AudioSegment.from_file(io.BytesIO(audio_bytes))
            audio_segment = audio_segment.set_frame_rate(16000) # 16 kHz
            audio_segment = audio_segment.set_channels(1) # Mono

            # We create a buffer and load up the audio segment and extract it as WAV bytes
            wav_buffer = io.BytesIO()
            audio_segment.export(wav_buffer, format="wav")
            wav_bytes = wav_buffer.getvalue()
            
            # 2. Get transcription
            language = state.language
            dialect = state.dialect
            language_code = None

            if dialect:
                language_code = AZURE_LANGUAGE_CODE[language][dialect]
            else:
                language_code = AZURE_LANGUAGE_CODE[language]

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
                raise Exception("Failed to generate transcription")

            return {"transcription": transcription}
        except Exception as e:
            return {
                "error": f"{function_code}: Trancription failed: {str(e)}"
            }


    async def _pronounciation_eval_node(self, state: VoiceTutorState) -> Dict[str, Any]:
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
            # We get the language code we're using
            language = state.language
            dialect = state.dialect
            language_code = None

            if dialect:
                language_code = AZURE_LANGUAGE_CODE[language][dialect]
            else:
                language_code = AZURE_LANGUAGE_CODE[language]

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
        except Exception as e:
            return {"error": f"{function_code}: Pronounciation scoring failed: {str(e)}"}

    
    async def _semantic_eval_node(self, state: VoiceTutorState) -> Dict[str, Any]:
        function_code = "VoiceTutorService/_semantic_eval_node"

        try:
            # 1. We get semantic evaluation of user's response
            vocab_words_list = [f"{vocab_word.word} ({vocab_word.meaning})" for vocab_word in state.vocab_words]
            vocab_words_str = "\n".join(vocab_words_list)

            language = state.language
            dialect = state.dialect
            question = state.question
            transcription = state.transcription
             
            messages = build_vocab_semantic_eval_messages(
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
                grammar_notes=response_data["grammar_notes"],
            )

            # 2. We determine the pass/fail status of the user's response
            overall_pron_score = state.pronounciation_scores.overall
            answer_makes_sense = semantic_evaluation.answer_makes_sense
            vocab_words_used_len = len(semantic_evaluation.vocab_words_used)
            
            # Thresholds
            overall_pron_score_threshold = 70.0
            min_vocab_words_used = max(len(state.vocab_words) - 1, 1)

            status = None

            if overall_pron_score > overall_pron_score_threshold and vocab_words_used_len >= min_vocab_words_used and answer_makes_sense:
                status = "pass"
            else:
                status = "fail"

            return {
                "semantic_evaluation": semantic_evaluation,
                "status": status
            }
        except Exception as e:
            return {"error": f"{function_code}: Semantic evaluation failed: {str(e)}"}


    async def _generate_feedback_node(self, state: VoiceTutorState) -> Dict[str, Any]:
        function_code = "VoiceTutorService/_generate_feedback_node"

        try:
            vocab_words_list = [f"{vocab_word.word} ({vocab_word.meaning})" for vocab_word in state.vocab_words]
            vocab_words_str = "\n".join(vocab_words_list)

            vocab_words_used_len = len(state.semantic_evaluation.vocab_words_used)
            min_vocab_words_used = max(len(state.vocab_words) - 1, 1)
            sufficent_vocab_words_used = vocab_words_used_len >= min_vocab_words_used

            vocab_words_used_str = "\n".join(state.semantic_evaluation.vocab_words_used)
            
            status = state.status
            language = state.language
            dialect = state.dialect
            question = state.question
            transcription = state.transcription
            accuracy = state.pronounciation_scores.accuracy
            completeness = state.pronounciation_scores.completeness
            overall = state.pronounciation_scores.overall
            answer_makes_sense = state.semantic_evaluation.answer_makes_sense
            grammar_notes = state.semantic_evaluation.grammar_notes

            messages = build_voice_tutor_generate_feedback_messages(
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
                grammar_notes=grammar_notes,
                sufficent_vocab_words_used=sufficent_vocab_words_used
            )

            response = await self.llm.ainvoke(messages)
            response_data = json.loads(response.content)

            feedback_text = response_data["feedback_text"]

            if not feedback_text:
                raise Exception("No feedback was generated.")
            
            return {"feedback_text": feedback_text}
        except Exception as e:
            return {"error": f"{function_code}: Generating feedback failed: {str(e)}"}


    async def _speak_node(self, state=VoiceTutorState) -> Dict[str, Any]:
        function_code = "VoiceTutorService/_speak_node"

        try:
            headers = {
                "Accept": "audio/mpeg", # We want to get MP3 audio back
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
            feedback_audio = f"data:audio/mpeg;base64,{audio_base64}" # This is the format we need to play audio on browser

            if not feedback_audio:
                raise Exception("No feedback audio url has been returned.")

            return {"feedback_audio": feedback_audio}
        except Exception as e:
            return {"error": f"{function_code}: Generating feedback audio failed: {str(e)}"}


    async def generate_response(self, input: VoiceTutorInput) -> VoiceTutorOutput:
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
            status=final_state["status"],
            feedback_text=final_state["feedback_text"],
            feedback_audio=final_state.get("feedback_audio", None)
        )

        return output


    async def speak_question(self, input: VoiceTutorQuestionInput) -> VoiceTutorQuestionOutput:
        function_code = "VoiceTutorService/speak_question"

        try:
            headers = {
                "Accept": "audio/mpeg",
                "Content-Type": "application/json",
                "xi-api-key": self.eleven_labs_key
            }

            payload = {
                "text": input.question,
                "model_id": "eleven_multilingual_v2",
                "voice_settings": {
                    "stability": 0.5,
                    "use_speaker_boost": True,
                    "similarity_boost": 0.75,
                    "style": 0.3,
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
            question_audio = f"data:audio/mpeg;base64,{audio_base64}"

            return VoiceTutorQuestionOutput(question_audio=question_audio)
        
        except Exception as e:
            raise Exception(f"{function_code}: Failed to generate question audio: {str(e)}")