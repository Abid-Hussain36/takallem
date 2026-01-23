from typing import Union
from app.models.db.lecture.info_lecture_response import InfoLectureResponse
from app.models.db.lecture.letter_speaking_lecture_response import LetterSpeakingLectureResponse
from app.models.db.lecture.letter_writing_lecture_response import LetterWritingLectureResponse
from app.models.db.lecture.vocab_lecture_response import VocabLectureResponse
from app.models.db.general_resource.dialect_selection_response import DialectSelectionResponse
from app.models.db.problem.letter_pronounciation_problem_response import LetterPronounciationProblemResponse
from app.models.db.problem_set.word_pronounciation_problem_set_response import WordPronounciationProblemSetResponse
from app.models.db.problem_set.discrimination_problem_set_response import DiscriminationProblemSetResponse
from app.models.db.problem_set.letter_recognition_problem_set_response import LetterRecognitionProblemSetResponse
from app.models.db.problem_set.letter_writing_problem_set_response import LetterWritingProblemSetResponse
from app.models.db.problem_set.letter_joining_problem_set_response import LetterJoiningProblemSetResponse
from app.models.db.problem_set.dictation_problem_set_response import DictationProblemSetResponse
from app.models.db.problem_set.vocab_reading_problem_sets_response import VocabReadingProblemSetsResponse
from app.models.db.problem_set.vocab_listening_problem_sets_response import VocabListeningProblemSetsResponse
from app.models.db.problem_set.vocab_speaking_problem_sets_response import VocabSpeakingProblemSetsResponse
from app.models.db.problem_set.reading_comprehension_writing_problem_set_response import ReadingComprehensionWritingProblemSetResponse
from app.models.db.general_resource.resource_response import ResourceResponse
from app.models.db.problem_set.reading_comprehension_mcq_problem_set_response import ReadingComprehensionMCQProblemSetResponse

# Union of all polymorphic resource types (excluding UNIT_TEST and FINAL_EXAM)
PolymorphicResource = Union[
    # Lecture Types
    InfoLectureResponse,
    LetterSpeakingLectureResponse,
    LetterWritingLectureResponse,
    VocabLectureResponse,
    # General Resources
    DialectSelectionResponse,
    # Problem Set Types
    LetterPronounciationProblemResponse,
    WordPronounciationProblemSetResponse,
    DiscriminationProblemSetResponse,
    LetterRecognitionProblemSetResponse,
    LetterWritingProblemSetResponse,
    LetterJoiningProblemSetResponse,
    DictationProblemSetResponse,
    VocabReadingProblemSetsResponse,
    VocabListeningProblemSetsResponse,
    VocabSpeakingProblemSetsResponse,
    ReadingComprehensionMCQProblemSetResponse,
    ReadingComprehensionWritingProblemSetResponse,
    ResourceResponse
]