import { ResourceType } from "../enums";

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
    letter_writing_sequences: any[];  // Can be expanded with LetterWritingSequenceResponse
}

export interface VocabLectureResponse extends BaseResource {
    resource_type: ResourceType.VOCAB_LECTURE;
    vocab_words: any[];  // Can be expanded with VocabWordResponse
}

// Problem Sets
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
    problems: any[];  // Can be expanded with WordPronounciationProblemResponse
}

export interface LetterRecognitionProblemSetResponse extends BaseResource {
    resource_type: ResourceType.LETTER_RECOGNITION_PROBLEM_SET;
    problem_count: number;
    problems: any[];  // Can be expanded with LetterRecognitionProblemResponse
}

export interface LetterWritingProblemSetResponse extends BaseResource {
    resource_type: ResourceType.LETTER_WRITING_PROBLEM_SET;
    problem_count: number;
    problems: any[];  // Can be expanded with LetterWritingProblemResponse
}

export interface VocabReadingProblemSetsResponse extends BaseResource {
    resource_type: ResourceType.VOCAB_READING_PROBLEM_SETS;
    set_limit: number;
    problem_sets: any[];  // Can be expanded with VocabReadingProblemSetResponse
}

export interface VocabListeningProblemSetsResponse extends BaseResource {
    resource_type: ResourceType.VOCAB_LISTENING_PROBLEM_SETS;
    set_limit: number;
    problem_sets: any[];  // Can be expanded with VocabListeningProblemSetResponse
}

export interface VocabSpeakingProblemSetsResponse extends BaseResource {
    resource_type: ResourceType.VOCAB_SPEAKING_PROBLEM_SETS;
    problem_sets: any[];  // Can be expanded with VocabSpeakingProblemSetResponse
}

// General Resources
export interface DialectSelectionResponse extends BaseResource {
    resource_type: ResourceType.DIALECT_SELECTION;
    dialects: any[];  // Can be expanded with DialectResponse
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
    | VocabReadingProblemSetsResponse
    | VocabListeningProblemSetsResponse
    | VocabSpeakingProblemSetsResponse
    | DialectSelectionResponse
    | BaseResource;  // Fallback for unknown types
