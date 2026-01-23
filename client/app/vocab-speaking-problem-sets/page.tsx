import { useResource } from "@/context/ResourceContext"
import { useUserCourseProgress } from "@/context/UserCourseProgressContext";
import { VocabSpeakingProblemSetsResponse } from "@/types/response_models/ResourceResponse";
import { useRouter } from "next/navigation";
import { useState } from "react";

type ProgressStatus = 'unanswered' | 'current' | 'correct' | 'incorrect';

const VocabSpeakingProblemSets = () => {
    const router = useRouter();

    const {userCourseProgress, setUserCourseProgress} = useUserCourseProgress();
    const {resource, setResource} = useResource();
    
    const [isLoading, setIsLoading] = useState<boolean>(false);
    const [error, setError] = useState<string>("");
    const [currProblemIdx, setCurrProblemIdx] = useState<number>(0);
    const [progressStatus, setProgressStatus] = useState<ProgressStatus[]>([]);
    const [selectedAnswer, setSelectedAnswer] = useState<string | null>(null);
    const [answered, setAnswered] = useState<boolean>(false);
    const [showConfetti, setShowConfetti] = useState<boolean>(false);

    if (!resource || !resource.resource) {
        return <div>Loading vocabulary problems...</div>;
    }

    // UserCourseProgress Fields
    const currVPS: number = userCourseProgress!.current_vocab_problem_set;
    const problemCounter: number = userCourseProgress!.problem_counter;
    
    // VocabSpeakingSets Data
    const vocabSpeakingProblemSetsData = resource.resource as VocabSpeakingProblemSetsResponse;
    const problemSetLimit = vocabSpeakingProblemSetsData.set_limit;
    const vocabSpeakingProblemSetData = vocabSpeakingProblemSetsData.problem_sets[currVPS - 1];
    const problems = vocabSpeakingProblemSetData.problems;
    const problem = problems[0];
    const question: string = problem.question;
    const vocabWords = problem.vocab_words;
    
    // Stopping Variables
    const vocabSpeakingProblemSetLength = vocabSpeakingProblemSetData.problem_count;
    const problemCounterStop = vocabSpeakingProblemSetLength * 2;

    // End Booleans
    const atSetEnd = currProblemIdx === problems.length - 1;
    const exerciseComplete = problemCounter === problemCounterStop;

    return(
        <h1>Vocab Speaking Problem Sets</h1>
    );
}

export default VocabSpeakingProblemSets;
