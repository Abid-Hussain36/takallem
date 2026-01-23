import { useResource } from "@/context/ResourceContext"
import { useUserCourseProgress } from "@/context/UserCourseProgressContext";
import { VocabListeningProblemSetsResponse } from "@/types/response_models/ResourceResponse";
import AddCoveredWordRequest from "@/types/request_models/AddCoveredWordRequest";
import { useRouter } from "next/navigation";
import { useState, useEffect, useRef } from "react";
import IncrementCurrentVocabProblemSetRequest from "@/types/request_models/IncrementCurrentVocabProblemSetRequest";
import styles from './VocabListeningProblemSets.module.css';

type ProgressStatus = 'unanswered' | 'current' | 'correct' | 'incorrect';

const VocabListeningProblemSets = () => {
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
    const [isPlaying, setIsPlaying] = useState<boolean>(false);

    const audioRef = useRef<HTMLAudioElement | null>(null);

    if (!resource || !resource.resource) {
        return (
            <div className={styles.loading}>
                <div className={styles.spinner}></div>
                <p className={styles.loadingText}>Loading vocabulary problems...</p>
            </div>
        );
    }

    // UserCourseProgress Fields
    const currVPS: number = userCourseProgress!.current_vocab_problem_set;
    const problemCounter: number = userCourseProgress!.problem_counter;
    
    // VocabListeningSets Data
    const vocabListeningProblemSetsData = resource.resource as VocabListeningProblemSetsResponse;
    const problemSetLimit = vocabListeningProblemSetsData.set_limit;
    const vocabListeningProblemSetData = vocabListeningProblemSetsData.problem_sets[currVPS - 1];
    const problems = vocabListeningProblemSetData.problems;
    const problem = problems[currProblemIdx];
    const answerChoices: string[] = problem.answer_choices;
    const correctAnswer: string = problem.vocab_word.word;
    const audioUrl: string = problem.vocab_word.vocab_audio;
    
    // Stopping Variables
    const vocabListeningProblemSetLength = vocabListeningProblemSetData.problem_count;
    const problemCounterStop = vocabListeningProblemSetLength * 2;

    // End Booleans
    const atSetEnd = currProblemIdx === problems.length - 1;
    const exerciseComplete = problemCounter === problemCounterStop;

    // Initialize progress status when component mounts or problem set changes
    useEffect(() => {
        const initialStatus: ProgressStatus[] = problems.map((_, idx) => 
            idx === 0 ? 'current' : 'unanswered'
        );
        setProgressStatus(initialStatus);
        setCurrProblemIdx(0);
        setSelectedAnswer(null);
        setAnswered(false);
        setIsPlaying(false);
    }, [currVPS]);

    // Update current problem indicator
    useEffect(() => {
        if (progressStatus.length > 0 && !answered) {
            const newStatus = [...progressStatus];
            newStatus[currProblemIdx] = 'current';
            setProgressStatus(newStatus);
        }
    }, [currProblemIdx, answered]);

    // Handle audio playback
    const handlePlayAudio = () => {
        if (audioRef.current) {
            if (isPlaying) {
                audioRef.current.pause();
                setIsPlaying(false);
            } else {
                audioRef.current.play();
                setIsPlaying(true);
            }
        }
    };

    // Audio event listeners
    useEffect(() => {
        const audio = audioRef.current;
        if (!audio) return;

        const handleAudioEnd = () => {
            setIsPlaying(false);
        };

        const handleAudioPlay = () => {
            setIsPlaying(true);
        };

        const handleAudioPause = () => {
            setIsPlaying(false);
        };

        audio.addEventListener('ended', handleAudioEnd);
        audio.addEventListener('play', handleAudioPlay);
        audio.addEventListener('pause', handleAudioPause);

        return () => {
            audio.removeEventListener('ended', handleAudioEnd);
            audio.removeEventListener('play', handleAudioPlay);
            audio.removeEventListener('pause', handleAudioPause);
        };
    }, [audioRef.current]);

    // Stop audio when moving to next problem
    useEffect(() => {
        if (audioRef.current) {
            audioRef.current.pause();
            audioRef.current.currentTime = 0;
            setIsPlaying(false);
        }
    }, [currProblemIdx, currVPS]);
    
    const handleChoiceSelection = async (choice: string) => {
        if (answered) return; // Prevent multiple clicks

        setSelectedAnswer(choice);
        setAnswered(true);

        const isCorrect = choice === correctAnswer;

        // Update progress bar
        const newStatus = [...progressStatus];
        newStatus[currProblemIdx] = isCorrect ? 'correct' : 'incorrect';
        setProgressStatus(newStatus);

        if(isCorrect){
            // Show confetti effect
            setShowConfetti(true);
            setTimeout(() => setShowConfetti(false), 1000);

            // Correct Answer - add to covered words and increment counter
            const authToken = localStorage.getItem("token");

            try {
                const addToCoveredWordsRequest: AddCoveredWordRequest = {
                    id: userCourseProgress!.id,
                    word: choice
                }
                
                const addToCoveredWordsResponse = await fetch(
                    `${process.env.NEXT_PUBLIC_SERVER_URL}/user-course-progress/covered_words`,
                    {
                        method: "PUT",
                        headers: {
                            'Authorization': `Bearer ${authToken}`,
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify(addToCoveredWordsRequest)
                    }
                )

                if(!addToCoveredWordsResponse.ok){
                    const errorData = await addToCoveredWordsResponse.json();
                    throw new Error(errorData.detail || "Failed to add to covered words")
                }

                const isWordAddedJson = await addToCoveredWordsResponse.json();
                const isWordAdded = isWordAddedJson.coveredWordAdded;

                if(isWordAdded){
                    const incrementProblemCounterResponse = await fetch(
                        `${process.env.NEXT_PUBLIC_SERVER_URL}/user-course-progress/problem_counter/increment/${userCourseProgress!.id}`,
                        {
                            method: "PUT",
                            headers: {
                                'Authorization': `Bearer ${authToken}`,
                                'Content-Type': 'application/json'
                            },
                        }
                    )
    
                    if(!incrementProblemCounterResponse.ok){
                        const errorData = await incrementProblemCounterResponse.json();
                        throw new Error(errorData.detail || "Failed to add to increment problem counter")
                    }
    
                    const updatedUserCourseProgress = await incrementProblemCounterResponse.json();
                    setUserCourseProgress(updatedUserCourseProgress);
                }
            } catch(err){
                setError(err instanceof Error ? err.message : "Error in handling correct user answer selection.");
            } finally{
                setIsLoading(false);
            }
        }
    }

    const handleNext = async () => {
        if(atSetEnd && exerciseComplete){
            setIsLoading(true);
            const authToken = localStorage.getItem("token");

            try {
                // 1. Reset Problem Counter
                const clearProblemCounterResponse = await fetch(
                    `${process.env.NEXT_PUBLIC_SERVER_URL}/user-course-progress/problem_counter/clear/${userCourseProgress!.id}`,
                    {
                        method: "PUT",
                        headers: {
                            'Authorization': `Bearer ${authToken}`,
                            'Content-Type': 'application/json'
                        }
                    }
                );

                if(!clearProblemCounterResponse.ok){
                    const errorData = await clearProblemCounterResponse.json();
                    throw new Error(errorData.detail || "Failed to reset problem counter")
                }

                // 2. Reset Covered Words
                const clearCoveredWordsResponse = await fetch(
                    `${process.env.NEXT_PUBLIC_SERVER_URL}/user-course-progress/covered_words/clear/${userCourseProgress!.id}`,
                    {
                        method: "PUT",
                        headers: {
                            'Authorization': `Bearer ${authToken}`,
                            'Content-Type': 'application/json'
                        }
                    }
                );

                if(!clearCoveredWordsResponse.ok){
                    const errorData = await clearCoveredWordsResponse.json();
                    throw new Error(errorData.detail || "Failed to reset covered words")
                }

                // 3. Reset Set Counter
                const clearSetCounterResponse = await fetch(
                    `${process.env.NEXT_PUBLIC_SERVER_URL}/user-course-progress/current_vocab_problem_set/clear/${userCourseProgress!.id}`,
                    {
                        method: "PUT",
                        headers: {
                            'Authorization': `Bearer ${authToken}`,
                            'Content-Type': 'application/json'
                        }
                    }
                );

                if(!clearSetCounterResponse.ok){
                    const errorData = await clearSetCounterResponse.json();
                    throw new Error(errorData.detail || "Failed to reset set counter")
                }

                // 4. Increment current module if necessary
                if(userCourseProgress?.curr_module === resource.number){
                    const incrementUserCourseProgress = await fetch(
                        `${process.env.NEXT_PUBLIC_SERVER_URL}/user-course-progress/curr_module/increment/${userCourseProgress.id}`,
                        {
                            method: "PUT",
                            headers: {
                                'Authorization': `Bearer ${authToken}`,
                                'Content-Type': 'application/json'
                            }
                        }
                    );

                    if(!incrementUserCourseProgress.ok){
                        const errorData = await incrementUserCourseProgress.json();
                        throw new Error(errorData.detail || "Failed to increment current module")
                    }

                    const updatedProgress = await incrementUserCourseProgress.json();
                    setUserCourseProgress(updatedProgress);
                } else {
                    // If we didn't increment module, update with the cleared progress from the last response
                    const finalProgress = await clearSetCounterResponse.json();
                    setUserCourseProgress(finalProgress);
                }
            } catch(err){
                setError(err instanceof Error ? err.message : "Error in resetting progress counters.");
            } finally{
                setIsLoading(false);
            }

            setResource(null);
            router.replace("/");
        } else if(atSetEnd && !exerciseComplete) {
            setIsLoading(true);
            const authToken = localStorage.getItem("token");

            try{
                // Get the next problem set
                const incrementCurrentVocabProblemSetRequest: IncrementCurrentVocabProblemSetRequest = {
                    id: userCourseProgress!.id,
                    limit: problemSetLimit
                }

                const incrementCurrentVocabProblemSetResponse = await fetch(
                    `${process.env.NEXT_PUBLIC_SERVER_URL}/user-course-progress/current_vocab_problem_set/increment`,
                    {
                        method: "PUT",
                        headers: {
                            'Authorization': `Bearer ${authToken}`,
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify(incrementCurrentVocabProblemSetRequest)
                    }
                )

                if(!incrementCurrentVocabProblemSetResponse.ok){
                    const errorData = await incrementCurrentVocabProblemSetResponse.json();
                    throw new Error(errorData.detail || "Error in incrementing vocab problem set number.")
                }

                const updatedUserCourseProgress = await incrementCurrentVocabProblemSetResponse.json();
                
                setUserCourseProgress(updatedUserCourseProgress);
                setCurrProblemIdx(0);
                setAnswered(false);
                setSelectedAnswer(null);
            } catch(err){
                setError(err instanceof Error ? err.message : "Error in getting next problem set.");
            } finally{
                setIsLoading(false);
            }
        } else{
            setCurrProblemIdx(currProblemIdx + 1);
            setAnswered(false);
            setSelectedAnswer(null);
        }        
    }

    const handleHomeNav = () => {
        setResource(null);
        router.replace("/");
    }

    const getButtonClass = (choice: string) => {
        if (!answered) return styles.answerButton;
        if (choice === correctAnswer) return `${styles.answerButton} ${styles.correct}`;
        if (choice === selectedAnswer) return `${styles.answerButton} ${styles.incorrect}`;
        return styles.answerButton;
    };

    return(
        <div className={styles.container}>
            {/* Hidden Audio Element */}
            <audio ref={audioRef} src={audioUrl} preload="auto" />

            {/* Header */}
            <div className={styles.header}>
                <button className={styles.backButton} onClick={handleHomeNav}>
                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                        <path fillRule="evenodd" d="M9.707 16.707a1 1 0 01-1.414 0l-6-6a1 1 0 010-1.414l6-6a1 1 0 011.414 1.414L5.414 9H17a1 1 0 110 2H5.414l4.293 4.293a1 1 0 010 1.414z" clipRule="evenodd" />
                    </svg>
                    Back to Home
                </button>
            </div>

            {/* Progress Bar */}
            <div className={styles.progressSection}>
                <p className={styles.progressLabel}>
                    Question {currProblemIdx + 1} of {problems.length}
                </p>
                <div className={styles.progressBar}>
                    {progressStatus.map((status, idx) => (
                        <div
                            key={idx}
                            className={`${styles.progressCell} ${styles[status]}`}
                        />
                    ))}
                </div>
            </div>

            {/* Main Content */}
            <div className={styles.mainContent}>
                <div className={styles.questionSection}>
                    <h1 className={styles.questionText}>What word did you hear?</h1>
                    
                    {/* Audio Player Button with Waves */}
                    <div className={styles.audioPlayerContainer}>
                        <div className={styles.waveContainer}>
                            <div className={`${styles.wave} ${isPlaying ? styles.active : ''}`}></div>
                            <div className={`${styles.wave} ${isPlaying ? styles.active : ''}`}></div>
                            <div className={`${styles.wave} ${isPlaying ? styles.active : ''}`}></div>
                            <div className={`${styles.wave} ${isPlaying ? styles.active : ''}`}></div>
                        </div>
                        <button 
                            className={styles.audioButton}
                            onClick={handlePlayAudio}
                            aria-label={isPlaying ? "Pause audio" : "Play audio"}
                        >
                            {isPlaying ? (
                                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
                                    <path fillRule="evenodd" d="M6.75 5.25a.75.75 0 01.75-.75H9a.75.75 0 01.75.75v13.5a.75.75 0 01-.75.75H7.5a.75.75 0 01-.75-.75V5.25zm7.5 0A.75.75 0 0115 4.5h1.5a.75.75 0 01.75.75v13.5a.75.75 0 01-.75.75H15a.75.75 0 01-.75-.75V5.25z" clipRule="evenodd" />
                                </svg>
                            ) : (
                                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
                                    <path fillRule="evenodd" d="M4.5 5.653c0-1.426 1.529-2.33 2.779-1.643l11.54 6.348c1.295.712 1.295 2.573 0 3.285L7.28 19.991c-1.25.687-2.779-.217-2.779-1.643V5.653z" clipRule="evenodd" />
                                </svg>
                            )}
                        </button>
                    </div>
                </div>

                {/* Answer Grid */}
                <div className={styles.answerGrid}>
                    {answerChoices.map((choice) => (
                        <button
                            key={choice}
                            className={getButtonClass(choice)}
                            onClick={() => handleChoiceSelection(choice)}
                            disabled={answered}
                        >
                            {choice}
                            {showConfetti && choice === correctAnswer && (
                                <>
                                    <span className={styles.confetti} style={{ left: '20%', animationDelay: '0s' }} />
                                    <span className={styles.confetti} style={{ left: '40%', animationDelay: '0.1s' }} />
                                    <span className={styles.confetti} style={{ left: '60%', animationDelay: '0.2s' }} />
                                    <span className={styles.confetti} style={{ left: '80%', animationDelay: '0.3s' }} />
                                </>
                            )}
                        </button>
                    ))}
                </div>

                {/* Navigation Buttons */}
                <div className={styles.navigationButtons}>
                    <button className={styles.homeButton} onClick={handleHomeNav}>
                        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                            <path fillRule="evenodd" d="M9.293 2.293a1 1 0 011.414 0l7 7A1 1 0 0117 11h-1v6a1 1 0 01-1 1h-2a1 1 0 01-1-1v-3a1 1 0 00-1-1H9a1 1 0 00-1 1v3a1 1 0 01-1 1H5a1 1 0 01-1-1v-6H3a1 1 0 01-.707-1.707l7-7z" clipRule="evenodd" />
                        </svg>
                        Home
                    </button>
                    <button
                        className={`${styles.nextButton} ${atSetEnd && exerciseComplete ? styles.complete : ''}`}
                        onClick={handleNext}
                        disabled={!answered || isLoading}
                    >
                        {isLoading ? (
                            'Loading...'
                        ) : atSetEnd && exerciseComplete ? (
                            <>
                                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.857-9.809a.75.75 0 00-1.214-.882l-3.483 4.79-1.88-1.88a.75.75 0 10-1.06 1.061l2.5 2.5a.75.75 0 001.137-.089l4-5.5z" clipRule="evenodd" />
                                </svg>
                                Complete
                            </>
                        ) : (
                            <>
                                Next
                                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                                    <path fillRule="evenodd" d="M3 10a.75.75 0 01.75-.75h10.638L10.23 5.29a.75.75 0 111.04-1.08l5.5 5.25a.75.75 0 010 1.08l-5.5 5.25a.75.75 0 11-1.04-1.08l4.158-3.96H3.75A.75.75 0 013 10z" clipRule="evenodd" />
                                </svg>
                            </>
                        )}
                    </button>
                </div>
            </div>

            {/* Error Toast */}
            {error && (
                <div className={styles.errorToast}>
                    {error}
                </div>
            )}
        </div>
    );
}

export default VocabListeningProblemSets;
