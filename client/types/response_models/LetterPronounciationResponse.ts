export interface LetterPronounciationResponse {
    status: string;
    transcription: string;
    feedback: string;
    mistake_tags: string[];
    performance_reflection: string
}