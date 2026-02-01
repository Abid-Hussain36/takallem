import { ResourceType, AvailableCourse, AvailableDialect, Gender } from "../enums";

// ===== NESTED RESPONSE TYPES =====

// Vocab Word Response
export interface VocabWordResponse {
    id: number;
    lecture_id: number;
    number: number;
    word: string;
    meaning: string;
    course: AvailableCourse;
    language: string;
    dialect: string | null;
    vocab_audio: string;
}

// Letter Writing Sequence Response
export interface LetterWritingSequenceResponse {
    id: number;
    lecture_id: number;
    problem_id: number;
    position: string;
    sequence_images: string[];
}

// Dialect Response
export interface DialectResponse {
    id: number;
    dialect: AvailableDialect;
    image: string;
    text_color: string;
}

// Problem Responses
export interface VocabReadingProblemResponse {
    id: number;
    problem_set_id: number;
    vocab_word_id: number;
    answer_choices: string[];
    vocab_word: VocabWordResponse;
}

export interface VocabListeningProblemResponse {
    id: number;
    problem_set_id: number;
    vocab_word_id: number;
    answer_choices: string[];
    vocab_word: VocabWordResponse;
}

export interface VocabSpeakingProblemResponse {
    id: number;
    problem_set_id: number;
    question: string;
    vocab_words: VocabWordResponse[];
}

export interface LetterWritingProblemResponse {
    id: number;
    problem_set_id: number;
    letter: string;
    position: string;
    reference_writing: string;
    writing_sequence: LetterWritingSequenceResponse;
}

export interface LetterJoiningProblemResponse {
    id: number;
    problem_set_id: number;
    word: string;
    letter_list: string[];
}

export interface LetterRecognitionProblemResponse {
    id: number;
    problem_set_id: number;
    word: string;
    answer_choices: string[];
    correct_answer: string;
}

export interface WordPronounciationProblemResponse {
    id: number;
    problem_set_id: number;
    question: string;
    word: string;
    word_audio: string;
}

export interface DictationProblemResponse {
    id: number;
    problem_set_id: number;
    word: string;
    word_audio: string;
}

export interface DiscriminationProblemResponse {
    id: number;
    problem_set_id: number;
    word_audio: string;
    incorrect_word_audio: string;
    answer_choices: string[];
    correct_answer: string;
}

// Problem Set Responses
export interface VocabReadingProblemSetResponse {
    id: number;
    set_number: number;
    problem_count: number;
    problems: VocabReadingProblemResponse[];
}

export interface VocabListeningProblemSetResponse {
    id: number;
    set_number: number;
    problem_count: number;
    problems: VocabListeningProblemResponse[];
}

export interface VocabSpeakingProblemSetResponse {
    id: number;
    problem_count: number;
    gender: Gender;
    problems: VocabSpeakingProblemResponse[];
}

// ===== RESOURCE TYPES (Polymorphic) =====

// Base Resource interface
export interface BaseResource {
    id: number;
    resource_type: ResourceType;
}

// Lecture Types
export interface InfoLectureResponse extends BaseResource {
    resource_type: ResourceType.INFO_LECTURE;
    content: string[];
}

export interface LetterSpeakingLectureResponse extends BaseResource {
    resource_type: ResourceType.LETTER_SPEAKING_LECTURE;
    letter: string;
    content: string[];
    letter_audio: string;
    word_audios: string[];
}

export interface LetterWritingLectureResponse extends BaseResource {
    resource_type: ResourceType.LETTER_WRITING_LECTURE;
    letter: string;
    content: string[];
    letter_writing_sequences: LetterWritingSequenceResponse[];
}

export interface VocabLectureResponse extends BaseResource {
    resource_type: ResourceType.VOCAB_LECTURE;
    vocab_words: VocabWordResponse[];
}

// Problem Set Resources
export interface LetterPronounciationProblemResponse extends BaseResource {
    resource_type: ResourceType.LETTER_PRONOUNCIATION_PROBLEM;
    problem_count: number;
    question: string;
    letter: string;
    letter_audio: string;
}

export interface WordPronounciationProblemSetResponse extends BaseResource {
    resource_type: ResourceType.WORD_PRONOUNCIATION_PROBLEM_SET;
    problem_count: number;
    problems: WordPronounciationProblemResponse[];
}

export interface LetterRecognitionProblemSetResponse extends BaseResource {
    resource_type: ResourceType.LETTER_RECOGNITION_PROBLEM_SET;
    problem_count: number;
    problems: LetterRecognitionProblemResponse[];
}

export interface LetterWritingProblemSetResponse extends BaseResource {
    resource_type: ResourceType.LETTER_WRITING_PROBLEM_SET;
    problem_count: number;
    problems: LetterWritingProblemResponse[];
}

export interface LetterJoiningProblemSetResponse extends BaseResource {
    resource_type: ResourceType.LETTER_JOINING_PROBLEM_SET;
    problem_count: number;
    problems: LetterJoiningProblemResponse[];
}

export interface DictationProblemSetResponse extends BaseResource {
    resource_type: ResourceType.DICTATION_PROBLEM_SET;
    problem_count: number;
    problems: DictationProblemResponse[];
}

export interface DiscriminationProblemSetResponse extends BaseResource {
    resource_type: ResourceType.DISCRIMINATION_PROBLEM_SET;
    problem_count: number;
    problems: DiscriminationProblemResponse[];
}

export interface VocabReadingProblemSetsResponse extends BaseResource {
    resource_type: ResourceType.VOCAB_READING_PROBLEM_SETS;
    set_limit: number;
    dialect?: AvailableDialect | null;
    problem_sets: VocabReadingProblemSetResponse[];
}

export interface VocabListeningProblemSetsResponse extends BaseResource {
    resource_type: ResourceType.VOCAB_LISTENING_PROBLEM_SETS;
    set_limit: number;
    dialect?: AvailableDialect | null;
    problem_sets: VocabListeningProblemSetResponse[];
}

export interface VocabSpeakingProblemSetsResponse extends BaseResource {
    resource_type: ResourceType.VOCAB_SPEAKING_PROBLEM_SETS;
    set_limit: number;
    dialect?: AvailableDialect | null;
    problem_sets: VocabSpeakingProblemSetResponse[];
}

// General Resources
export interface DialectSelectionResponse extends BaseResource {
    resource_type: ResourceType.DIALECT_SELECTION;
    dialects: DialectResponse[];
}

// Union type for all possible resources (discriminated union)
export type PolymorphicResource = 
    | InfoLectureResponse
    | LetterSpeakingLectureResponse
    | LetterWritingLectureResponse
    | VocabLectureResponse
    | LetterPronounciationProblemResponse
    | WordPronounciationProblemSetResponse
    | LetterRecognitionProblemSetResponse
    | LetterWritingProblemSetResponse
    | LetterJoiningProblemSetResponse
    | DictationProblemSetResponse
    | DiscriminationProblemSetResponse
    | VocabReadingProblemSetsResponse
    | VocabListeningProblemSetsResponse
    | VocabSpeakingProblemSetsResponse
    | DialectSelectionResponse
    | BaseResource;  // Fallback for unknown types

export interface CachedResource{
    course: AvailableCourse;
    unit: string;
    section: string;
    title: string;
    number: number;
    resource: PolymorphicResource | null;
}
