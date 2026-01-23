from app.db.enums import ResourceType
from typing import Type
from app.db.schemas.resource import Resource

# Import all resource schema classes
from app.db.schemas.info_lecture import InfoLecture
from app.db.schemas.letter_speaking_lecture import LetterSpeakingLecture
from app.db.schemas.letter_writing_lecture import LetterWritingLecture
from app.db.schemas.vocab_lecture import VocabLecture
from app.db.schemas.dialect_selection import DialectSelection
from app.db.schemas.letter_pronounciation_problem import LetterPronounciationProblem
from app.db.schemas.word_pronounciation_problem_set import WordPronounciationProblemSet
from app.db.schemas.discrimination_problem_set import DiscriminationProblemSet
from app.db.schemas.letter_recognition_problem_set import LetterRecognitionProblemSet
from app.db.schemas.letter_writing_problem_set import LetterWritingProblemSet
from app.db.schemas.letter_joining_problem_set import LetterJoiningProblemSet
from app.db.schemas.dictation_problem_set import DictationProblemSet
from app.db.schemas.vocab_reading_problem_sets import VocabReadingProblemSets
from app.db.schemas.vocab_listening_problem_sets import VocabListeningProblemSets
from app.db.schemas.vocab_speaking_problem_sets import VocabSpeakingProblemSets
from app.db.schemas.reading_comprehension_mcq_problem_set import ReadingComprehensionMCQProblemSet
from app.db.schemas.reading_comprehension_writing_problem_set import ReadingComprehensionWritingProblemSet


# Maps ResourceType enum values to their corresponding database table names
# Used for querying specific resource subclasses from the polymorphic Resource table
RESOURCE_TYPE_TO_TABLE: dict[ResourceType, str] = {
    # Lecture Types
    ResourceType.INFO_LECTURE: "info_lectures",
    ResourceType.LETTER_SPEAKING_LECTURE: "letter_speaking_lectures",
    ResourceType.LETTER_WRITING_LECTURE: "letter_writing_lectures",
    ResourceType.VOCAB_LECTURE: "vocab_lectures",
    
    # General Resources
    ResourceType.DIALECT_SELECTION: "dialect_selections",
    
    # Problem Set Types
    ResourceType.LETTER_PRONOUNCIATION_PROBLEM: "letter_pronounciation_problems",
    ResourceType.WORD_PRONOUNCIATION_PROBLEM_SET: "word_pronounciation_problem_sets",
    ResourceType.DISCRIMINATION_PROBLEM_SET: "discrimination_problem_sets",
    ResourceType.LETTER_RECOGNITION_PROBLEM_SET: "letter_recognition_problem_sets",
    ResourceType.LETTER_WRITING_PROBLEM_SET: "letter_writing_problem_sets",
    ResourceType.LETTER_JOINING_PROBLEM_SET: "letter_joining_problem_sets",
    ResourceType.DICTATION_PROBLEM_SET: "dictation_problem_sets",
    ResourceType.VOCAB_READING_PROBLEM_SETS: "vocab_reading_problem_sets_collection",
    ResourceType.VOCAB_LISTENING_PROBLEM_SETS: "vocab_listening_problem_sets_collection",
    ResourceType.VOCAB_SPEAKING_PROBLEM_SETS: "vocab_speaking_problem_sets_collection",
    ResourceType.READING_COMPREHENSION_MCQ_PROBLEM_SET: "reading_comprehension_mcq_problem_sets",
    ResourceType.READING_COMPREHENSION_WRITING_PROBLEM_SET: "reading_comprehension_writing_problem_sets",
    
    # Note: UNIT_TEST and FINAL_EXAM are intentionally excluded
}


# Maps ResourceType enum values to their corresponding SQLAlchemy model classes
# Used for type-specific queries and eager loading
RESOURCE_TYPE_TO_CLASS: dict[ResourceType, Type[Resource]] = {
    # Lecture Types
    ResourceType.INFO_LECTURE: InfoLecture,
    ResourceType.LETTER_SPEAKING_LECTURE: LetterSpeakingLecture,
    ResourceType.LETTER_WRITING_LECTURE: LetterWritingLecture,
    ResourceType.VOCAB_LECTURE: VocabLecture,
    
    # General Resources
    ResourceType.DIALECT_SELECTION: DialectSelection,
    
    # Problem Set Types
    ResourceType.LETTER_PRONOUNCIATION_PROBLEM: LetterPronounciationProblem,
    ResourceType.WORD_PRONOUNCIATION_PROBLEM_SET: WordPronounciationProblemSet,
    ResourceType.DISCRIMINATION_PROBLEM_SET: DiscriminationProblemSet,
    ResourceType.LETTER_RECOGNITION_PROBLEM_SET: LetterRecognitionProblemSet,
    ResourceType.LETTER_WRITING_PROBLEM_SET: LetterWritingProblemSet,
    ResourceType.LETTER_JOINING_PROBLEM_SET: LetterJoiningProblemSet,
    ResourceType.DICTATION_PROBLEM_SET: DictationProblemSet,
    ResourceType.VOCAB_READING_PROBLEM_SETS: VocabReadingProblemSets,
    ResourceType.VOCAB_LISTENING_PROBLEM_SETS: VocabListeningProblemSets,
    ResourceType.VOCAB_SPEAKING_PROBLEM_SETS: VocabSpeakingProblemSets,
    ResourceType.READING_COMPREHENSION_MCQ_PROBLEM_SET: ReadingComprehensionMCQProblemSet,
    ResourceType.READING_COMPREHENSION_WRITING_PROBLEM_SET: ReadingComprehensionWritingProblemSet,
}
