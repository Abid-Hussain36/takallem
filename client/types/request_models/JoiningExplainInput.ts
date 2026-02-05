import { AvailableDialect, AvailableLanguage } from "../enums";
import { LetterJoiningScores } from "../response_models/LetterWritingResponse";

export interface JoiningExplainInput {
    query: string;
    language: AvailableLanguage;
    dialect: AvailableDialect | null;
    letter_list: string[];
    target_word: string;
    status: string;
    scores: LetterJoiningScores;
    previous_feedback: string[];
    mistake_tags: string[];
    performance_reflection: string;
}
