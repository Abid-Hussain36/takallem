import { AvailableDialect, AvailableLanguage } from "../enums";
import { PronounciationScores, SemanticEvaluation } from "../general/SpeakingScores";
import { VocabWordResponse } from "../response_models/ResourceResponse";

export interface VoiceTutorExplainInput{
    query: string;
    question: string;
    language: AvailableLanguage;
    dialect: AvailableDialect | null;
    vocab_words: VocabWordResponse[];
    transcription: string;
    pronounciation_scores: PronounciationScores;
    semantic_evaluation: SemanticEvaluation;
    status: string;
    performance_reflection: string;
    previous_feedback: string[];
}