'use client'

import { useResource } from "@/context/ResourceContext"
import { useUserCourseProgress } from "@/context/UserCourseProgressContext";
import { DictationProblemSetResponse } from "@/types/response_models/ResourceResponse";
import { DictationResponse, WritingPhotoRetakeResponse } from "@/types/response_models/LetterWritingResponse";
import { DictationExplainInput } from "@/types/request_models/DictationExplainInput";
import { WritingExplainOutput } from "@/types/response_models/WritingExplainOutput";
import { useRouter } from "next/navigation";
import { useState, useEffect, useRef } from "react";
import styles from './DictationProblemSet.module.css';

type ProgressStatus = 'unanswered' | 'current' | 'correct';

const DictationProblemSet = () => {
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
                <p className={styles.loadingText}>Loading dictation problems...</p>
            </div>
        );
    }

    // UserCourseProgress
    const problemCounter = userCourseProgress!.problem_counter;
    
    // Resource
    const dictationProblemSet = resource.resource as DictationProblemSetResponse;
    const problems = dictationProblemSet.problems;
    
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

    // Audio State
    const [isPlaying, setIsPlaying] = useState<boolean>(false);
    const audioRef = useRef<HTMLAudioElement | null>(null);

    // Writing Data per problem
    const [uploadedImage, setUploadedImage] = useState<File | null>(null);
    const [imagePreview, setImagePreview] = useState<string | null>(null);
    const [dictationResponse, setDictationResponse] = useState<DictationResponse | null>(null);
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
        setUploadedImage(null);
        setImagePreview(null);
        setDictationResponse(null);
        setShowFeedback(false);
        setPassed(false);
        setIsPlaying(false);
        setQuery("");
        setFeedback([]);
        if (fileInputRef.current) {
            fileInputRef.current.value = '';
        }
        if (audioRef.current) {
            audioRef.current.pause();
            audioRef.current.currentTime = 0;
        }
    }, [problemCounter]);

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

    // Play audio
    const handlePlayAudio = () => {
        if (audioRef.current) {
            if (isPlaying) {
                audioRef.current.pause();
            } else {
                audioRef.current.play();
            }
        }
    };

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
            formData.append('target_word', problem.word);
            formData.append('language', userCourseProgress!.language);
            if (userCourseProgress!.dialect) {
                formData.append('dialect', userCourseProgress!.dialect);
            }

            const response = await fetch(
                `${process.env.NEXT_PUBLIC_SERVER_URL}/writing/dictation`,
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

            const dictationResult = result as DictationResponse;
            setDictationResponse(dictationResult);
            setFeedback([dictationResult.feedback]);
            setShowFeedback(true);

            // Check if passed
            if (dictationResult.status === 'pass') {
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

        if (!dictationResponse) {
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
            const explainRequest: DictationExplainInput = {
                query: query,
                language: userCourseProgress!.language,
                dialect: userCourseProgress?.dialect ?? null,
                target_word: problem.word,
                status: dictationResponse.status,
                scores: dictationResponse.scores,
                previous_feedback: feedback,
                mistake_tags: dictationResponse.mistake_tags,
                performance_reflection: dictationResponse.performance_reflection
            };

            const explainResponse = await fetch(
                `${process.env.NEXT_PUBLIC_SERVER_URL}/writing/dictation/explain`,
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

                // Increment current module
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
                        Write the word you heard:
                    </h1>
                    
                    {/* Audio Player with Wave Animation */}
                    <div className={styles.audioPlayerContainer}>
                        <button 
                            className={styles.audioButton}
                            onClick={handlePlayAudio}
                        >
                            {isPlaying ? (
                                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 9v6m4-6v6m7-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                                </svg>
                            ) : (
                                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                                </svg>
                            )}
                        </button>
                        
                        {/* Wave Animation */}
                        <div className={styles.waveContainer}>
                            <div className={`${styles.wave} ${isPlaying ? styles.active : ''}`}></div>
                            <div className={`${styles.wave} ${isPlaying ? styles.active : ''}`}></div>
                            <div className={`${styles.wave} ${isPlaying ? styles.active : ''}`}></div>
                            <div className={`${styles.wave} ${isPlaying ? styles.active : ''}`}></div>
                        </div>
                    </div>
                    
                    {/* Hidden Audio Element */}
                    <audio ref={audioRef} src={problem.word_audio} />
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
                {showFeedback && dictationResponse && (
                    <div className={styles.feedbackSection}>
                        <div className={styles.feedbackHeader}>
                            <h2 className={styles.feedbackTitle}>AI Feedback</h2>
                            <span className={`${styles.statusBadge} ${styles[dictationResponse.status]}`}>
                                {dictationResponse.status === 'pass' ? (
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

                        {/* Detected Word Section */}
                        <div className={styles.detectedWordSection}>
                            <div className={styles.detectedWordLabel}>AI Detected Word:</div>
                            <div className={styles.detectedWord}>{dictationResponse.detected_word}</div>
                        </div>

                        {/* Scores Grid */}
                        <div className={styles.scoresGrid}>
                            <div className={styles.scoreCard}>
                                <div className={styles.scoreLabel}>Word Accuracy</div>
                                <div className={styles.scoreValue}>
                                    {dictationResponse.scores.word_accuracy.toFixed(1)}
                                    <span className={styles.scorePercentage}>%</span>
                                </div>
                            </div>
                            <div className={styles.scoreCard}>
                                <div className={styles.scoreLabel}>Letter Identity</div>
                                <div className={styles.scoreValue}>
                                    {dictationResponse.scores.letter_identity.toFixed(1)}
                                    <span className={styles.scorePercentage}>%</span>
                                </div>
                            </div>
                            <div className={styles.scoreCard}>
                                <div className={styles.scoreLabel}>Joining Quality</div>
                                <div className={styles.scoreValue}>
                                    {dictationResponse.scores.joining_quality.toFixed(1)}
                                    <span className={styles.scorePercentage}>%</span>
                                </div>
                            </div>
                            <div className={styles.scoreCard}>
                                <div className={styles.scoreLabel}>Legibility</div>
                                <div className={styles.scoreValue}>
                                    {dictationResponse.scores.legibility.toFixed(1)}
                                    <span className={styles.scorePercentage}>%</span>
                                </div>
                            </div>
                            <div className={styles.scoreCard}>
                                <div className={styles.scoreLabel}>Dots & Diacritics</div>
                                <div className={styles.scoreValue}>
                                    {dictationResponse.scores.dots_diacritics.toFixed(1)}
                                    <span className={styles.scorePercentage}>%</span>
                                </div>
                            </div>
                            <div className={styles.scoreCard}>
                                <div className={styles.scoreLabel}>Baseline & Spacing</div>
                                <div className={styles.scoreValue}>
                                    {dictationResponse.scores.baseline_spacing.toFixed(1)}
                                    <span className={styles.scorePercentage}>%</span>
                                </div>
                            </div>
                            <div className={styles.scoreCard}>
                                <div className={styles.scoreLabel}>Overall Score</div>
                                <div className={styles.scoreValue}>
                                    {dictationResponse.scores.overall.toFixed(1)}
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
                        {dictationResponse.mistake_tags.length > 0 && (
                            <div className={styles.mistakeTags}>
                                {dictationResponse.mistake_tags.map((tag, idx) => (
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

export default DictationProblemSet;
