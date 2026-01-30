'use client'

import { useResource } from "@/context/ResourceContext"
import { useUserCourseProgress } from "@/context/UserCourseProgressContext";
import { LetterWritingProblemSetResponse } from "@/types/response_models/ResourceResponse";
import { LetterWritingResponse, WritingPhotoRetakeResponse } from "@/types/response_models/LetterWritingResponse";
import { useRouter } from "next/navigation";
import { useState, useEffect, useRef } from "react";
import styles from './LetterWritingProblemSet.module.css';

type ProgressStatus = 'unanswered' | 'current' | 'correct';

const LetterWritingProblemSet = () => {
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
                <p className={styles.loadingText}>Loading letter writing problems...</p>
            </div>
        );
    }

    // UserCourseProgress
    const problemCounter = userCourseProgress!.problem_counter;
    
    // Resource
    const letterWritingProblemSet = resource.resource as LetterWritingProblemSetResponse;
    const problems = letterWritingProblemSet.problems;
    const problem = problems[problemCounter];

    // Writing Data per problem
    const [uploadedImage, setUploadedImage] = useState<File | null>(null);
    const [imagePreview, setImagePreview] = useState<string | null>(null);
    const [writingResponse, setWritingResponse] = useState<LetterWritingResponse | null>(null);
    const [showFeedback, setShowFeedback] = useState<boolean>(false);
    const [passed, setPassed] = useState<boolean>(false);
    
    const fileInputRef = useRef<HTMLInputElement>(null);

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
        setWritingResponse(null);
        setShowFeedback(false);
        setPassed(false);
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

        setIsLoading(true);
        setError('');

        try {
            const authToken = localStorage.getItem("token");
            const formData = new FormData();
            
            formData.append('user_image', uploadedImage);
            
            // Fetch the reference image
            const referenceResponse = await fetch(problem.reference_writing);
            const referenceBlob = await referenceResponse.blob();
            const referenceFile = new File([referenceBlob], 'reference.png', { type: 'image/png' });
            formData.append('target_image', referenceFile);
            
            formData.append('letter', problem.letter);
            formData.append('position', problem.position);

            const response = await fetch(
                `${process.env.NEXT_PUBLIC_SERVER_URL}/letter/writing/alphabet`,
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

            const writingResult = result as LetterWritingResponse;
            setWritingResponse(writingResult);
            setShowFeedback(true);

            // Check if passed
            if (writingResult.status === 'pass') {
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

    // Navigate home
    const handleHomeNav = () => {
        setResource(null);
        router.replace("/");
    };

    // Handle next button
    const handleNext = async () => {
        if (allProblemsCompleted) {
            // All problems completed, increment module
            setIsLoading(true);
            const authToken = localStorage.getItem("token");

            try {
                // Reset problem counter
                const resetCounterResponse = await fetch(
                    `${process.env.NEXT_PUBLIC_SERVER_URL}/user-course-progress/problem_counter/clear/${userCourseProgress!.id}`,
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
                    `${process.env.NEXT_PUBLIC_SERVER_URL}/user-course-progress/curr_module/increment/${userCourseProgress!.id}`,
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
            const authToken = localStorage.getItem("token");

            try {
                const incrementResponse = await fetch(
                    `${process.env.NEXT_PUBLIC_SERVER_URL}/user-course-progress/problem_counter/increment/${userCourseProgress!.id}`,
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
                        Write the letter in {problem.position} position:
                    </h1>
                    <div className={styles.letterDisplay}>
                        {problem.letter}
                    </div>
                    <span className={styles.positionBadge}>
                        {problem.position} Form
                    </span>
                </div>

                {/* Reference Sequence Section */}
                <div className={styles.referenceSection}>
                    <h2 className={styles.referenceTitle}>
                        Writing Sequence Reference
                    </h2>
                    <div className={styles.sequenceContainer}>
                        {[...problem.writing_sequence.sequence_images].reverse().map((image, idx, arr) => (
                            <div key={idx} style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                                <img 
                                    src={image} 
                                    alt={`Step ${arr.length - idx}`}
                                    className={styles.sequenceImage}
                                />
                                
                                {idx < arr.length - 1 && (
                                    <div className={styles.arrow}>
                                        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M13 7l-5 5 5 5" />
                                        </svg>
                                    </div>
                                )}
                            </div>
                        ))}
                    </div>
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
                {showFeedback && writingResponse && (
                    <div className={styles.feedbackSection}>
                        <div className={styles.feedbackHeader}>
                            <h2 className={styles.feedbackTitle}>AI Feedback</h2>
                            <span className={`${styles.statusBadge} ${styles[writingResponse.status]}`}>
                                {writingResponse.status === 'pass' ? (
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
                                <div className={styles.scoreLabel}>Legibility</div>
                                <div className={styles.scoreValue}>
                                    {writingResponse.scores.legibility.toFixed(1)}
                                    <span className={styles.scorePercentage}>%</span>
                                </div>
                            </div>
                            <div className={styles.scoreCard}>
                                <div className={styles.scoreLabel}>Form Accuracy</div>
                                <div className={styles.scoreValue}>
                                    {writingResponse.scores.form_accuracy.toFixed(1)}
                                    <span className={styles.scorePercentage}>%</span>
                                </div>
                            </div>
                            <div className={styles.scoreCard}>
                                <div className={styles.scoreLabel}>Dots & Diacritics</div>
                                <div className={styles.scoreValue}>
                                    {writingResponse.scores.dots_diacritics.toFixed(1)}
                                    <span className={styles.scorePercentage}>%</span>
                                </div>
                            </div>
                            <div className={styles.scoreCard}>
                                <div className={styles.scoreLabel}>Baseline & Proportion</div>
                                <div className={styles.scoreValue}>
                                    {writingResponse.scores.baseline_proportion.toFixed(1)}
                                    <span className={styles.scorePercentage}>%</span>
                                </div>
                            </div>
                            <div className={styles.scoreCard}>
                                <div className={styles.scoreLabel}>Overall Score</div>
                                <div className={styles.scoreValue}>
                                    {writingResponse.scores.overall.toFixed(1)}
                                    <span className={styles.scorePercentage}>%</span>
                                </div>
                            </div>
                        </div>

                        {/* Feedback Text */}
                        <div className={styles.feedbackText}>
                            {writingResponse.feedback}
                        </div>

                        {/* Mistake Tags */}
                        {writingResponse.mistake_tags.length > 0 && (
                            <div className={styles.mistakeTags}>
                                {writingResponse.mistake_tags.map((tag, idx) => (
                                    <span key={idx} className={styles.mistakeTag}>
                                        {tag}
                                    </span>
                                ))}
                            </div>
                        )}
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
                <div className={styles.error}>
                    {error}
                </div>
            )}
        </div>
    );
};

export default LetterWritingProblemSet;
