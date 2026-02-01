from app.models.ai.writing import DictationResponse, DictationScores, LetterHandwritingScores, LetterJoiningResponse, LetterJoiningScores, LetterWritingResponse, WritingQAResponse, WritingPhotoRetakeResponse
from app.utils.openai import openai_client
from fastapi import UploadFile
from typing import Union, List
from app.utils.prompts.writing.letter_writing_qa import build_letter_writing_qa_messages
from app.utils.prompts.writing.letter_writing import build_letter_writing_messages
from app.utils.prompts.writing.letter_joining import build_letter_joining_messages
from app.utils.prompts.writing.letter_dictation import build_letter_dictation_messages
from app.utils.enums import LetterPosition
import base64, os, json


class WritingService:
    async def check_letter_writing(self, user_image: UploadFile, target_image: UploadFile, letter: str, position: LetterPosition) -> Union[LetterWritingResponse, WritingPhotoRetakeResponse]:
        thresholds = {
            "baseline_qa_confidence": 55.0,
            "baseline_eval_confidence": 60.0,
            "legibility": 75.0,
            "form_accuracy": 85.0,
            "dots_diacritics": 90.0,
            "baseline_proportion": 70.0,
            "overall": 85.0,
        }
        
        raw_user_bytes = await user_image.read()
        raw_target_bytes = await target_image.read()

        # Converting Image Bytes to base64 for processing
        user_image_base64 = base64.b64encode(raw_user_bytes).decode("utf-8")
        target_image_base64 = base64.b64encode(raw_target_bytes).decode("utf-8")
        
        user_image_format = user_image.content_type or "image/jpeg"
        target_image_format = target_image.content_type or "image/jpeg"

        # Building image urls for the OpenAI API
        user_image_url = f"data:{user_image_format};base64,{user_image_base64}"
        target_image_url = f"data:{target_image_format};base64,{target_image_base64}"

        qa_messages = build_letter_writing_qa_messages(user_image_url)

        qa_chat_response = await openai_client.chat.completions.create(
            model=os.getenv("PRIMARY_MODEL") or "gpt-5.2-chat-latest",
            messages=qa_messages,
            response_format={"type": "json_object"},
        )

        # Initialize with default error response
        qa_response = WritingQAResponse(
            is_usable=False,
            confidence=0.0,
            reasons=["Error processing image"],
            capture_tips="Please ensure the image is clear and try again."
        )

        try:
            qa_response_content = qa_chat_response.choices[0].message.content
            qa_response_obj = json.loads(qa_response_content)
            qa_response = WritingQAResponse(
                is_usable=qa_response_obj["is_usable"],
                confidence=qa_response_obj["confidence"],
                reasons=qa_response_obj["reasons"],
                capture_tips=qa_response_obj["capture_tips"]
            )
        except Exception as e:
            print(f"QA error when checking letter writing: {e}")

        # If QA says the image is not good enough, we ask the user to retake their writing image
        if (not qa_response.is_usable) or qa_response.confidence < thresholds["baseline_qa_confidence"]:
            return WritingPhotoRetakeResponse(capture_tips=qa_response.capture_tips)

        writing_eval_messages = build_letter_writing_messages(user_image_url, target_image_url, letter, position.value)

        writing_eval_chat_response = await openai_client.chat.completions.create(
            model=os.getenv("PRIMARY_MODEL") or "gpt-5.2-chat-latest",
            messages=writing_eval_messages,
            response_format={"type": "json_object"}
        )

        status = "fail"
        # Initialize with default error response
        writing_eval_response = LetterWritingResponse(
            status=status,
            scores=LetterHandwritingScores(
                legibility=0.0,
                form_accuracy=0.0,
                dots_diacritics=0.0,
                baseline_proportion=0.0,
                overall=0.0
            ),
            feedback="An error occurred while evaluating your writing. Please try again.",
            mistake_tags=[],
            performance_reflection=""
        )

        try:
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
        except Exception as e:
            print(f"Error when parsing response of letter written evaluation: {e}")

        return writing_eval_response


    async def check_letter_joining(self, user_image: UploadFile, letter_list: List[str], target_word: str) -> Union[LetterJoiningResponse, WritingPhotoRetakeResponse]:
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
        
        raw_user_bytes = await user_image.read()

        # Getting image in the right format to be sent to OpenAI API
        user_image_base64 = base64.b64encode(raw_user_bytes).decode("utf-8")
        user_image_format = user_image.content_type or "image/jpeg"
        user_image_url = f"data:{user_image_format};base64,{user_image_base64}"

        qa_messages = build_letter_writing_qa_messages(user_image_url)

        qa_chat_response = await openai_client.chat.completions.create(
            model=os.getenv("PRIMARY_MODEL") or "gpt-5.2-chat-latest",
            messages=qa_messages,
            response_format={"type": "json_object"}
        )

        # Initialize with default error response
        qa_response = WritingQAResponse(
            is_usable=False,
            confidence=0.0,
            reasons=["Error processing image"],
            capture_tips="Please ensure the image is clear and try again."
        )

        try:
            qa_response_content = qa_chat_response.choices[0].message.content
            qa_response_obj = json.loads(qa_response_content)
            qa_response = WritingQAResponse(
                is_usable=qa_response_obj["is_usable"],
                confidence=qa_response_obj["confidence"],
                reasons=qa_response_obj["reasons"],
                capture_tips=qa_response_obj["capture_tips"]
            )
        except Exception as e:
            print(f"QA error when checking letter joining: {e}")

        # If QA says the image is not good enough, we ask the user to retake their writing image
        if (not qa_response.is_usable) or qa_response.confidence < thresholds["baseline_qa_confidence"]:
            return WritingPhotoRetakeResponse(capture_tips=qa_response.capture_tips)

        joining_messages = build_letter_joining_messages(user_image_url, letter_list, target_word)

        joining_chat_response = await openai_client.chat.completions.create(
            model=os.getenv("PRIMARY_MODEL") or "gpt-5.2-chat-latest",
            messages=joining_messages,
            response_format={"type": "json_object"}
        )

        status = "fail"
        # Initialize with default error response
        joining_response = LetterJoiningResponse(
            status=status,
            scores=LetterJoiningScores(
                connection_accuracy=0.0,
                positional_forms=0.0,
                spacing_flow=0.0,
                baseline_consistency=0.0,
                dots_diacritics=0.0,
                overall=0.0
            ),
            feedback="An error occurred while evaluating your letter joining. Please try again.",
            mistake_tags=[],
            performance_reflection=""
        )

        try:
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
        except Exception as e:
            print(f"Error when parsing joining chat response: {e}")

        return joining_response


    async def check_dictation(self, user_image: UploadFile, target_word: str) -> Union[DictationResponse, WritingPhotoRetakeResponse]:
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

        raw_user_bytes = await user_image.read()

        # Getting image in the right format to be sent to OpenAI API
        user_image_base64 = base64.b64encode(raw_user_bytes).decode("utf-8")
        user_image_format = user_image.content_type or "image/jpeg"
        user_image_url = f"data:{user_image_format};base64,{user_image_base64}"

        qa_messages = build_letter_writing_qa_messages(user_image_url)

        qa_chat_response = await openai_client.chat.completions.create(
            model=os.getenv("PRIMARY_MODEL") or "gpt-5.2-chat-latest",
            messages=qa_messages,
            response_format={"type": "json_object"}
        )

        # Initialize with default error response
        qa_response = WritingQAResponse(
            is_usable=False,
            confidence=0.0,
            reasons=["Error processing image"],
            capture_tips="Please ensure the image is clear and try again."
        )

        try:
            qa_response_content = qa_chat_response.choices[0].message.content
            qa_response_obj = json.loads(qa_response_content)
            qa_response = WritingQAResponse(
                is_usable=qa_response_obj["is_usable"],
                confidence=qa_response_obj["confidence"],
                reasons=qa_response_obj["reasons"],
                capture_tips=qa_response_obj["capture_tips"]
            )
        except Exception as e:
            print(f"QA error when checking dictation: {e}")

        # If QA says the image is not good enough, we ask the user to retake their writing image
        if (not qa_response.is_usable) or qa_response.confidence < thresholds["baseline_qa_confidence"]:
            return WritingPhotoRetakeResponse(capture_tips=qa_response.capture_tips)

        dictation_messages = build_letter_dictation_messages(user_image_url, target_word)

        dictation_chat_response = await openai_client.chat.completions.create(
            model=os.getenv("PRIMARY_MODEL") or "gpt-5.2-chat-latest",
            messages=dictation_messages,
            response_format={"type": "json_object"}
        )

        status = "fail"
        # Initialize with default error response
        dictation_response = DictationResponse(
            status=status,
            detected_word="",
            scores=DictationScores(
                word_accuracy=0.0,
                letter_identity=0.0,
                joining_quality=0.0,
                legibility=0.0,
                dots_diacritics=0.0,
                baseline_spacing=0.0,
                overall=0.0
            ),
            feedback="An error occurred while evaluating your dictation. Please try again.",
            mistake_tags=[],
            performance_reflection=""
        )

        try:
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
        except Exception as e:
            print(f"Error when parsing dictation chat response: {e}")

        return dictation_response