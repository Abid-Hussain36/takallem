'use client'

import { useResource } from "@/context/ResourceContext"
import { useUserCourseProgress } from "@/context/UserCourseProgressContext";
import { PronounciationExplainInput } from "@/types/request_models/PronounciationExplainInput";
import { PronounciationExplainOutput } from "@/types/response_models/PronounciationExplainOutput";
import { PronounciationResponse } from "@/types/response_models/PronounciationResponse";
import { WordPronounciationProblemSetResponse } from "@/types/response_models/ResourceResponse";
import { useRouter } from "next/navigation";
import { useRef, useState, useEffect } from "react";
import styles from './WordPronounciationProblemSet.module.css';

type ProgressStatus = 'unanswered' | 'current' | 'correct';

const WordPronounciationProblemSet = () => {
    const router = useRouter();

    // Contexts
    const {resource, setResource} = useResource();
    const {userCourseProgress, setUserCourseProgress} = useUserCourseProgress();

    // Utils
    const [isLoading, setIsLoading] = useState<boolean>(false);
    const [error, setError] = useState<string>("");
    const [progressStatus, setProgressStatus] = useState<ProgressStatus[]>([]);

    if (!resource || !resource.resource) {
        return (
            <div className={styles.loading}>
                <div className={styles.spinner}></div>
                <p className={styles.loadingText}>Loading word pronunciation problems...</p>
            </div>
        );
    }

    // UserCourseProgress
    const problemCounter = userCourseProgress!.problem_counter;
    
    // Resource
    const wordPronounciationProblemSet = resource.resource as WordPronounciationProblemSetResponse;
    const problems = wordPronounciationProblemSet.problems;
    
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

    // Pronunciation Data per problem
    const [query, setQuery] = useState<string>("");
    const word = useRef<string>(problem.word);
    const [status, setStatus] = useState<string>("");
    const transcription = useRef<string>("");
    const [feedback, setFeedback] = useState<string[]>([]);
    const mistake_tags = useRef<string[]>([]);
    const performance_reflection = useRef<string>("");
    const [showFeedback, setShowFeedback] = useState<boolean>(false);
    const [passed, setPassed] = useState<boolean>(false);
    
    // User Audio
    const [isRecording, setIsRecording] = useState(false);
    const [audioBlob, setAudioBlob] = useState<Blob | null>(null);
    const mediaRecorderRef = useRef<MediaRecorder | null>(null);
    const audioChunksRef = useRef<Blob[]>([]);
    
    // Word Audio
    const wordAudioRef = useRef<HTMLAudioElement | null>(null);
    
    // Chat Messages Ref for auto-scroll
    const chatMessagesRef = useRef<HTMLDivElement | null>(null);

    // Completion check
    const allProblemsCompleted = progressStatus.every(status => status === 'correct');

    // Initialize progress status when component mounts
    useEffect(() => {
        const initialStatus: ProgressStatus[] = problems.map((_, idx) => 
            idx === problemCounter ? 'current' : 'unanswered'
        );
        setProgressStatus(initialStatus);
    }, []);

    // Update current problem indicator and reset state when problem changes
    useEffect(() => {
        if (progressStatus.length > 0) {
            const newStatus = [...progressStatus];
            // Set current problem to current only if not already correct
            if (newStatus[problemCounter] !== 'correct') {
                newStatus[problemCounter] = 'current';
            }
            setProgressStatus(newStatus);
        }
        
        // Reset state for new problem
        word.current = problem.word;
        setQuery("");
        setStatus("");
        transcription.current = "";
        setFeedback([]);
        mistake_tags.current = [];
        performance_reflection.current = "";
        setShowFeedback(false);
        setPassed(false);
        setAudioBlob(null);
    }, [problemCounter]);

    // Play word audio when user clicks on the word
    const playWordAudio = async () => {
        if (wordAudioRef.current) {
            try {
                await wordAudioRef.current.play();
            } catch (err) {
                console.error("Failed to play audio:", err);
                setError("Failed to play audio. Please try again.");
            }
        }
    };

    // Handle recording
    const handleRecordClick = () => {
        if (isRecording) {
            stopRecording();
        } else {
            startRecording();
        }
    };

    const startRecording = async () => {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ 
                audio: {
                    channelCount: 1,
                    sampleRate: 16000
                } 
            });
            
            const mediaRecorder = new MediaRecorder(stream, {
                mimeType: 'audio/webm'
            });
            
            mediaRecorderRef.current = mediaRecorder;
            audioChunksRef.current = [];
            
            mediaRecorder.ondataavailable = (event) => {
                if (event.data.size > 0) {
                    audioChunksRef.current.push(event.data);
                }
            };
            
            mediaRecorder.onstop = () => {
                const audioBlob = new Blob(audioChunksRef.current, { 
                    type: 'audio/webm' 
                });
                setAudioBlob(audioBlob);
                stream.getTracks().forEach(track => track.stop());
            };
            
            mediaRecorder.start();
            setIsRecording(true);
            
        } catch (error) {
            console.error('Error accessing microphone:', error);
            setError('Please allow microphone access to record audio');
        }
    };

    const stopRecording = () => {
        if (mediaRecorderRef.current && isRecording) {
            mediaRecorderRef.current.stop();
            setIsRecording(false);
        }
    };

    const submitAudio = async () => {
        setQuery("");
        
        if (!audioBlob) {
            setError('Please record audio first');
            return;
        }

        const authToken = localStorage.getItem('token');
        if (!authToken) {
            setError("Authentication required. Please log in.");
            router.replace("/login");
            return;
        }

        const formData = new FormData();
        formData.append('user_audio', audioBlob, 'user_audio.webm');
        formData.append('phrase', problem.word);
        formData.append('isWord', 'true');
        formData.append('language', userCourseProgress!.language);
        if (userCourseProgress!.dialect) {
            formData.append('dialect', userCourseProgress!.dialect);
        }

        setIsLoading(true);
        setError("");
        
        try {
            const pronounciationCheckResponse = await fetch(
                `${process.env.NEXT_PUBLIC_SERVER_URL}/pronounciation/check`,
                {
                    method: 'POST',
                    headers: {
                        'Authorization': `Bearer ${authToken}`,
                    },
                    body: formData
                }
            );
            
            if (!pronounciationCheckResponse.ok) {
                const errorData = await pronounciationCheckResponse.json();
                throw new Error(errorData.detail || 'Failed to submit audio');
            }
            
            const pronounciationCheckResult: PronounciationResponse = await pronounciationCheckResponse.json();

            setStatus(pronounciationCheckResult.status);
            transcription.current = pronounciationCheckResult.transcription;
            setFeedback([pronounciationCheckResult.feedback]);
            mistake_tags.current = pronounciationCheckResult.mistake_tags;
            performance_reflection.current = pronounciationCheckResult.performance_reflection;

            if(pronounciationCheckResult.status === "pass"){
                setPassed(true);
                
                // Update progress bar to show green for passed problem
                const newStatus = [...progressStatus];
                newStatus[problemCounter] = 'correct';
                setProgressStatus(newStatus);
            }

            setShowFeedback(true);
            setAudioBlob(null);
        } catch (err) {
            setError(err instanceof Error ? err.message : "Error submitting audio.");
        } finally{
            setIsLoading(false);
        }
    };

    const handleQuestionSubmit = async() => {
        if (!query.trim()) {
            setError("Please enter a question");
            return;
        }

        const authToken = localStorage.getItem('token');
        if (!authToken) {
            setError("Authentication required. Please log in.");
            router.replace("/login");
            return;
        }

        setIsLoading(true);
        setError("");

        try{
            const explainRequest: PronounciationExplainInput = {
                query: query,
                language: userCourseProgress!.language,
                dialect: userCourseProgress?.dialect ?? null,
                phrase: word.current,
                status: status,
                transcription: transcription.current,
                previous_feedback: feedback,
                mistake_tags: mistake_tags.current,
                performance_reflection: performance_reflection.current
            }

            const explainResponse = await fetch(
                `${process.env.NEXT_PUBLIC_SERVER_URL}/pronounciation/explain`,
                {
                    method: "POST",
                    headers: {
                        "Authorization": `Bearer ${authToken}`,
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify(explainRequest)
                }
            );

            if(!explainResponse.ok){
                const errorData = await explainResponse.json();
                throw new Error(errorData.detail || "Failed to get explain response.")
            }

            const explainResult: PronounciationExplainOutput = await explainResponse.json();
            setFeedback([...feedback, query, explainResult.response || ""]);
            setQuery("");
        } catch(err){
            setError(err instanceof Error ? err.message : "Error answering user question.");
        } finally{
            setIsLoading(false);
        }
    }

    const handleHomeNav = () => {
        setResource(null);
        router.replace("/");
    }

    const handleNext = async () => {
        const authToken = localStorage.getItem("token");
        if (!authToken) {
            setError("Authentication required. Please log in.");
            router.replace("/login");
            return;
        }

        if (allProblemsCompleted) {
            // All problems passed, complete the exercise
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
                setError(err instanceof Error ? err.message : "Error in completing exercise.");
            } finally{
                setIsLoading(false);
            }
        } else if (passed) {
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
            } catch(err){
                setError(err instanceof Error ? err.message : "Error moving to next problem.");
            } finally{
                setIsLoading(false);
            }
        }
    }

    // Auto-scroll chat messages
    useEffect(() => {
        if (chatMessagesRef.current) {
            chatMessagesRef.current.scrollTop = chatMessagesRef.current.scrollHeight;
        }
    }, [feedback]);

    // Auto-dismiss error after 5 seconds
    useEffect(() => {
        if (error) {
            const timer = setTimeout(() => setError(""), 5000);
            return () => clearTimeout(timer);
        }
    }, [error]);

    return(
        <div className={styles.container}>
            {/* Header */}
            <div className={styles.header}>
                <button className={styles.backButton} onClick={handleHomeNav}>
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                    </svg>
                    Back
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
                {/* Question Section */}
                <div className={styles.questionSection}>
                    <h1 className={styles.questionText}>{problem.question}</h1>
                    
                    {/* Clickable Word Display */}
                    <div className={styles.wordDisplay} onClick={playWordAudio}>
                        <span className={styles.wordText}>{problem.word}</span>
                    </div>
                </div>

                {/* Recording Section */}
                <div className={styles.recordingSection}>
                    <div className={styles.recordButton}>
                        <button 
                            className={`${styles.recordButtonInner} ${isRecording ? styles.recording : ''}`}
                            onClick={handleRecordClick}
                            disabled={passed}
                        >
                            {isRecording ? (
                                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 10a1 1 0 011-1h4a1 1 0 011 1v4a1 1 0 01-1 1h-4a1 1 0 01-1-1v-4z" />
                                </svg>
                            ) : (
                                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
                                </svg>
                            )}
                        </button>
                        
                        {/* Wave Animation */}
                        <div className={styles.waveContainer}>
                            <div className={`${styles.wave} ${isRecording ? styles.active : ''}`}></div>
                            <div className={`${styles.wave} ${isRecording ? styles.active : ''}`}></div>
                            <div className={`${styles.wave} ${isRecording ? styles.active : ''}`}></div>
                            <div className={`${styles.wave} ${isRecording ? styles.active : ''}`}></div>
                        </div>
                    </div>

                    {/* Recording Controls */}
                    {audioBlob && !isRecording && (
                        <div className={styles.recordingButtons}>
                            <button className={styles.submitButton} onClick={submitAudio} disabled={isLoading}>
                                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                                </svg>
                                Submit Recording
                            </button>
                        </div>
                    )}
                </div>

                {/* Feedback Section */}
                {showFeedback && (
                    <div className={styles.feedbackSection}>
                        <div className={styles.feedbackTitle}>
                            <span className={`${styles.statusBadge} ${status === 'pass' ? styles.pass : styles.fail}`}>
                                {status === 'pass' ? (
                                    <>
                                        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                                        </svg>
                                        Passed
                                    </>
                                ) : (
                                    <>
                                        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                                        </svg>
                                        Try Again
                                    </>
                                )}
                            </span>
                        </div>

                        {/* Chat Interface */}
                        {feedback.length > 0 && (
                            <div className={styles.chatContainer} ref={chatMessagesRef}>
                                {feedback.map((message, index) => (
                                    <div 
                                        key={index} 
                                        className={`${styles.chatMessage} ${index % 2 === 0 ? styles.ai : styles.user}`}
                                    >
                                        {message}
                                    </div>
                                ))}
                            </div>
                        )}

                        {/* Question Input */}
                        <div className={styles.questionInputContainer}>
                            <label className={styles.questionInputLabel}>
                                Have a question? Ask the AI for clarification:
                            </label>
                            <div className={styles.questionInputWrapper}>
                                <textarea
                                    className={styles.questionInput}
                                    value={query}
                                    onChange={(e) => setQuery(e.target.value)}
                                    placeholder="Type your question here..."
                                    onKeyDown={(e) => {
                                        if (e.key === 'Enter' && !e.shiftKey) {
                                            e.preventDefault();
                                            handleQuestionSubmit();
                                        }
                                    }}
                                />
                                <button 
                                    className={styles.askButton} 
                                    onClick={handleQuestionSubmit}
                                    disabled={isLoading || !query.trim()}
                                >
                                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                                    </svg>
                                    Ask
                                </button>
                            </div>
                        </div>
                    </div>
                )}

                {/* Navigation Buttons */}
                <div className={styles.navigationButtons}>
                    <button className={styles.homeButton} onClick={handleHomeNav}>
                        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
                        </svg>
                        Home
                    </button>
                    
                    {passed && (
                        <button 
                            className={`${styles.nextButton} ${allProblemsCompleted ? styles.complete : ''}`}
                            onClick={handleNext}
                        >
                            {allProblemsCompleted ? (
                                <>
                                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                                    </svg>
                                    Complete
                                </>
                            ) : (
                                <>
                                    Next
                                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                                    </svg>
                                </>
                            )}
                        </button>
                    )}
                </div>
            </div>

            {/* Word Audio Element */}
            <audio ref={wordAudioRef} src={problem.word_audio} />

            {/* Loading Overlay */}
            {isLoading && (
                <div className={styles.loadingOverlay}>
                    <div className={styles.spinner}></div>
                </div>
            )}

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

export default WordPronounciationProblemSet;
