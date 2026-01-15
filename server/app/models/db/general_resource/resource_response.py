from pydantic import BaseModel, Field
from typing import Union
from app.db.enums import ResourceType

# Import all specific resource response types
from app.models.db.lecture.info_lecture_response import InfoLectureResponse
from app.models.db.lecture.letter_speaking_lecture_response import LetterSpeakingLectureResponse
from app.models.db.lecture.letter_writing_lecture_response import LetterWritingLectureResponse
from app.models.db.lecture.vocab_lecture_response import VocabLectureResponse
from app.models.db.general_resource.dialect_selection_response import DialectSelectionResponse
from app.models.db.problem.letter_pronounciation_problem_response import LetterPronounciationProblemResponse
from app.models.db.problem_set.word_pronounciation_problem_set_response import WordPronounciationProblemSetResponse
from app.models.db.problem_set.letter_recognition_problem_set_response import LetterRecognitionProblemSetResponse
from app.models.db.problem_set.letter_writing_problem_set_response import LetterWritingProblemSetResponse
from app.models.db.problem_set.vocab_reading_problem_sets_response import VocabReadingProblemSetsResponse
from app.models.db.problem_set.vocab_listening_problem_sets_response import VocabListeningProblemSetsResponse
from app.models.db.problem_set.vocab_speaking_problem_sets_response import VocabSpeakingProblemSetsResponse


# Base ResourceResponse for cases where we only have basic resource info
class ResourceResponse(BaseModel):
    id: int
    resource_type: ResourceType


# Union type for all possible polymorphic resource types
# Using discriminated union for better Pydantic v2 support
PolymorphicResource = Union[
    InfoLectureResponse,
    LetterSpeakingLectureResponse,
    LetterWritingLectureResponse,
    VocabLectureResponse,
    DialectSelectionResponse,
    LetterPronounciationProblemResponse,
    WordPronounciationProblemSetResponse,
    LetterRecognitionProblemSetResponse,
    LetterWritingProblemSetResponse,
    VocabReadingProblemSetsResponse,
    VocabListeningProblemSetsResponse,
    VocabSpeakingProblemSetsResponse,
    ResourceResponse  # Fallback for unknown types
]

