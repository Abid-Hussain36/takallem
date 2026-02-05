export interface PronounciationScores{
    accuracy: number;
    completeness: number;
    overall: number;
}


export interface SemanticEvaluation{
    vocab_words_used: string[];
    answer_makes_sense: boolean;
    grammatical_score: number;
    grammar_notes: string;
}