'use client'

import { useResource } from "@/context/ResourceContext"
import { useUserCourseProgress } from "@/context/UserCourseProgressContext";
import { LetterJoiningProblemSetResponse } from "@/types/response_models/ResourceResponse";
import { LetterJoiningResponse, WritingPhotoRetakeResponse } from "@/types/response_models/LetterWritingResponse";
import { JoiningExplainInput } from "@/types/request_models/JoiningExplainInput";
import { WritingExplainOutput } from "@/types/response_models/WritingExplainOutput";
import { useRouter } from "next/navigation";
import { useState, useEffect, useRef } from "react";
import styles from './LetterJoiningProblemSet.module.css';

type ProgressStatus = 'unanswered' | 'current' | 'correct';

const LetterJoiningProblemSet = () => {
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
                <p className={styles.loadingText}>Loading letter joining problems...</p>
            </div>
        );
    }

    // UserCourseProgress
    const problemCounter = userCourseProgress!.problem_counter;
    
    // Resource
    const letterJoiningProblemSet = resource.resource as LetterJoiningProblemSetResponse;
    const problems = letterJoiningProblemSet.problems;
    
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

    // Writing Data per problem
    const [uploadedImage, setUploadedImage] = useState<File | null>(null);
    const [imagePreview, setImagePreview] = useState<string | null>(null);
    const [joiningResponse, setJoiningResponse] = useState<LetterJoiningResponse | null>(null);
    const [showFeedback, setShowFeedback] = useState<boolean>(false);
    const [passed, setPassed] = useState<boolean>(false);
    
    // Chat functionality
    const [query, setQuery] = useState<string>("");
    const [feedback, setFeedback] = useState<string[]>([]);
    
    const fileInputRef = useRef<HTMLInputElement>(null);
    const chatMessagesRef = useRef<HTMLDivElement | null>(null);

    // Completion check
    const allProblemsCompleted = progressStatus.every(status => status === 'correct');

    // Initialize progress status when component mounts
    useEffect(() => {
        const initialProgressStatus: ProgressStatus[] = problems.map((_, idx) => {
            if(idx < problemCounter){
                return "correct";
            } else if(idx === problemCounter){
                return "current";
            } else{
                return "unanswered"
            }
        });

        setProgressStatus(initialProgressStatus);
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
        setUploadedImage(null);
        setImagePreview(null);
        setJoiningResponse(null);
        setShowFeedback(false);
        setPassed(false);
        setQuery("");
        setFeedback([]);
        if (fileInputRef.current) {
            fileInputRef.current.value = '';
        }
    }, [problemCounter]);

    // Handle file selection
    const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0];
        if (file) {
            // Validate file type
            if (!file.type.startsWith('image/')) {
                setError('Please upload an image file');
                return;
            }

            // Validate file size (max 10MB)
            if (file.size > 10 * 1024 * 1024) {
                setError('Image size must be less than 10MB');
                return;
            }

            setUploadedImage(file);
            
            // Create preview
            const reader = new FileReader();
            reader.onload = (e) => {
                setImagePreview(e.target?.result as string);
            };
            reader.readAsDataURL(file);
        }
    };

    // Remove uploaded image
    const handleRemoveImage = () => {
        setUploadedImage(null);
        setImagePreview(null);
        if (fileInputRef.current) {
            fileInputRef.current.value = '';
        }
    };

    // Submit writing for evaluation
    const submitWriting = async () => {
        if (!uploadedImage) {
            setError('Please upload an image of your writing');
            return;
        }

        const authToken = localStorage.getItem("token");
        if (!authToken) {
            setError("Authentication required. Please log in.");
            router.replace("/login");
            return;
        }

        setIsLoading(true);
        setError('');

        try {
            const formData = new FormData();
            
            formData.append('user_image', uploadedImage);
            
            // Add letter_list as individual form entries
            problem.letter_list.forEach((letter) => {
                formData.append('letter_list', letter);
            });
            
            formData.append('target_word', problem.word);
            formData.append('language', userCourseProgress!.language);
            if (userCourseProgress!.dialect) {
                formData.append('dialect', userCourseProgress!.dialect);
            }

            const response = await fetch(
                `${process.env.NEXT_PUBLIC_SERVER_URL}/writing/joining`,
                {
                    method: 'POST',
                    headers: {
                        'Authorization': `Bearer ${authToken}`,
                    },
                    body: formData
                }
            );

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Failed to evaluate writing');
            }

            const result = await response.json();
            
            // Check if it's a retake response
            if ('capture_tips' in result && !('status' in result)) {
                const retakeResponse = result as WritingPhotoRetakeResponse;
                setError(retakeResponse.capture_tips);
                setIsLoading(false);
                return;
            }

            const joiningResult = result as LetterJoiningResponse;
            setJoiningResponse(joiningResult);
            setFeedback([joiningResult.feedback]);
            setShowFeedback(true);

            // Check if passed
            if (joiningResult.status === 'pass') {
                setPassed(true);
                
                // Update progress status to correct
                const newStatus = [...progressStatus];
                newStatus[problemCounter] = 'correct';
                setProgressStatus(newStatus);
            }

        } catch (err) {
            setError(err instanceof Error ? err.message : 'Error evaluating writing');
        } finally {
            setIsLoading(false);
        }
    };

    // Handle question submit for chat
    const handleQuestionSubmit = async () => {
        if (!query.trim()) {
            setError("Please enter a question");
            return;
        }

        if (!joiningResponse) {
            setError("Please submit your writing first");
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

        try {
            const explainRequest: JoiningExplainInput = {
                query: query,
                language: userCourseProgress!.language,
                dialect: userCourseProgress?.dialect ?? null,
                letter_list: problem.letter_list,
                target_word: problem.word,
                status: joiningResponse.status,
                scores: joiningResponse.scores,
                previous_feedback: feedback,
                mistake_tags: joiningResponse.mistake_tags,
                performance_reflection: joiningResponse.performance_reflection
            };

            const explainResponse = await fetch(
                `${process.env.NEXT_PUBLIC_SERVER_URL}/writing/joining/explain`,
                {
                    method: "POST",
                    headers: {
                        "Authorization": `Bearer ${authToken}`,
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify(explainRequest)
                }
            );

            if (!explainResponse.ok) {
                const errorData = await explainResponse.json();
                throw new Error(errorData.detail || "Failed to get explain response.");
            }

            const explainResult: WritingExplainOutput = await explainResponse.json();
            // Append user question and AI response to feedback array
            setFeedback([...feedback, query, explainResult.response || ""]);
            setQuery("");
        } catch (err) {
            setError(err instanceof Error ? err.message : "Error answering user question.");
        } finally {
            setIsLoading(false);
        }
    };

    // Navigate home
    const handleHomeNav = () => {
        setResource(null);
        router.replace("/");
    };

    // Handle next button
    const handleNext = async () => {
        // Prevent multiple clicks while loading
        if (isLoading) {
            return;
        }

        const authToken = localStorage.getItem("token");
        if (!authToken) {
            setError("Authentication required. Please log in.");
            router.replace("/login");
            return;
        }

        if (allProblemsCompleted) {
            // All problems completed, increment module
            setIsLoading(true);

            try {
                // Reset problem counter
                const resetCounterResponse = await fetch(
                    `${process.env.NEXT_PUBLIC_SERVER_URL}/user-course-progress/problem-counter/clear/${userCourseProgress!.id}`,
                    {
                        method: "PUT",
                        headers: {
                            'Authorization': `Bearer ${authToken}`,
                            'Content-Type': 'application/json'
                        }
                    }
                );

                if (!resetCounterResponse.ok) {
                    throw new Error("Failed to reset problem counter");
                }

                // Increment current module ONLY if we're currently on this module
                // This prevents double-increments if the user revisits this page
                if (userCourseProgress!.curr_module === resource!.number) {
                    const incrementModuleResponse = await fetch(
                        `${process.env.NEXT_PUBLIC_SERVER_URL}/user-course-progress/curr-module/increment/${userCourseProgress!.id}`,
                        {
                            method: "PUT",
                            headers: {
                                'Authorization': `Bearer ${authToken}`,
                                'Content-Type': 'application/json'
                            }
                        }
                    );

                    if (!incrementModuleResponse.ok) {
                        throw new Error("Failed to increment module");
                    }

                    const updatedProgress = await incrementModuleResponse.json();
                    setUserCourseProgress(updatedProgress);
                }

                // Navigate home
                setResource(null);
                router.replace("/");

            } catch (err) {
                setError(err instanceof Error ? err.message : "Error completing exercise");
            } finally {
                setIsLoading(false);
            }
        } else {
            // Move to next problem
            setIsLoading(true);

            try {
                const incrementResponse = await fetch(
                    `${process.env.NEXT_PUBLIC_SERVER_URL}/user-course-progress/problem-counter/increment/${userCourseProgress!.id}`,
                    {
                        method: "PUT",
                        headers: {
                            'Authorization': `Bearer ${authToken}`,
                            'Content-Type': 'application/json'
                        }
                    }
                );

                if (!incrementResponse.ok) {
                    throw new Error("Failed to move to next problem");
                }

                const updatedProgress = await incrementResponse.json();
                setUserCourseProgress(updatedProgress);

            } catch (err) {
                setError(err instanceof Error ? err.message : "Error moving to next problem");
            } finally {
                setIsLoading(false);
            }
        }
    };

    // Auto-scroll chat messages
    useEffect(() => {
        if (chatMessagesRef.current) {
            chatMessagesRef.current.scrollTop = chatMessagesRef.current.scrollHeight;
        }
    }, [feedback]);

    // Auto-dismiss error after 5 seconds
    useEffect(() => {
        if (error) {
            const timer = setTimeout(() => setError(''), 5000);
            return () => clearTimeout(timer);
        }
    }, [error]);

    return (
        <div className={styles.container}>
            {/* Header */}
            <div className={styles.header}>
                <button className={styles.backButton} onClick={handleHomeNav}>
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
                    </svg>
                    Back to Modules
                </button>
            </div>

            {/* Progress Bar */}
            <div className={styles.progressSection}>
                <div className={styles.progressLabel}>Progress</div>
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
                    <h1 className={styles.questionText}>
                        Write the joined word formed from these letters:
                    </h1>
                    <div className={styles.lettersDisplay}>
                        {/* Display letters right-to-left with + between them */}
                        {[...problem.letter_list].reverse().map((letter, idx, arr) => (
                            <div key={idx} style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                                <span className={styles.letter}>{letter}</span>
                                {idx < arr.length - 1 && (
                                    <span className={styles.plusSign}>+</span>
                                )}
                            </div>
                        ))}
                    </div>
                    <span className={styles.targetWord}>
                        Target Word: {problem.word}
                    </span>
                </div>

                {/* Upload Section */}
                <div className={styles.uploadSection}>
                    <h2 className={styles.uploadTitle}>
                        Upload a Photo of Your Writing
                    </h2>
                    
                    <div className={`${styles.uploadButton} ${uploadedImage ? styles.hasImage : ''}`}>
                        <input 
                            type="file" 
                            accept="image/*"
                            onChange={handleFileSelect}
                            ref={fileInputRef}
                            id="file-upload"
                        />
                        <label htmlFor="file-upload" style={{ cursor: 'pointer', width: '100%', height: '100%' }}>
                            {imagePreview ? (
                                <img src={imagePreview} alt="Preview" className={styles.previewImage} />
                            ) : (
                                <div className={styles.uploadButtonInner}>
                                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                                    </svg>
                                    <span className={styles.uploadButtonText}>
                                        {uploadedImage ? 'Change Photo' : 'Tap to Upload'}
                                    </span>
                                </div>
                            )}
                        </label>
                        
                        {uploadedImage && (
                            <button 
                                className={styles.removeImageButton}
                                onClick={handleRemoveImage}
                                type="button"
                            >
                                ✕
                            </button>
                        )}
                    </div>

                    <button 
                        className={styles.submitButton}
                        onClick={submitWriting}
                        disabled={!uploadedImage || isLoading}
                    >
                        {isLoading ? 'Evaluating...' : 'Submit Writing'}
                    </button>
                </div>

                {/* Feedback Section */}
                {showFeedback && joiningResponse && (
                    <div className={styles.feedbackSection}>
                        <div className={styles.feedbackHeader}>
                            <h2 className={styles.feedbackTitle}>AI Feedback</h2>
                            <span className={`${styles.statusBadge} ${styles[joiningResponse.status]}`}>
                                {joiningResponse.status === 'pass' ? (
                                    <>
                                        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                                        </svg>
                                        Passed
                                    </>
                                ) : (
                                    <>
                                        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                                        </svg>
                                        Try Again
                                    </>
                                )}
                            </span>
                        </div>

                        {/* Scores Grid */}
                        <div className={styles.scoresGrid}>
                            <div className={styles.scoreCard}>
                                <div className={styles.scoreLabel}>Connection Accuracy</div>
                                <div className={styles.scoreValue}>
                                    {joiningResponse.scores.connection_accuracy.toFixed(1)}
                                    <span className={styles.scorePercentage}>%</span>
                                </div>
                            </div>
                            <div className={styles.scoreCard}>
                                <div className={styles.scoreLabel}>Positional Forms</div>
                                <div className={styles.scoreValue}>
                                    {joiningResponse.scores.positional_forms.toFixed(1)}
                                    <span className={styles.scorePercentage}>%</span>
                                </div>
                            </div>
                            <div className={styles.scoreCard}>
                                <div className={styles.scoreLabel}>Spacing & Flow</div>
                                <div className={styles.scoreValue}>
                                    {joiningResponse.scores.spacing_flow.toFixed(1)}
                                    <span className={styles.scorePercentage}>%</span>
                                </div>
                            </div>
                            <div className={styles.scoreCard}>
                                <div className={styles.scoreLabel}>Baseline Consistency</div>
                                <div className={styles.scoreValue}>
                                    {joiningResponse.scores.baseline_consistency.toFixed(1)}
                                    <span className={styles.scorePercentage}>%</span>
                                </div>
                            </div>
                            <div className={styles.scoreCard}>
                                <div className={styles.scoreLabel}>Dots & Diacritics</div>
                                <div className={styles.scoreValue}>
                                    {joiningResponse.scores.dots_diacritics.toFixed(1)}
                                    <span className={styles.scorePercentage}>%</span>
                                </div>
                            </div>
                            <div className={styles.scoreCard}>
                                <div className={styles.scoreLabel}>Overall Score</div>
                                <div className={styles.scoreValue}>
                                    {joiningResponse.scores.overall.toFixed(1)}
                                    <span className={styles.scorePercentage}>%</span>
                                </div>
                            </div>
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

                        {/* Mistake Tags */}
                        {joiningResponse.mistake_tags.length > 0 && (
                            <div className={styles.mistakeTags}>
                                {joiningResponse.mistake_tags.map((tag, idx) => (
                                    <span key={idx} className={styles.mistakeTag}>
                                        {tag}
                                    </span>
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

                {/* Navigation Section */}
                <div className={styles.navigationSection}>
                    <button 
                        className={`${styles.navButton} ${styles.homeButton}`}
                        onClick={handleHomeNav}
                    >
                        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
                        </svg>
                        Home
                    </button>

                    {allProblemsCompleted ? (
                        <button 
                            className={`${styles.navButton} ${styles.completeButton}`}
                            onClick={handleNext}
                            disabled={isLoading}
                        >
                            {isLoading ? 'Loading...' : 'Complete Exercise'}
                            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                            </svg>
                        </button>
                    ) : (
                        <button 
                            className={`${styles.navButton} ${styles.nextButton}`}
                            onClick={handleNext}
                            disabled={!passed || isLoading}
                        >
                            {isLoading ? 'Loading...' : 'Next'}
                            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
                            </svg>
                        </button>
                    )}
                </div>
            </div>

            {/* Loading Overlay */}
            {isLoading && (
                <div className={styles.loadingOverlay}>
                    <div className={styles.spinner}></div>
                    <p className={styles.loadingText}>Processing...</p>
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
};

export default LetterJoiningProblemSet;
