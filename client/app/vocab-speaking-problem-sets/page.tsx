'use client'

import { useResource } from "@/context/ResourceContext"
import { useUser } from "@/context/UserContext";
import { useUserCourseProgress } from "@/context/UserCourseProgressContext";
import { VoiceTutorInput } from "@/types/request_models/VoiceTutorInput";
import { VocabSpeakingProblemSetResponse, VocabSpeakingProblemSetsResponse, VocabWordResponse } from "@/types/response_models/ResourceResponse";
import { VoiceTutorOutput } from "@/types/response_models/VoiceTutorOutput";
import { useRouter } from "next/navigation";
import { useState, useEffect, useRef } from "react";
import styles from './VocabSpeakingProblemSets.module.css';
import { AvailableDialect, Gender } from "@/types/enums";
import { VoiceTutorTTSInput } from "@/types/request_models/VoiceTutorTTSInput";
import { VoiceTutorTTSOutput } from "@/types/response_models/VoiceTutorTTSOutput";
import { VoiceTutorExplainInput } from "@/types/request_models/VoiceTutorExplainInput";
import { VoiceTutorExplainOutput } from "@/types/response_models/VoiceTutorExplainOutput";

type ProgressStatus = 'unanswered' | 'current' | 'correct';
type AudioMode = 'listen' | 'record';
type ChatMessage = { sender: 'tutor' | 'student', text: string };

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
    const [passed, setPassed] = useState<boolean>(false);

    // Audio Recording States
    const [audioBlob, setAudioBlob] = useState<Blob | null>(null);
    const mediaRecorderRef = useRef<MediaRecorder | null>(null);
    const audioChunksRef = useRef<Blob[]>([]);

    // Audio Refs
    const playAudioRef = useRef<HTMLAudioElement | null>(null);

    // Audio Boolean States
    const [isRecording, setIsRecording] = useState<boolean>(false);
    const [isPlayingAudio, setIsPlayingAudio] = useState<boolean>(false);
    const [mode, setMode] = useState<AudioMode>("listen");

    // Feedback States
    const [tutorOutput, setTutorOutput] = useState<VoiceTutorOutput | null>(null);
    const [questionAnswered, setQuestionAnswered] = useState<boolean>(false);
    const [chatMessages, setChatMessages] = useState<ChatMessage[]>([]);
    const [query, setQuery] = useState("");

    if (!resource || !resource.resource || !userCourseProgress || !user) {
        return (
            <div className={styles.loadingContainer}>
                <div className={styles.spinner}></div>
                <p className={styles.loadingText}>Loading speaking exercise...</p>
            </div>
        );
    }

    // UserCourseProgress Fields
    const problemCounter: number = userCourseProgress.problem_counter;

    // Language data
    const language = userCourseProgress.language;
    const dialect = userCourseProgress?.dialect;
    const gender = user.gender;

    // VocabSpeakingProblemSets Data
    const vocabSpeakingProblemSets = resource.resource as VocabSpeakingProblemSetsResponse;
    const problemSets = vocabSpeakingProblemSets.problem_sets;

    const problemSet = problemSets.find(ps => 
        ps.dialect === dialect && (!ps.gender || ps.gender === gender)
    ) ?? null;

    // Safety check: ensure problem set exists
    if (!problemSet || !problemSet.problems || problemSet.problems.length === 0) {
        return (
            <div className={styles.loadingContainer}>
                <div className={styles.spinner}></div>
                <p className={styles.loadingText}>
                    No speaking problems available for your gender and dialect combination: {gender}, {dialect}.
                </p>
            </div>
        );
    }

    const problems = problemSet.problems;

    if (problemCounter >= problems.length || problemCounter < 0) {
        return (
            <div className={styles.loadingContainer}>
                <div className={styles.spinner}></div>
                <p className={styles.loadingText}>
                    Problem counter out of sync. Resetting...
                </p>
            </div>
        );
    }

    const problem = problems[problemCounter];
    const question: string = problem.question;
    const vocabWords: VocabWordResponse[] = problem.vocab_words;

    // Stopping Variables
    const problemCounterStop = problemSet.problem_count - 1;
    const exerciseComplete = problemCounter >= problemCounterStop;
    

    useEffect(() => {
        const handlePlayAudioEnd = () => setIsPlayingAudio(false);
        const audioPlayer = playAudioRef.current;
        audioPlayer?.addEventListener("ended", handlePlayAudioEnd);

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
            audioPlayer?.removeEventListener("ended", handlePlayAudioEnd);
        }
    }, []);


    const startRecording = async() => {
        try{ 
            // We clear the previous audio
            setAudioBlob(null);
            audioChunksRef.current = [];

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
            
            // 3. When data is available from the media recorder, we fire a function to capture the data in the audioChunksRef
            mediaRecorder.ondataavailable = (event) => {
                if(event.data.size > 0){
                    audioChunksRef.current.push(event.data); // We're basically pushing a small audio blob
                }
            }

            // 4. When the mediaRecorder is stopped, we create a blob with recorded data and stop all tracks
            mediaRecorder.onstop = () => {
                // We create a blob with all the chunks (blobs) we got
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
            setError(`Please allow microphone access to record your answer.`)
        }
    }


    const stopRecording = () => {
        // If we have a mediaRecorder and we're recording, we stop the mediaRecorder
        if(mediaRecorderRef.current && isRecording){
            mediaRecorderRef.current.stop();
            setIsRecording(false);
        }
    }


    const handleModeToggle = (newMode: AudioMode) => {
        // Don't allow mode switch while recording
        if (isRecording && newMode === 'listen') {
            setError("Please stop recording before switching to listen mode.");
            return;
        }
        setMode(newMode);
    }

    const handleAudioButtonClick = () => {
        if (mode === 'listen') {
            // Play the question audio
            if (!isPlayingAudio) {
                playAudio(question);
            }
        } else if (mode === 'record') {
            // Start or stop recording
            if (isRecording) {
                stopRecording();
            } else {
                startRecording();
            }
        }
    }


    const handleSubmitAudio = async() => {
        // Submits the recorded audio to get back the tutor response
        if(!audioBlob){
            setError("Please record your answer first!");
            return;
        }

        const authToken = localStorage.getItem("token");
        if (!authToken) {
            setError("Authentication required. Please log in.");
            router.replace("/login");
            return;
        }

        setIsLoading(true);
        setMode("listen");

        try{
            const reader = new FileReader();
            
            // 1. We read the audio blob and get back its base64 string
            const base64Audio = await new Promise<string>((resolve, reject) => {
                reader.onloadend = () => {
                    const base64 = (reader.result as string).split(",")[1];
                    resolve(base64);
                }
                reader.onerror = reject;
                reader.readAsDataURL(audioBlob);
            })

            // 2. We get back the voice tutor response
            const requestBody: VoiceTutorInput = {
                question: question,
                language: language,
                dialect: dialect ?? null,
                vocab_words: vocabWords,
                user_audio_base64: base64Audio
            }

            const generatedResponse = await fetch(
                `${process.env.NEXT_PUBLIC_SERVER_URL}/speaking/generate-response`,
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
                throw new Error(errorData.detail || "Failed to generate feedback response");
            }

            const generatedFeedback: VoiceTutorOutput = await generatedResponse.json();

            setTutorOutput(generatedFeedback);
            setQuestionAnswered(true);

            // 3. Update the progress bar if we had a correct answer
            if(generatedFeedback.status === "pass"){
                setPassed(true);
                const newStatus = [...progressStatus];
                newStatus[problemCounter] = "correct";
                setProgressStatus(newStatus);
            }

            // 4. Set initial chat message with tutor feedback
            const generatedFeedbackText = generatedFeedback.feedback_text;
            if(generatedFeedbackText){
                setChatMessages([{ sender: 'tutor', text: generatedFeedbackText }]);
            }

            // 5. Play feedback audio
            if(generatedFeedback.feedback_audio_base64 && playAudioRef.current){
                const audio = playAudioRef.current;

                // We make sure to pause the previous audio if present and reset to the beginning of the audio file
                audio.pause();
                audio.currentTime = 0;

                audio.src = generatedFeedback.feedback_audio_base64;
                setIsPlayingAudio(true);
                try{
                    await audio.play();
                } catch(err){
                    setIsPlayingAudio(false);
                }
            }
        } catch(err){
            setError(err instanceof Error ? err.message : "Failed to generate feedback response");
        } finally{
            setIsLoading(false);
        }
    }


    const handleAskQuestion = async () => {
        // Answers the passed in query regarding user performance on a question
        if (!query.trim()) {
            setError("Please enter a question.");
            return;
        }

        if (!tutorOutput) {
            setError("No tutor feedback available yet.");
            return;
        }

        const authToken = localStorage.getItem("token");
        if (!authToken) {
            setError("Authentication required. Please log in.");
            router.replace("/login");
            return;
        }

        setIsLoading(true);

        try{
            // 1. Build the previous feedback array from chat messages
            const previousFeedback = chatMessages.map(msg => 
                `${msg.sender === 'tutor' ? 'Tutor' : 'Student'}: ${msg.text}`
            );

            // 2. We generate the response to user query
            const explainRequest: VoiceTutorExplainInput = {
                query: query,
                question: question,
                language: language,
                dialect: dialect ?? null,
                vocab_words: vocabWords,
                transcription: tutorOutput.transcription,
                pronounciation_scores: tutorOutput.pronounciation_scores,
                semantic_evaluation: tutorOutput.semantic_evaluation,
                status: tutorOutput.status as "pass" | "fail",
                performance_reflection: tutorOutput.performance_reflection,
                previous_feedback: previousFeedback
            }

            const explainResponse = await fetch(
                `${process.env.NEXT_PUBLIC_SERVER_URL}/speaking/explain`,
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
                throw new Error(errorData.detail || "Failed to generate explain response");
            }

            const explainData: VoiceTutorExplainOutput = await explainResponse.json();
            const responseText = explainData.response_text;
            
            if(!responseText){
                throw new Error("Did not get back response text for speaking explain");
            }

            // 3. Add the student question and tutor response to chat
            const newMessages: ChatMessage[] = [
                ...chatMessages,
                { sender: 'student', text: query },
                { sender: 'tutor', text: responseText }
            ];
            setChatMessages(newMessages);
            setQuery(""); // Clear the input

            // 4. Play the explain response audio
            playAudio(responseText);
        } catch(err){
            setError(err instanceof Error ? err.message : "Failed to generate explain");
        } finally{
            setIsLoading(false);
        }
    }


    const resetQuestion = () => {
        // We reset our previous data
        // Can be used to retry the question
        setError("");
        setAudioBlob(null);
        setChatMessages([]);
        setTutorOutput(null);
        setQuestionAnswered(false);
        setQuery("");
        setMode("listen");
        audioChunksRef.current = [];
    }


    const handleHomeNav = async () => {
        // Handles navigation to home page in middle of exercise.
        // We increment the problem counter before nav only if we answered non-end problem correctly.
        if(!exerciseComplete && passed){
            const authToken = localStorage.getItem("token");
            if (!authToken) {
                setError("Authentication required. Please log in.");
                router.replace("/login");
                return;
            }

            setIsLoading(true);

            try{
                // We increment the problem counter
                const incrementProblemCounterResponse = await fetch(
                    `${process.env.NEXT_PUBLIC_SERVER_URL}/user-course-progress/problem-counter/increment/${userCourseProgress!.id}`,
                    {
                        method: "PUT",
                        headers: {"Authorization": `Bearer ${authToken}`}
                    }
                )

                if(!incrementProblemCounterResponse.ok){
                    const errorData = await incrementProblemCounterResponse.json();
                    throw new Error(errorData.detail || "Failed to increment problem counter")
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
        // Handles going to the next problem or completing the exercise.
        const authToken = localStorage.getItem("token");
        if (!authToken) {
            setError("Authentication required. Please log in.");
            router.replace("/login");
            return;
        }

        if(exerciseComplete && passed){
            resetQuestion();
            setIsLoading(true);

            try{
                // 1. Reset the problem counter
                const resetProblemCounterResponse = await fetch(
                    `${process.env.NEXT_PUBLIC_SERVER_URL}/user-course-progress/problem-counter/clear/${userCourseProgress!.id}`,
                    {
                        method: "PUT",
                        headers: {"Authorization": `Bearer ${authToken}`}
                    }
                )

                if(!resetProblemCounterResponse.ok){
                    const errorData = await resetProblemCounterResponse.json();
                    throw new Error(errorData.detail || "Failed to reset problem counter");
                }

                let result = await resetProblemCounterResponse.json();
                
                // 2. Update current module if applicable
                if(userCourseProgress!.curr_module === resource.number){
                    const incrementCurrModuleResponse = await fetch(
                        `${process.env.NEXT_PUBLIC_SERVER_URL}/user-course-progress/curr-module/increment/${userCourseProgress!.id}`,
                        {
                            method: "PUT",
                            headers: {"Authorization": `Bearer ${authToken}`}
                        }
                    )

                    if(!incrementCurrModuleResponse.ok){
                        const errorData = await incrementCurrModuleResponse.json();
                        throw new Error(errorData.detail || "Failed to increment current module");
                    }

                    result = await incrementCurrModuleResponse.json();
                }

                setUserCourseProgress(result);
                
                // 3. Navigate back to modules
                setResource(null);
                router.replace("/");
            } catch(err){
                setError(err instanceof Error ? err.message : "Error completing module")
            } finally{
                setIsLoading(false);
            }
        } else if(!exerciseComplete && passed){
            resetQuestion();
            setIsLoading(true);

            try{
                // We increment the problem counter
                const incrementProblemCounterResponse = await fetch(
                    `${process.env.NEXT_PUBLIC_SERVER_URL}/user-course-progress/problem-counter/increment/${userCourseProgress!.id}`,
                    {
                        method: "PUT",
                        headers: {"Authorization": `Bearer ${authToken}`}
                    }
                )

                if(!incrementProblemCounterResponse.ok){
                    const errorData = await incrementProblemCounterResponse.json();
                    throw new Error(errorData.detail || "Failed to increment problem counter")
                }

                const result = await incrementProblemCounterResponse.json();
                setUserCourseProgress(result);
                setPassed(false);
            } catch(err){
                setError(err instanceof Error ? err.message : "Failed to increment problem counter");
            } finally{
                setIsLoading(false);
            }
        }
    }


    const playAudio = async(text: string) => {
        // Plays the passed in audio
        const authToken = localStorage.getItem("token");
        if (!authToken) {
            setError("Authentication required. Please log in.");
            router.replace("/login");
            return;
        }

        setIsPlayingAudio(true);
        setIsLoading(true);

        try{
            const requestBody: VoiceTutorTTSInput = {
                text: text
            }

            const speakResponse = await fetch(
                `${process.env.NEXT_PUBLIC_SERVER_URL}/speaking/speak-question`,
                {
                    method: "POST",
                    headers: {
                        "Authorization": `Bearer ${authToken}`,
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify(requestBody)
                }
            );

            if(!speakResponse.ok){
                const errorData = await speakResponse.json();
                throw new Error(errorData.detail || "Failed to get audio")
            }

            const speakData: VoiceTutorTTSOutput = await speakResponse.json();
            
            if(playAudioRef.current && speakData.response_audio_base64){
                const audio = playAudioRef.current;

                // We make sure to pause the previous audio if present and reset to the beginning of the audio file
                audio.pause();
                audio.currentTime = 0;

                audio.src = speakData.response_audio_base64;
                try{
                    await audio.play();
                } catch(err){
                    setIsPlayingAudio(false);
                }
            }
        } catch(err){
            setError(err instanceof Error ? err.message : "Failed to get and play audio");
        } finally{
            setIsLoading(false);
        }
    }


    return(
        <div className={styles.container}>
            {/* Hidden Audio Elements */}
            <audio ref={playAudioRef} />

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
                {!questionAnswered ? (
                    /* Pre-Answer View */
                    <div className={styles.questionView}>
                        <h2 className={styles.instructionText}>
                            Listen to the question and record your response.
                        </h2>

                        {/* Mode Toggle */}
                        <div className={styles.modeToggle}>
                            <button
                                className={`${styles.modeButton} ${mode === 'listen' ? styles.active : ''}`}
                                onClick={() => handleModeToggle('listen')}
                                disabled={isLoading}
                            >
                                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                                    <polygon points="5 3 19 12 5 21 5 3"/>
                                </svg>
                                Listen
                            </button>
                            <button
                                className={`${styles.modeButton} ${mode === 'record' ? styles.active : ''}`}
                                onClick={() => handleModeToggle('record')}
                                disabled={isLoading}
                            >
                                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                                    <circle cx="12" cy="12" r="3"/>
                                    <path d="M19 10v4a7 7 0 01-14 0v-4M12 19v4M8 23h8"/>
                                </svg>
                                Record
                            </button>
                        </div>

                        {/* Main Audio Button */}
                        <div className={styles.audioButtonContainer}>
                            <button
                                className={`${styles.mainAudioButton} ${
                                    mode === 'listen' ? styles.listenMode : styles.recordMode
                                } ${isRecording ? styles.recording : ''} ${isPlayingAudio ? styles.playing : ''}`}
                                onClick={handleAudioButtonClick}
                                disabled={isLoading}
                            >
                                {mode === 'listen' ? (
                                    isPlayingAudio ? (
                                        <div className={styles.waveAnimation}>
                                            <div className={styles.wave}></div>
                                            <div className={styles.wave}></div>
                                            <div className={styles.wave}></div>
                                            <div className={styles.wave}></div>
                                        </div>
                                    ) : (
                                        <svg viewBox="0 0 24 24" fill="currentColor">
                                            <polygon points="5 3 19 12 5 21 5 3"/>
                                        </svg>
                                    )
                                ) : (
                                    isRecording ? (
                                        <svg viewBox="0 0 24 24" fill="currentColor">
                                            <rect x="6" y="6" width="12" height="12" rx="2"/>
                                        </svg>
                                    ) : (
                                        <svg viewBox="0 0 24 24" fill="currentColor">
                                            <circle cx="12" cy="12" r="8"/>
                                        </svg>
                                    )
                                )}
                            </button>
                            <p className={styles.audioButtonHint}>
                                {mode === 'listen' 
                                    ? (isPlayingAudio ? 'Playing question...' : 'Click to listen to the question')
                                    : (isRecording ? 'Click to stop recording' : (audioBlob ? 'Click to re-record' : 'Click to start recording'))}
                            </p>
                        </div>

                        {/* Submit Button */}
                        {audioBlob && (
                            <button
                                className={styles.submitButton}
                                onClick={handleSubmitAudio}
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
                ) : (
                    /* Post-Answer View */
                    <div className={styles.answerView}>
                        {/* Status Badge */}
                        <div className={`${styles.statusBadge} ${styles[tutorOutput?.status || 'fail']}`}>
                            {tutorOutput?.status === 'pass' ? (
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

                        {/* Question Section */}
                        <div className={styles.questionSection}>
                            <h3 className={styles.sectionTitle}>Question</h3>
                            <div className={styles.questionCard} onClick={() => playAudio(question)}>
                                <p className={styles.questionText}>{question}</p>
                                <button className={styles.playIconButton}>
                                    <svg viewBox="0 0 24 24" fill="currentColor">
                                        <polygon points="5 3 19 12 5 21 5 3"/>
                                    </svg>
                                </button>
                            </div>
                        </div>

                        {/* Vocabulary Words */}
                        <div className={styles.vocabSection}>
                            <h3 className={styles.sectionTitle}>Vocabulary Words</h3>
                            <div className={styles.vocabGrid}>
                                {vocabWords.map((vw, idx) => (
                                    <div key={idx} className={styles.vocabCard}>
                                        <div className={styles.vocabWord}>{vw.word}</div>
                                        <div className={styles.vocabMeaning}>{vw.meaning}</div>
                                    </div>
                                ))}
                            </div>
                        </div>

                        {/* Chat Interface */}
                        <div className={styles.chatSection}>
                            <h3 className={styles.sectionTitle}>Feedback & Questions</h3>
                            <div className={styles.chatMessages}>
                                {chatMessages.map((message, idx) => (
                                    <div
                                        key={idx}
                                        className={`${styles.chatMessage} ${
                                            message.sender === 'tutor' ? styles.tutorMessage : styles.studentMessage
                                        }`}
                                        onClick={() => message.sender === 'tutor' && playAudio(message.text)}
                                    >
                                        <p className={styles.messageText}>{message.text}</p>
                                        {message.sender === 'tutor' && (
                                            <button className={styles.playMessageButton}>
                                                <svg viewBox="0 0 24 24" fill="currentColor">
                                                    <polygon points="5 3 19 12 5 21 5 3"/>
                                                </svg>
                                            </button>
                                        )}
                                    </div>
                                ))}
                            </div>

                            {/* Chat Input */}
                            <div className={styles.chatInputContainer}>
                                <input
                                    className={styles.chatInput}
                                    type="text"
                                    value={query}
                                    onChange={(e) => setQuery(e.target.value)}
                                    onKeyPress={(e) => e.key === 'Enter' && !isLoading && query.trim() && handleAskQuestion()}
                                    placeholder="Ask a follow-up question..."
                                    disabled={isLoading}
                                />
                                <button
                                    className={styles.sendButton}
                                    onClick={handleAskQuestion}
                                    disabled={isLoading || !query.trim()}
                                >
                                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                                        <path d="M22 2L11 13M22 2l-7 20-4-9-9-4 20-7z"/>
                                    </svg>
                                </button>
                            </div>
                        </div>

                        {/* Try Again Button (if failed) */}
                        {!passed && (
                            <button
                                className={styles.tryAgainButton}
                                onClick={resetQuestion}
                                disabled={isLoading}
                            >
                                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                                    <path d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
                                    <path d="M9 12l2 2 4-4"/>
                                </svg>
                                Try Again
                            </button>
                        )}
                    </div>
                )}

                {/* Navigation Buttons */}
                <div className={styles.navigationSection}>
                    <button 
                        className={styles.homeButton}
                        onClick={handleHomeNav}
                        disabled={isLoading}
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