export interface VoiceTutorOutput{
    status: string;
    feedback_text: string;
    feedback_audio: string | null;
}