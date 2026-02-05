import { AvailableDialect, AvailableLanguage } from "../enums";
import { DictationScores } from "../response_models/LetterWritingResponse";

export interface DictationExplainInput {
    query: string;
    language: AvailableLanguage;
    dialect: AvailableDialect | null;
    target_word: string;
    status: string;
    scores: DictationScores;
    previous_feedback: string[];
    mistake_tags: string[];
    performance_reflection: string;
}
