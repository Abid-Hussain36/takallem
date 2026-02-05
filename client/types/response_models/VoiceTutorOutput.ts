import { PronounciationScores, SemanticEvaluation } from "../general/SpeakingScores";

export interface VoiceTutorOutput{
    transcription: string;
    pronounciation_scores: PronounciationScores;
    semantic_evaluation: SemanticEvaluation;
    status: string;
    performance_reflection: string;
    feedback_text: string | null;
    feedback_audio_base64: string | null;
}