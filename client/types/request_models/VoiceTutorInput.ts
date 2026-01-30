import { AvailableDialect, AvailableLanguage } from "../enums";
import { VocabWordResponse } from "../response_models/ResourceResponse";

export interface VoiceTutorInput {
    question: string;
    language: AvailableLanguage;
    dialect: AvailableDialect | null;
    vocab_words: VocabWordResponse[];
    user_audio_base64: string;
}