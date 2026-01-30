'use client'

import { useResource } from "@/context/ResourceContext"
import { useUser } from "@/context/UserContext";
import { useUserCourseProgress } from "@/context/UserCourseProgressContext";
import { VoiceTutorInput } from "@/types/request_models/VoiceTutorInput";
import { VoiceTutorQuestionInput } from "@/types/request_models/VoiceTutorQuestionInput";
import { VocabSpeakingProblemSetsResponse, VocabWordResponse } from "@/types/response_models/ResourceResponse";
import { VoiceTutorOutput } from "@/types/response_models/VoiceTutorOutput";
import { VoiceTutorQuestionOutput } from "@/types/response_models/VoiceTutorQuestionOutput";
import { useRouter } from "next/navigation";
import { useState, useEffect, useRef } from "react";
import styles from './VocabSpeakingProblemSets.module.css';

type ProgressStatus = 'unanswered' | 'current' | 'correct';

const VocabSpeakingProblemSets = () => {
    // Router
    const router = useRouter();

    // Contexts
    const {user} = useUser();
    const {userCourseProgress, setUserCourseProgress} = useUserCourseProgress();
    const {resource, setResource} = useResource();
    
    // Util States
    const [isLoading, setIsLoading] = useState<boolean>(false);
    const [error, setError] = useState<string>("");
    const [progressStatus, setProgressStatus] = useState<ProgressStatus[]>([]);

    // Audio States
    const [audioBlob, setAudioBlob] = useState<Blob | null>(null); // A Blob is a chunk of binary data
    const [isRecording, setIsRecording] = useState<boolean>(false);
    const [isPlayingQuestion, setIsPlayingQuestion] = useState<boolean>(false);
    const [isPlayingFeedback, setIsPlayingFeedback] = useState<boolean>(false);

    // Feedback States:
    const [tutorOutput, setTutorOutput] = useState<VoiceTutorOutput | null>(null);
    const [showFeedback, setShowFeedback] = useState<boolean>(false);
    const [passed, setPassed] = useState<boolean>(false);
    
    // Tutor Audio Refs
    const questionAudioRef = useRef<HTMLAudioElement | null>(null);
    const feedbackAudioRef = useRef<HTMLAudioElement | null>(null);

    // Audio Recording Refs
    const mediaRecorderRef = useRef<MediaRecorder | null>(null);
    const audioChunksRef = useRef<Blob[]>([]);

    if (!resource || !resource.resource) {
        return (
            <div className={styles.loadingContainer}>
                <div className={styles.spinner}></div>
                <p className={styles.loadingText}>Loading speaking exercise...</p>
            </div>
        );
    }

    // UserCourseProgress Fields
    const userGender = user!.gender;
    const problemCounter: number = userCourseProgress!.problem_counter;
    
    // VocabSpeakingProblemSets Data
    const problemSets = resource.resource as VocabSpeakingProblemSetsResponse;
    const problemSet = problemSets.problem_sets.find(pSet => pSet.gender === userGender);
    const problems = problemSet!.problems;
    const problem = problems[problemCounter];
    const question: string = problem.question;
    const vocabWords: VocabWordResponse[] = problem.vocab_words;
    
    // Stopping Variables
    const problemCounterStop = problemSet!.problem_count - 1;
    const exerciseComplete = problemCounter >= problemCounterStop;

    useEffect(() => {
        const handleQuestionEnd = () => setIsPlayingQuestion(false)
        const handleFeedbackEnd = () => setIsPlayingFeedback(false)

        const questionAudio = questionAudioRef.current;
        const feedbackAudio = feedbackAudioRef.current;

        questionAudio?.addEventListener("ended", handleQuestionEnd);
        feedbackAudio?.addEventListener("ended", handleFeedbackEnd)

        // When we mount this component, we setup its progress bar based on current problem
        const initialProgressStatus: ProgressStatus[] = problems.map((_, idx) => {
            if(idx < problemCounter){
                return "correct";
            } else if(idx === problemCounter){
                return "current";
            } else{
                return "unanswered"
            }
        });

        setProgressStatus(initialProgressStatus)

        return () => {
            questionAudio?.removeEventListener("ended", handleQuestionEnd);
            feedbackAudio?.removeEventListener("ended", handleFeedbackEnd);
        }
    }, []);


    useEffect(() => {
        // We reset the recorded audio and tutor response states
        setAudioBlob(null);
        setTutorOutput(null);
        setShowFeedback(false);
        setPassed(false);

        if(problemCounter < problems.length){
            // We set the current problem cell to gray.
            const newStatus = [...progressStatus]
            newStatus[problemCounter] = "current"
            setProgressStatus(newStatus)
        }
    }, [problemCounter]);


    useEffect(() => {
        if (error) {
            // Sets a timer to clear the error after 5 seconds
            const timer = setTimeout(() => setError(''), 5000);
            
            // Clean up the timer if the component unmounts
            return () => clearTimeout(timer);
        }
    }, [error]);  // Run when error changes


    const startRecording = async() => {
        try{
            // 1. We ask for permission to use user microphone and get audio from it as a stream
            const stream = await navigator.mediaDevices.getUserMedia({
                audio: {
                    channelCount: 1,
                    sampleRate: 16000
                }
            });

            // 2. We create a media recorder from the stream to save the audio, like a tape
            const mediaRecorder = new MediaRecorder(stream, {
                mimeType: "audio/webm"
            });

            mediaRecorderRef.current = mediaRecorder;
            audioChunksRef.current = [];
            
            // 3. When data is available from the media recorder, we fire a function to capture the data in the audioChunksRef
            mediaRecorder.ondataavailable = (event) => {
                if(event.data.size > 0){
                    audioChunksRef.current.push(event.data);
                }
            }

            // 4. When the mediaRecorder is stopped, we create a blob with recorded data and stop all tracks
            mediaRecorder.onstop = () => {
                // We create a blob with all the chunks we got
                const blob = new Blob(audioChunksRef.current, {
                    type: "audio/webm"
                });
                setAudioBlob(blob);

                // We stop all the tracks used to record with microphone
                stream.getTracks().forEach(track => track.stop());
            }

            // 5. We start the recording of the user audio
            mediaRecorder.start();
            setIsRecording(true);
        } catch(err){
            console.log("Microphone error: ", err);
            setError("Please allow microphone access to record your answer.")
        }
    }


    const stopRecording = () => {
        // If we have a mediaRecorder and we're recording, we stop the mediaRecorder
        if(mediaRecorderRef.current && isRecording){
            mediaRecorderRef.current.stop();
            setIsRecording(false);
        }
    }


    const handleRecordClick = () => {
        // Starts or stops recording based on isRecording
        if(isRecording){
            stopRecording();
        } else{
            startRecording();
        }
    }


    const submitAudio = async() => {
        if(!audioBlob){
            setError("Please record your answer first!");
            return;
        }

        setIsLoading(true);
        setError(""); // Reset error to capture a new one from API

        try{
            const reader = new FileReader();
            
            // We read the audio blob and get back its base64 string
            const base64Audio = await new Promise<string>((resolve, reject) => {
                reader.onloadend = () => {
                    // When we finish reading the loaded file, we get the base64 portion from the result string
                    const base64 = (reader.result as string).split(",")[1];
                    resolve(base64);
                }

                reader.onerror = reject;

                // Actually initiates the file reading process
                reader.readAsDataURL(audioBlob);
            })

            const authToken = localStorage.getItem("token");

            const requestBody: VoiceTutorInput = {
                question: question,
                language: userCourseProgress!.language,
                dialect: userCourseProgress?.dialect ?? null,
                vocab_words: vocabWords,
                user_audio_base64: base64Audio
            }

            const generatedResponse = await fetch(
                `${process.env.NEXT_PUBLIC_SERVER_URL}/voice-tutor/generate-response`,
                {
                    method: "POST",
                    headers: {
                        "Authorization": `Bearer ${authToken}`,
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify(requestBody)
                }
            )

            if(!generatedResponse.ok){
                const errorData = await generatedResponse.json();
                throw new Error(`Failed to generate feedback response: ${errorData.detail}`);
            }

            const generatedFeedback: VoiceTutorOutput = await generatedResponse.json();

            setTutorOutput(generatedFeedback);
            setShowFeedback(true);

            if(generatedFeedback.status === "pass"){
                setPassed(true);

                const newStatus = [...progressStatus];
                newStatus[problemCounter] = "correct";
                setProgressStatus(newStatus);
            } else{
                setAudioBlob(null);
            }

            // This plays the feedback audio
            if(generatedFeedback.feedback_audio && feedbackAudioRef.current){
                feedbackAudioRef.current.src = generatedFeedback.feedback_audio;
                setIsPlayingFeedback(true);
                feedbackAudioRef.current.play();
            }
        } catch(err){
            setError(err instanceof Error ? err.message : "Failed to generate feedback response");
        } finally{
            setIsLoading(false);
        }
    }


    const handleHomeNav = async () => {
        if(!exerciseComplete && progressStatus[problemCounter] === "correct"){
            setIsLoading(true);

            try{
                const authToken = localStorage.getItem("token");

                // We incremement the problem counter
                const incrementProblemCounterResponse = await fetch(
                    `${process.env.NEXT_PUBLIC_SERVER_URL}/user-course-progress/problem_counter/increment/${userCourseProgress!.id}`,
                    {
                        method: "PUT",
                        headers: {"Authorization": `Bearer ${authToken}`}
                    }
                )

                if(!incrementProblemCounterResponse.ok){
                    const errorData = await incrementProblemCounterResponse.json();
                    throw new Error(`Error in incrementing problem counter: ${errorData.detail}`)
                }

                const result = await incrementProblemCounterResponse.json();
                setUserCourseProgress(result);
            } catch(err){
                setError(err instanceof Error ? err.message : "Failed to increment problem counter")
            } finally{
                setIsLoading(false);
            }
        }

        setResource(null);
        router.replace("/");
    }


    const handleNext = async () => {
        if(exerciseComplete && progressStatus[problemCounter] === "correct"){
            const authToken = localStorage.getItem("token");
            setIsLoading(true);

            try{
                // 1. Reset the problem counter
                const resetProblemCounterResponse = await fetch(
                    `${process.env.NEXT_PUBLIC_SERVER_URL}/user-course-progress/problem_counter/clear/${userCourseProgress!.id}`,
                    {
                        method: "PUT",
                        headers: {"Authorization": `Bearer ${authToken}`}
                    }
                )

                if(!resetProblemCounterResponse.ok){
                    const errorData = await resetProblemCounterResponse.json();
                    throw new Error(`Error when resetting problem counter: ${errorData}`);
                }

                let result = await resetProblemCounterResponse.json();
                
                // 2. Update current module if applicable
                if(userCourseProgress!.curr_module === resource.number){
                    const incrementCurrModuleResponse = await fetch(
                        `${process.env.NEXT_PUBLIC_SERVER_URL}/user-course-progress/curr_module/increment/${userCourseProgress!.id}`,
                        {
                            method: "PUT",
                            headers: {"Authorization": `Bearer ${authToken}`}
                        }
                    )

                    if(!incrementCurrModuleResponse.ok){
                        const errorData = await incrementCurrModuleResponse.json();
                        throw new Error(errorData.detail);
                    }

                    result = await incrementCurrModuleResponse.json();
                }

                setUserCourseProgress(result);
                
                // 3. Navigate back to modules
                setResource(null);
                router.replace("/");
            } catch(err){
                setError(err instanceof Error ? err.message : "Error in handling next for Speaking Problems")
            } finally{
                setIsLoading(false);
            }
        } else if(!exerciseComplete && progressStatus[problemCounter] === "correct"){
            try{
                const authToken = localStorage.getItem("token");
                setIsLoading(true);

                // We incremement the problem counter
                const incrementProblemCounterResponse = await fetch(
                    `${process.env.NEXT_PUBLIC_SERVER_URL}/user-course-progress/problem_counter/increment/${userCourseProgress!.id}`,
                    {
                        method: "PUT",
                        headers: {"Authorization": `Bearer ${authToken}`}
                    }
                )

                if(!incrementProblemCounterResponse.ok){
                    const errorData = await incrementProblemCounterResponse.json();
                    throw new Error(`Error in incrementing problem counter: ${errorData.detail}`)
                }

                const result = await incrementProblemCounterResponse.json();
                setUserCourseProgress(result);
            } catch(err){
                setError(err instanceof Error ? err.message : "Failed to increment problem counter");
            } finally{
                setIsLoading(false);
            }
        }
    }


    const playQuestionAudio = async() => {
        setIsPlayingQuestion(true);
        setIsLoading(true);

        try{
            const authToken = localStorage.getItem("token");

            const requestBody: VoiceTutorQuestionInput = {
                question: question
            }

            const speakQuestionResponse = await fetch(
                `${process.env.NEXT_PUBLIC_SERVER_URL}/voice-tutor/speak_question`,
                {
                    method: "POST",
                    headers: {
                        "Authorization": `Bearer ${authToken}`,
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify(requestBody)
                }
            );

            if(!speakQuestionResponse.ok){
                const errorData = await speakQuestionResponse.json();
                throw new Error(`Error in getting question audio: ${errorData.detail}`)
            }

            const speakQuestionData: VoiceTutorQuestionOutput = await speakQuestionResponse.json();
            
            if(questionAudioRef.current && speakQuestionData.question_audio){
                questionAudioRef.current.src = speakQuestionData.question_audio;
                questionAudioRef.current.play();
            }
        } catch(err){
            setError(err instanceof Error ? err.message : "Failed to get question audio to play")
        } finally{
            setIsLoading(false);
        }
    }

    return(
        <div className={styles.container}>
            {/* Hidden Audio Elements */}
            <audio ref={questionAudioRef} />
            <audio ref={feedbackAudioRef} />

            {/* Header */}
            <div className={styles.header}>
                <button className={styles.backButton} onClick={handleHomeNav}>
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <path d="M19 12H5M12 19l-7-7 7-7" />
                    </svg>
                    Back
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
                    <h2 className={styles.questionLabel}>Question</h2>
                    <p className={styles.questionText}>{question}</p>
                    
                    {/* Question Audio Button */}
                    <div className={styles.audioPlayerContainer}>
                        <button 
                            className={styles.audioButton}
                            onClick={playQuestionAudio}
                            disabled={isLoading || isPlayingQuestion}
                        >
                            {isPlayingQuestion ? (
                                <svg viewBox="0 0 24 24" fill="currentColor">
                                    <path d="M6 4h4v16H6V4zm8 0h4v16h-4V4z"/>
                                </svg>
                            ) : (
                                <svg viewBox="0 0 24 24" fill="currentColor">
                                    <path d="M8 5v14l11-7z"/>
                                </svg>
                            )}
                        </button>
                        <div className={styles.waveContainer}>
                            <div className={`${styles.wave} ${isPlayingQuestion ? styles.active : ''}`}></div>
                            <div className={`${styles.wave} ${isPlayingQuestion ? styles.active : ''}`}></div>
                            <div className={`${styles.wave} ${isPlayingQuestion ? styles.active : ''}`}></div>
                            <div className={`${styles.wave} ${isPlayingQuestion ? styles.active : ''}`}></div>
                        </div>
                    </div>
                </div>

                {/* Vocabulary Words */}
                <div className={styles.vocabSection}>
                    <h3 className={styles.vocabLabel}>Vocabulary to Use</h3>
                    <div className={styles.vocabGrid}>
                        {vocabWords.map((vw, idx) => (
                            <div key={idx} className={styles.vocabCard}>
                                <div className={styles.vocabWord}>{vw.word}</div>
                                <div className={styles.vocabMeaning}>{vw.meaning}</div>
                            </div>
                        ))}
                    </div>
                </div>

                {/* Recording Section */}
                <div className={styles.recordingSection}>
                    <h3 className={styles.sectionTitle}>Your Answer</h3>
                    
                    <div className={styles.recordButtonContainer}>
                        <button 
                            className={`${styles.recordButton} ${isRecording ? styles.recording : ''}`}
                            onClick={handleRecordClick}
                            disabled={showFeedback && passed}
                        >
                            {isRecording ? (
                                <svg viewBox="0 0 24 24" fill="currentColor">
                                    <rect x="6" y="6" width="12" height="12" rx="2"/>
                                </svg>
                            ) : (
                                <svg viewBox="0 0 24 24" fill="currentColor">
                                    <path d="M12 15a3 3 0 100-6 3 3 0 000 6z"/>
                                    <path d="M19 10v4a7 7 0 01-14 0v-4M12 19v4M8 23h8"/>
                                </svg>
                            )}
                        </button>
                        
                        {/* Wave Animation for Recording */}
                        <div className={styles.recordWaveContainer}>
                            <div className={`${styles.recordWave} ${isRecording ? styles.active : ''}`}></div>
                            <div className={`${styles.recordWave} ${isRecording ? styles.active : ''}`}></div>
                            <div className={`${styles.recordWave} ${isRecording ? styles.active : ''}`}></div>
                            <div className={`${styles.recordWave} ${isRecording ? styles.active : ''}`}></div>
                        </div>
                    </div>

                    <p className={styles.recordingHint}>
                        {isRecording ? 'Click again to stop recording' : 'Click to start recording your answer'}
                    </p>

                    {/* Submit Button */}
                    {audioBlob && !showFeedback && (
                        <button 
                            className={styles.submitButton}
                            onClick={submitAudio}
                            disabled={isLoading}
                        >
                            {isLoading ? (
                                <>
                                    <div className={styles.buttonSpinner}></div>
                                    Evaluating...
                                </>
                            ) : (
                                <>
                                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                                        <path d="M22 2L11 13M22 2l-7 20-4-9-9-4 20-7z"/>
                                    </svg>
                                    Submit Answer
                                </>
                            )}
                        </button>
                    )}
                </div>

                {/* Feedback Section */}
                {showFeedback && tutorOutput && (
                    <div className={styles.feedbackSection}>
                        <div className={`${styles.statusBadge} ${styles[tutorOutput.status]}`}>
                            {tutorOutput.status === 'pass' ? (
                                <>
                                    <svg viewBox="0 0 24 24" fill="currentColor">
                                        <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
                                    </svg>
                                    Passed!
                                </>
                            ) : (
                                <>
                                    <svg viewBox="0 0 24 24" fill="currentColor">
                                        <path d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
                                    </svg>
                                    Try Again
                                </>
                            )}
                        </div>

                        <div className={styles.feedbackContent}>
                            <h4 className={styles.feedbackLabel}>Feedback</h4>
                            <p className={styles.feedbackText}>{tutorOutput.feedback_text}</p>
                            
                            {/* Feedback Audio Button */}
                            {tutorOutput.feedback_audio && (
                                <div className={styles.feedbackAudioContainer}>
                                    <button 
                                        className={styles.feedbackAudioButton}
                                        onClick={() => {
                                            if (feedbackAudioRef.current) {
                                                if (isPlayingFeedback) {
                                                    feedbackAudioRef.current.pause();
                                                    setIsPlayingFeedback(false);
                                                } else {
                                                    feedbackAudioRef.current.play();
                                                    setIsPlayingFeedback(true);
                                                }
                                            }
                                        }}
                                    >
                                        {isPlayingFeedback ? (
                                            <svg viewBox="0 0 24 24" fill="currentColor">
                                                <path d="M6 4h4v16H6V4zm8 0h4v16h-4V4z"/>
                                            </svg>
                                        ) : (
                                            <svg viewBox="0 0 24 24" fill="currentColor">
                                                <path d="M8 5v14l11-7z"/>
                                            </svg>
                                        )}
                                        <span>{isPlayingFeedback ? 'Pause' : 'Listen to'} Feedback</span>
                                    </button>
                                </div>
                            )}
                        </div>
                    </div>
                )}

                {/* Navigation Buttons */}
                <div className={styles.navigationSection}>
                    <button 
                        className={styles.homeButton}
                        onClick={handleHomeNav}
                    >
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                            <path d="M3 9l9-7 9 7v11a2 2 0 01-2 2H5a2 2 0 01-2-2z"/>
                            <polyline points="9 22 9 12 15 12 15 22"/>
                        </svg>
                        Home
                    </button>
                    
                    {passed && (
                        <button 
                            className={styles.nextButton}
                            onClick={handleNext}
                            disabled={isLoading}
                        >
                            {exerciseComplete ? 'Complete Module' : 'Next Question'}
                            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                                <path d="M5 12h14M12 5l7 7-7 7"/>
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
                    <div className={styles.errorContent}>
                        <svg viewBox="0 0 24 24" fill="currentColor">
                            <path d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
                        </svg>
                        <span>{error}</span>
                    </div>
                    <button 
                        className={styles.errorClose}
                        onClick={() => setError('')}
                    >
                        ×
                    </button>
                </div>
            )}
        </div>
    );
}

export default VocabSpeakingProblemSets;
