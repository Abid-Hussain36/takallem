import { AvailableDialect, AvailableLanguage } from "../enums";
import { LetterHandwritingScores } from "../response_models/LetterWritingResponse";

export interface WritingExplainInput {
    query: string;
    language: AvailableLanguage;
    dialect: AvailableDialect | null;
    letter: string;
    position: string | null;
    status: string;
    scores: LetterHandwritingScores;
    previous_feedback: string[];
    mistake_tags: string[];
    performance_reflection: string;
}
