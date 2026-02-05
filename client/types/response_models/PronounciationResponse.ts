export interface PronounciationResponse {
    status: string;
    transcription: string;
    feedback: string;
    mistake_tags: string[];
    performance_reflection: string;
}
