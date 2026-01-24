export interface LetterHandwritingScores {
    legibility: number;
    form_accuracy: number;
    dots_diacritics: number;
    baseline_proportion: number;
    overall: number;
}

export interface LetterWritingResponse {
    status: "pass" | "fail";
    scores: LetterHandwritingScores;
    feedback: string;
    mistake_tags: string[];
    performance_reflection: string;
}

export interface LetterJoiningScores {
    connection_accuracy: number;
    positional_forms: number;
    spacing_flow: number;
    baseline_consistency: number;
    dots_diacritics: number;
    overall: number;
}

export interface LetterJoiningResponse {
    status: "pass" | "fail";
    scores: LetterJoiningScores;
    feedback: string;
    mistake_tags: string[];
    performance_reflection: string;
}

export interface DictationScores {
    word_accuracy: number;
    letter_identity: number;
    joining_quality: number;
    legibility: number;
    dots_diacritics: number;
    baseline_spacing: number;
    overall: number;
}

export interface DictationResponse {
    status: "pass" | "fail";
    detected_word: string;
    scores: DictationScores;
    feedback: string;
    mistake_tags: string[];
    performance_reflection: string;
}

export interface WritingPhotoRetakeResponse {
    capture_tips: string;
}
