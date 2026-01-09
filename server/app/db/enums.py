import enum


class AvailableLanguage(str, enum.Enum):
    ARABIC = "Arabic"
    SPANISH = "Spanish"
    FRENCH = "French"


class AvailableDialect(str, enum.Enum):
    MSA = "MSA"
    LEVANTINE = "Levantine"
    EGYPTIAN = "Egyptian"


class AvailableCourse(str, enum.Enum):
    BEGINNER_ARABIC = "Beginner Arabic"
    INTERMEDIATE_ARABIC = "Intermediate Arabic"
    ADVANCED_ARABIC = "Advanced Arabic"


class ResourceType(str, enum.Enum):
    # Lecture Types
    LETTER_SPEAKING_LECTURE = "Letter Speaking Lecture"
    LETTER_WRITING_LECTURE = "Letter Writing Lecture"
    VOCAB_LECTURE = "Vocab Lecture"
    INFO_LECTURE = "Info Lecture"

    # General Resources
    READING_COMPREHENSION_TEXT = "Reading Comprehension Text"
    VOCAB_WORD = "Vocab Word"

    # Problem Set Types
    LETTER_PRONOUNCIATION_PROBLEM = "Letter Pronounciation Problem"
    WORD_PRONOUNCIATION_PROBLEM_SET = "Word Pronounciation Problem Set"
    DISCRIMINATION_PROBLEM_SET = "Discrimination Problem Set"
    LETTER_RECOGNITION_PROBLEM_SET = "Letter Recognition Problem Set"
    LETTER_WRITING_PROBLEM_SET = "Letter Writing Problem Set"
    LETTER_JOINING_PROBLEM_SET = "Letter Joining Problem Set"
    DICTATION_PROBLEM_SET = "Dictation Problem Set"
    VOCAB_READING_PROBLEM_SET = "Vocab Reading Problem Set"
    VOCAB_LISTENING_PROBLEM_SET = "Vocab Listening Problem Set"
    VOCAB_SPEAKING_PROBLEM_SET = "Vocab Speaking Problem Set"
    READING_COMPREHENSION_MCQ_PROBLEM_SET = "Reading Comprehension MCQ Problem Set"
    READING_COMPREHENSION_WRITING_PROBLEM_SET = "Reading Comprehension Writing Problem Set"

    # Unit Test
    UNIT_TEST = "Unit Test"
    FINAL_EXAM = "Final Exam"