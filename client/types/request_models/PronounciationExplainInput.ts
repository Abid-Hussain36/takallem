import { AvailableDialect, AvailableLanguage } from "../enums";

export interface PronounciationExplainInput {
    query: string;
    language: AvailableLanguage;
    dialect: AvailableDialect | null;
    phrase: string;
    status: string;
    transcription: string;
    previous_feedback: string[];
    mistake_tags: string[];
    performance_reflection: string;
}
