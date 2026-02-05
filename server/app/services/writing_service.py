from app.models.ai.writing import DictationExplainInput, DictationResponse, DictationScores, JoiningExplainInput, LetterHandwritingScores, LetterJoiningResponse, LetterJoiningScores, LetterWritingResponse, WritingExplainInput, WritingExplainResponse, WritingQAResponse, WritingPhotoRetakeResponse
from app.utils.openai import openai_client
from fastapi import HTTPException, UploadFile, status as http_status
from typing import List
from app.utils.prompts.writing.letter_writing_qa import build_letter_writing_qa_messages
from app.utils.prompts.writing.letter_writing import build_letter_writing_messages
from app.utils.prompts.writing.letter_joining import build_letter_joining_messages
from app.utils.enums import LetterPosition
import base64, os, json
from app.utils.prompts.writing.dictation import build_dictation_messages
from app.utils.prompts.writing.explain_joining_messages import build_explain_joining_messages
from app.utils.prompts.writing.explain_writing_messages import build_explain_writing_messages
from app.utils.prompts.writing.explain_dictation_messages import build_explain_dictation_messages
from app.db.enums import AvailableDialect, AvailableLanguage


class WritingService:
    async def check_letter_writing(
        self, 
        user_image: UploadFile, 
        target_image: UploadFile, 
        letter: str, 
        language: AvailableLanguage,
        dialect: AvailableDialect | None,
        position: LetterPosition | None
    ) -> LetterWritingResponse | WritingPhotoRetakeResponse:
        """Takes in the user's writing image and a reference image to evaluate the user's writing."""

        # 1. Establishing thresholds for QA and scoring
        thresholds = {
            "baseline_qa_confidence": 55.0,
            "baseline_eval_confidence": 60.0,
            "legibility": 75.0,
            "form_accuracy": 85.0,
            "dots_diacritics": 90.0,
            "baseline_proportion": 70.0,
            "overall": 85.0,
        }
        
        # 2. Converting files into image urls that can be fed into OpenAI API
        raw_user_bytes = await user_image.read()
        raw_target_bytes = await target_image.read()

        user_image_base64 = base64.b64encode(raw_user_bytes).decode("utf-8")
        target_image_base64 = base64.b64encode(raw_target_bytes).decode("utf-8")
        
        user_image_format = user_image.content_type or "image/jpeg"
        target_image_format = target_image.content_type or "image/jpeg"

        user_image_url = f"data:{user_image_format};base64,{user_image_base64}"
        target_image_url = f"data:{target_image_format};base64,{target_image_base64}"

        # 3. Determining if the image is actually suitable for evaluation
        qa_messages = build_letter_writing_qa_messages(user_image_url)

        try:
            qa_chat_response = await openai_client.chat.completions.create(
                model=os.getenv("PRIMARY_MODEL") or "gpt-5.2-chat-latest",
                messages=qa_messages,
                response_format={"type": "json_object"},
            )

            qa_response_content = qa_chat_response.choices[0].message.content
            qa_response_obj = json.loads(qa_response_content)

            qa_response = WritingQAResponse(
                is_usable=qa_response_obj["is_usable"],
                confidence=qa_response_obj["confidence"],
                reasons=qa_response_obj["reasons"],
                capture_tips=qa_response_obj["capture_tips"]
            )
        except Exception as e:
            raise HTTPException(
                status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error when performing QA for letter writing: {str(e)}"
            )

        # If QA says the image is not good enough, we ask the user to retake their writing image
        if (not qa_response.is_usable) or qa_response.confidence < thresholds["baseline_qa_confidence"]:
            return WritingPhotoRetakeResponse(capture_tips=qa_response.capture_tips)

        # 4. Running evaluation of user writing image relative to the target image and actual letter
        position_value = position.value if position else None
        language_value = language.value
        dialect_value = dialect.value if dialect else None

        writing_eval_messages = build_letter_writing_messages(user_image_url, target_image_url, letter, language_value, dialect_value, position_value)
        status = "fail"

        try:
            writing_eval_chat_response = await openai_client.chat.completions.create(
                model=os.getenv("PRIMARY_MODEL") or "gpt-5.2-chat-latest",
                messages=writing_eval_messages,
                response_format={"type": "json_object"}
            )

            writing_eval_response_content = writing_eval_chat_response.choices[0].message.content
            writing_eval_response_obj = json.loads(writing_eval_response_content)

            handwriting_scores = LetterHandwritingScores(
                legibility=writing_eval_response_obj["scores"]["legibility"],
                form_accuracy=writing_eval_response_obj["scores"]["form_accuracy"],
                dots_diacritics=writing_eval_response_obj["scores"]["dots_diacritics"],
                baseline_proportion=writing_eval_response_obj["scores"]["baseline_proportion"],
                overall=writing_eval_response_obj["scores"]["overall"],
            )

            passed = (
                writing_eval_response_obj["confidence"] >= thresholds["baseline_eval_confidence"]
                and handwriting_scores.legibility >= thresholds["legibility"]
                and handwriting_scores.form_accuracy >= thresholds["form_accuracy"]
                and handwriting_scores.dots_diacritics >= thresholds["dots_diacritics"]
                and handwriting_scores.baseline_proportion >= thresholds["baseline_proportion"]
                and handwriting_scores.overall >= thresholds["overall"] 
            )

            if passed:
                status = "pass"

            writing_eval_response = LetterWritingResponse(
                status=status,
                scores=handwriting_scores,
                feedback=writing_eval_response_obj["feedback"],
                mistake_tags=writing_eval_response_obj["mistake_tags"],
                performance_reflection=writing_eval_response_obj["performance_reflection"]
            )

            return writing_eval_response
        except Exception as e:
            raise HTTPException(
                status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error when evaluating user writing image in letter writing: {str(e)}"
            )


    async def check_letter_joining(
        self, 
        user_image: UploadFile, 
        letter_list: List[str], 
        target_word: str,
        language: AvailableLanguage,
        dialect: AvailableDialect | None
    ) -> LetterJoiningResponse | WritingPhotoRetakeResponse:
        """Takes in the user's writing image of joining a list of letters and evaluates the user's writing."""

        # 1. Establishing thresholds for QA and scoring
        thresholds = {
            "baseline_qa_confidence": 55.0,
            "baseline_eval_confidence": 62.0,
            "connection_accuracy": 85.0,
            "positional_forms": 82.0,
            "dots_diacritics": 90.0,
            "spacing_flow": 75.0,
            "baseline_consistency": 70.0,
            "overall": 85.0,
        }
        
        # 2. Converting file into image urls that can be fed into OpenAI API
        raw_user_bytes = await user_image.read()
        user_image_base64 = base64.b64encode(raw_user_bytes).decode("utf-8")
        user_image_format = user_image.content_type or "image/jpeg"
        user_image_url = f"data:{user_image_format};base64,{user_image_base64}"

        print(f"Image Format: {user_image_format}")
        print(f"Image b64 Len: {len(user_image_base64)}")

        # 3. Determining if the image is actually suitable for evaluation
        qa_messages = build_letter_writing_qa_messages(user_image_url)

        try:
            qa_chat_response = await openai_client.chat.completions.create(
                model=os.getenv("PRIMARY_MODEL") or "gpt-5.2-chat-latest",
                messages=qa_messages,
                response_format={"type": "json_object"}
            )

            qa_response_content = qa_chat_response.choices[0].message.content
            qa_response_obj = json.loads(qa_response_content)

            qa_response = WritingQAResponse(
                is_usable=qa_response_obj["is_usable"],
                confidence=qa_response_obj["confidence"],
                reasons=qa_response_obj["reasons"],
                capture_tips=qa_response_obj["capture_tips"]
            )
        except Exception as e:
            raise HTTPException(
                status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error when performing QA for letter joining: {str(e)}"
            )

        # If QA says the image is not good enough, we ask the user to retake their writing image
        if (not qa_response.is_usable) or qa_response.confidence < thresholds["baseline_qa_confidence"]:
            return WritingPhotoRetakeResponse(capture_tips=qa_response.capture_tips)

        # 4. Running evaluation of user joining writing image relative to the target word
        letter_list_str = str(letter_list)
        language_value = language.value
        dialect_value = dialect.value if dialect else None
        joining_messages = build_letter_joining_messages(user_image_url, letter_list_str, target_word, language_value, dialect_value)
        status = "fail"

        try:
            joining_chat_response = await openai_client.chat.completions.create(
                model=os.getenv("PRIMARY_MODEL") or "gpt-5.2-chat-latest",
                messages=joining_messages,
                response_format={"type": "json_object"}
            )

            joining_content = joining_chat_response.choices[0].message.content
            joining_obj = json.loads(joining_content)

            joining_scores = LetterJoiningScores(
                connection_accuracy=joining_obj["scores"]["connection_accuracy"],
                positional_forms=joining_obj["scores"]["positional_forms"],
                spacing_flow=joining_obj["scores"]["spacing_flow"],
                baseline_consistency=joining_obj["scores"]["baseline_consistency"],
                dots_diacritics=joining_obj["scores"]["dots_diacritics"],
                overall=joining_obj["scores"]["overall"],
            )

            passed = (
                joining_obj["confidence"] >= thresholds["baseline_eval_confidence"]
                and joining_scores.connection_accuracy >= thresholds["connection_accuracy"]
                and joining_scores.positional_forms >= thresholds["positional_forms"]
                and joining_scores.dots_diacritics >= thresholds["dots_diacritics"]
                and joining_scores.baseline_consistency >= thresholds["baseline_consistency"]
                and joining_scores.spacing_flow >= thresholds["spacing_flow"]
                and joining_scores.overall >= thresholds["overall"] 
            )

            if passed:
                status = "pass"

            joining_response = LetterJoiningResponse(
                status=status,
                scores=joining_scores,
                feedback=joining_obj["feedback"],
                mistake_tags=joining_obj["mistake_tags"],
                performance_reflection=joining_obj["performance_reflection"]
            )

            return joining_response
        except Exception as e:
            raise HTTPException(
                status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error when evaluating user image in letter joining: {str(e)}"
            )


    async def check_dictation(self, user_image: UploadFile, target_word: str, language: AvailableLanguage, dialect: AvailableDialect | None) -> DictationResponse | WritingPhotoRetakeResponse:
        """Takes in the user's writing image from a dictation and evaluates the user's writing."""

        # 1. Establishing thresholds for QA and scoring
        thresholds = {
            "baseline_qa_confidence": 70.0,
            "baseline_eval_confidence": 65.0,
            "word_accuracy": 90.0,
            "letter_identity": 90.0,
            "joining_quality": 80.0,
            "legibility": 75.0,
            "dots_diacritics": 92.0,
            "baseline_spacing": 70.0,
            "overall": 85.0,
        }

        # 2. Converting file into image urls that can be fed into OpenAI API
        raw_user_bytes = await user_image.read()
        user_image_base64 = base64.b64encode(raw_user_bytes).decode("utf-8")
        user_image_format = user_image.content_type or "image/jpeg"
        user_image_url = f"data:{user_image_format};base64,{user_image_base64}"

        # 3. Determining if the image is actually suitable for evaluation
        qa_messages = build_letter_writing_qa_messages(user_image_url)

        try:
            qa_chat_response = await openai_client.chat.completions.create(
                model=os.getenv("PRIMARY_MODEL") or "gpt-5.2-chat-latest",
                messages=qa_messages,
                response_format={"type": "json_object"}
            )
            
            qa_response_content = qa_chat_response.choices[0].message.content
            qa_response_obj = json.loads(qa_response_content)
            
            qa_response = WritingQAResponse(
                is_usable=qa_response_obj["is_usable"],
                confidence=qa_response_obj["confidence"],
                reasons=qa_response_obj["reasons"],
                capture_tips=qa_response_obj["capture_tips"]
            )
        except Exception as e:
            raise HTTPException(
                status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error when performing QA for dictation: {str(e)}"
            )

        # If QA says the image is not good enough, we ask the user to retake their writing image
        if (not qa_response.is_usable) or qa_response.confidence < thresholds["baseline_qa_confidence"]:
            return WritingPhotoRetakeResponse(capture_tips=qa_response.capture_tips)

        # 4. Running evaluation of user dictation writing image relative to the target word
        language_value = language.value
        dialect_value = dialect.value if dialect else None
        dictation_messages = build_dictation_messages(user_image_url, target_word, language_value, dialect_value)
        status = "fail"

        try:
            dictation_chat_response = await openai_client.chat.completions.create(
                model=os.getenv("PRIMARY_MODEL") or "gpt-5.2-chat-latest",
                messages=dictation_messages,
                response_format={"type": "json_object"}
            )

            dictation_content = dictation_chat_response.choices[0].message.content
            dictation_obj = json.loads(dictation_content)

            dictation_scores = DictationScores(
                word_accuracy=dictation_obj["scores"]["word_accuracy"],
                letter_identity=dictation_obj["scores"]["letter_identity"],
                joining_quality=dictation_obj["scores"]["joining_quality"],
                legibility=dictation_obj["scores"]["legibility"],
                dots_diacritics=dictation_obj["scores"]["dots_diacritics"],
                baseline_spacing=dictation_obj["scores"]["baseline_spacing"],
                overall=dictation_obj["scores"]["overall"],
            )
            
            passed = (
                dictation_obj["confidence"] >= thresholds["baseline_eval_confidence"]
                and dictation_obj["detected_word"] == target_word
                and dictation_scores.word_accuracy >= thresholds["word_accuracy"]
                and dictation_scores.letter_identity >= thresholds["letter_identity"]
                and dictation_scores.joining_quality >= thresholds["joining_quality"]
                and dictation_scores.legibility >= thresholds["legibility"]
                and dictation_scores.dots_diacritics >= thresholds["dots_diacritics"]
                and dictation_scores.baseline_spacing >= thresholds["baseline_spacing"]
                and dictation_scores.overall >= thresholds["overall"]
            )

            if passed:
                status = "pass"

            dictation_response = DictationResponse(
                status=status,
                detected_word=dictation_obj["detected_word"],
                scores=dictation_scores,
                feedback=dictation_obj["feedback"],
                mistake_tags=dictation_obj["mistake_tags"],
                performance_reflection=dictation_obj["performance_reflection"]
            )

            return dictation_response
        except Exception as e:
            raise HTTPException(
                status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error when evaluating user image in dictation: {str(e)}"
            )

    
    async def explain_writing(self, input: WritingExplainInput) -> WritingExplainResponse:
        """Takes in a reflection on the user's letter writing performance and user question and returns a response."""
        
        query = input.query
        language = input.language.value
        dialect = input.dialect.value if input.dialect else None
        letter = input.letter
        position = input.position
        status = input.status
        legibility = input.scores.legibility
        form_accuracy = input.scores.form_accuracy
        dots_diacritics = input.scores.dots_diacritics
        baseline_proportion = input.scores.baseline_proportion
        overall = input.scores.overall
        previous_feedback = str(input.previous_feedback)
        mistake_tags = str(input.mistake_tags)
        performance_reflection = input.performance_reflection

        position_value = None
        if position:
            position_value = position.value

        explain_messages = build_explain_writing_messages(
            query,
            language,
            dialect,
            letter, 
            position_value, 
            status, 
            legibility, 
            form_accuracy,
            dots_diacritics,
            baseline_proportion,
            overall,
            previous_feedback,
            mistake_tags,
            performance_reflection
        )

        try:
            chat_response = await openai_client.chat.completions.create(
                model=os.getenv("PRIMARY_MODEL") or "gpt-5.2-chat-latest",
                messages=explain_messages,
                response_format={"type": "json_object"},
            )

            chat_response_content = chat_response.choices[0].message.content
            chat_response_obj = json.loads(chat_response_content)

            explain_response = WritingExplainResponse(
                response=chat_response_obj["response"]
            )
            return explain_response
        except Exception as e:
            raise HTTPException(
                status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error when generating response for explain writing: {str(e)}"
            )


    async def explain_joining(self, input: JoiningExplainInput) -> WritingExplainResponse:
        """Takes in a reflection on the user's letter joining performance and user question and returns a response."""
        
        query = input.query
        language = input.language.value
        dialect = input.dialect.value if input.dialect else None
        letter_list = str(input.letter_list)
        target_word = input.target_word
        status = input.status
        connection_accuracy = input.scores.connection_accuracy
        positional_forms = input.scores.positional_forms
        spacing_flow = input.scores.spacing_flow
        baseline_consistency = input.scores.baseline_consistency
        dots_diacritics = input.scores.dots_diacritics
        overall = input.scores.overall
        previous_feedback = str(input.previous_feedback)
        mistake_tags = str(input.mistake_tags)
        performance_reflection = input.performance_reflection

        explain_messages = build_explain_joining_messages(
            query,
            language,
            dialect,
            letter_list, 
            target_word, 
            status, 
            connection_accuracy, 
            positional_forms,
            spacing_flow,
            baseline_consistency,
            dots_diacritics,
            overall,
            previous_feedback,
            mistake_tags,
            performance_reflection
        )

        try:
            chat_response = await openai_client.chat.completions.create(
                model=os.getenv("PRIMARY_MODEL") or "gpt-5.2-chat-latest",
                messages=explain_messages,
                response_format={"type": "json_object"},
            )

            chat_response_content = chat_response.choices[0].message.content
            chat_response_obj = json.loads(chat_response_content)

            explain_response = WritingExplainResponse(
                response=chat_response_obj["response"]
            )

            return explain_response
        except Exception as e:
            raise HTTPException(
                status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error when generating response for explain joining: {str(e)}"
            )


    async def explain_dictation(self, input: DictationExplainInput) -> WritingExplainResponse:
        """Takes in a reflection on the user's dictation performance and user question and returns a response."""
        
        query = input.query
        language = input.language.value
        dialect = input.dialect.value if input.dialect else None
        target_word = input.target_word
        status = input.status
        word_accuracy = input.scores.word_accuracy
        letter_identity = input.scores.letter_identity
        joining_quality = input.scores.joining_quality
        legibility = input.scores.legibility
        dots_diacritics = input.scores.dots_diacritics
        baseline_spacing = input.scores.baseline_spacing
        overall = input.scores.overall
        previous_feedback = str(input.previous_feedback)
        mistake_tags = str(input.mistake_tags)
        performance_reflecton = input.performance_reflection

        explain_messages = build_explain_dictation_messages(
            query,
            language,
            dialect,
            target_word,
            status,
            word_accuracy,
            letter_identity,
            joining_quality,
            legibility,
            dots_diacritics,
            baseline_spacing,
            overall,
            previous_feedback,
            mistake_tags,
            performance_reflecton
        )

        try:
            chat_response = await openai_client.chat.completions.create(
                model=os.getenv("PRIMARY_MODEL") or "gpt-5.2-chat-latest",
                messages=explain_messages,
                response_format={"type": "json_object"},
            )

            chat_response_content = chat_response.choices[0].message.content
            chat_response_obj = json.loads(chat_response_content)

            explain_response = WritingExplainResponse(
                response=chat_response_obj["response"]
            )

            return explain_response
        except Exception as e:
            raise HTTPException(
                status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error when generating response for explain dictation: {str(e)}"
            )