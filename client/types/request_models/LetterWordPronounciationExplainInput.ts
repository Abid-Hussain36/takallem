export interface LetterWordPronounciationExplainInput{
    query: string;
    word: string;
    status: string;
    transcription: string;
    previous_feedback: string[];
    mistake_tags: string[];
    performance_reflection: string;
}
