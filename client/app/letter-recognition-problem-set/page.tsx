'use client'

import { useResource } from "@/context/ResourceContext"
import { useUserCourseProgress } from "@/context/UserCourseProgressContext";
import { LetterRecognitionProblemSetResponse } from "@/types/response_models/ResourceResponse";
import { useRouter } from "next/navigation";
import { useState, useEffect } from "react";
import styles from './LetterRecognitionProblemSet.module.css';

type ProgressStatus = 'unanswered' | 'current' | 'correct' | 'incorrect';

const LetterRecognitionProblemSet = () => {
    const router = useRouter();

    // Contexts
    const {resource, setResource} = useResource();
    const {userCourseProgress, setUserCourseProgress} = useUserCourseProgress();

    // Utils
    const [isLoading, setIsLoading] = useState<boolean>(false);
    const [error, setError] = useState<string>("");
    const [points, setPoints] = useState<number>(0);
    const [progressStatus, setProgressStatus] = useState<ProgressStatus[]>([]);
    const [selectedAnswer, setSelectedAnswer] = useState<string | null>(null);
    const [answered, setAnswered] = useState<boolean>(false);
    const [showConfetti, setShowConfetti] = useState<boolean>(false);

    if (!resource || !resource.resource) {
        return (
            <div className={styles.loading}>
                <div className={styles.spinner}></div>
                <p className={styles.loadingText}>Loading letter recognition problems...</p>
            </div>
        );
    }

    // UserCourseProgress
    const problemCounter = userCourseProgress!.problem_counter;
    
    // Resource
    const letterRecognitionProblemSet = resource.resource as LetterRecognitionProblemSetResponse;
    const problems = letterRecognitionProblemSet.problems;
    
    // Safety check: ensure problemCounter is within bounds
    if (problemCounter >= problems.length || problemCounter < 0) {
        return (
            <div className={styles.loading}>
                <div className={styles.spinner}></div>
                <p className={styles.loadingText}>Loading problem...</p>
            </div>
        );
    }
    
    const problem = problems[problemCounter];
    const answerChoices = problem.answer_choices;
    const correctAnswer = problem.correct_answer;

    // Completion logic
    const minPoints = problems.length - 1;
    const atSetEnd = problemCounter === problems.length - 1;
    const exerciseComplete = points >= minPoints;

    // Initialize progress status when component mounts
    useEffect(() => {
        const initialStatus: ProgressStatus[] = problems.map((_, idx) => 
            idx === problemCounter ? 'current' : 'unanswered'
        );
        setProgressStatus(initialStatus);
    }, []);

    // Update current problem indicator
    useEffect(() => {
        if (progressStatus.length > 0 && !answered) {
            const newStatus = [...progressStatus];
            newStatus[problemCounter] = 'current';
            setProgressStatus(newStatus);
        }
    }, [problemCounter, answered]);

    const handleAnswerSelection = (choice: string) => {
        if (answered) return; // Prevent multiple clicks

        setSelectedAnswer(choice);
        setAnswered(true);

        const isCorrect = choice === correctAnswer;

        // Update progress bar
        const newStatus = [...progressStatus];
        newStatus[problemCounter] = isCorrect ? 'correct' : 'incorrect';
        setProgressStatus(newStatus);

        if(isCorrect){
            // Show confetti effect
            setShowConfetti(true);
            setTimeout(() => setShowConfetti(false), 1000);
            
            // Increment points
            setPoints(points + 1);
        }
    }

    const handleHomeNav = () => {
        setResource(null);
        router.replace("/");
    }

    const handleNext = async() => {
        const authToken = localStorage.getItem("token");
        if (!authToken) {
            setError("Authentication required. Please log in.");
            router.replace("/login");
            return;
        }

        if(atSetEnd && exerciseComplete){
            setIsLoading(true);

            try{
                // Clear problem counter
                const clearProblemCounterResponse = await fetch(
                    `${process.env.NEXT_PUBLIC_SERVER_URL}/user-course-progress/problem-counter/clear/${userCourseProgress!.id}`,
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

                // Increment current module if this is the current module
                if(userCourseProgress!.curr_module === resource!.number){
                    const incrementUserCourseProgress = await fetch(
                        `${process.env.NEXT_PUBLIC_SERVER_URL}/user-course-progress/curr-module/increment/${userCourseProgress!.id}`,
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
                    const updatedProgress = await clearProblemCounterResponse.json();
                    setUserCourseProgress(updatedProgress);
                }

                setResource(null);
                router.replace("/");
            } catch(err){
                setError(err instanceof Error ? err.message : "Error in resetting progress counters.");
            } finally{
                setIsLoading(false);
            }
        } else if(atSetEnd && !exerciseComplete){
            // Reset to start of problem set
            setIsLoading(true);

            try{
                const resetProblemCounterResponse = await fetch(
                    `${process.env.NEXT_PUBLIC_SERVER_URL}/user-course-progress/problem-counter/clear/${userCourseProgress!.id}`,
                    {
                        method: "PUT",
                        headers: {
                            'Authorization': `Bearer ${authToken}`,
                            'Content-Type': 'application/json'
                        }
                    }
                );

                if(!resetProblemCounterResponse.ok){
                    const errorData = await resetProblemCounterResponse.json();
                    throw new Error(errorData.detail || "Failed to reset problem counter")
                }

                const updatedUser = await resetProblemCounterResponse.json();
                setUserCourseProgress(updatedUser);
                
                // Reset UI state
                setPoints(0);
                setAnswered(false);
                setSelectedAnswer(null);
                const resetStatus: ProgressStatus[] = problems.map((_, idx) => 
                    idx === 0 ? 'current' : 'unanswered'
                );
                setProgressStatus(resetStatus);
            } catch(err){
                setError(err instanceof Error ? err.message : "Error in resetting problem set.");
            } finally{
                setIsLoading(false);
            }
        } else{
            // Move to next problem
            setIsLoading(true);

            try{
                const incrementProblemCounterResponse = await fetch(
                    `${process.env.NEXT_PUBLIC_SERVER_URL}/user-course-progress/problem-counter/increment/${userCourseProgress!.id}`,
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
                    throw new Error(errorData.detail || "Failed to increment problem counter")
                }

                const updatedUserCourseProgress = await incrementProblemCounterResponse.json();
                setUserCourseProgress(updatedUserCourseProgress);
                
                // Reset answer state for next problem
                setAnswered(false);
                setSelectedAnswer(null);
            } catch(err){
                setError(err instanceof Error ? err.message : "Error moving to next problem.");
            } finally{
                setIsLoading(false);
            }
        }
    }

    const getButtonClass = (choice: string) => {
        if (!answered) return styles.answerButton;
        if (choice === correctAnswer) return `${styles.answerButton} ${styles.correct}`;
        if (choice === selectedAnswer) return `${styles.answerButton} ${styles.incorrect}`;
        return styles.answerButton;
    };

    // Auto-dismiss error after 5 seconds
    useEffect(() => {
        if (error) {
            const timer = setTimeout(() => setError(''), 5000);
            return () => clearTimeout(timer);
        }
    }, [error]);

    return(
        <div className={styles.container}>
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
                    Question {problemCounter + 1} of {problems.length}
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
                    <h1 className={styles.questionText}>Which letter is in the word in the right form?</h1>
                    <div className={styles.wordCard}>
                        <p className={styles.wordText}>{problem.word}</p>
                    </div>
                </div>

                {/* Answer Grid */}
                <div className={styles.answerGrid}>
                    {answerChoices.map((choice) => (
                        <button
                            key={choice}
                            className={getButtonClass(choice)}
                            onClick={() => handleAnswerSelection(choice)}
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
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    {error}
                </div>
            )}
        </div>
    );
}

export default LetterRecognitionProblemSet;
