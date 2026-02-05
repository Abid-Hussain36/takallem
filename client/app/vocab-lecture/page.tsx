'use client'

import { useResource } from "@/context/ResourceContext"
import { VocabLectureResponse, VocabWordResponse } from "@/types/response_models/ResourceResponse";
import styles from './VocabLecture.module.css';
import { useRouter } from "next/navigation";
import { useUserCourseProgress } from "@/context/UserCourseProgressContext";
import { useState, useMemo, useRef } from "react";
import { useUser } from "@/context/UserContext";
import { useModules } from "@/context/ModulesContext";


const VocabLecture = () => {
    const router = useRouter();

    const {resource, setResource} = useResource();
    const {setUser} = useUser();
    const {userCourseProgress, setUserCourseProgress} = useUserCourseProgress();
    const {setModules} = useModules();

    const [isLoading, setIsLoading] = useState<boolean>(false)
    const [error, setError] = useState<string>("")
    const [playingWordId, setPlayingWordId] = useState<number | null>(null);
    
    const audioRef = useRef<HTMLAudioElement | null>(null);

    // Filter vocab words by user's dialect (must be before early return to follow hooks rules)
    const filteredVocabWords = useMemo(() => {
        if (!resource?.resource) return [];
        
        const lectureData = resource.resource as VocabLectureResponse;
        const userDialect = userCourseProgress?.dialect;
        
        if (!userDialect) {
            // If no dialect selected, show all words or words with null dialect
            return lectureData.vocab_words.filter(word => word.dialect === null);
        }
        
        // Show words matching user's dialect or universal words (null dialect)
        // Compare case-insensitively to handle potential mismatches
        const filtered = lectureData.vocab_words.filter(
            word => word.dialect === null || 
                    word.dialect === userDialect ||
                    word.dialect?.toUpperCase() === userDialect.toUpperCase()
        );
        
        return filtered;
    }, [resource?.resource, userCourseProgress?.dialect]);

    if (!resource || !resource.resource) {
        return <div className={styles.loading}>Loading vocabulary...</div>;
    }

    const lectureData = resource.resource as VocabLectureResponse;

    const handleHomeNav = () => {
        setResource(null);
        router.replace("/");
    }

    const handleNext = async () => {
        // Prevent multiple clicks while loading
        if (isLoading) {
            return;
        }

        const authToken = localStorage.getItem("token");

        if (!authToken) {
            setError("User is not authenticated");
            setUser(null);
            setUserCourseProgress(null);
            setModules(null);
            setResource(null);
            router.replace("/login");
            return;
        }

        // Increment current module ONLY if we're currently on this module
        // This prevents double-increments if the user revisits this page
        if(userCourseProgress?.curr_module === resource.number){
            try {
                setIsLoading(true);

                const incrementUserCourseProgress = await fetch(
                    `${process.env.NEXT_PUBLIC_SERVER_URL}/user-course-progress/curr-module/increment/${userCourseProgress.id}`,
                    {
                        method: "PUT",
                        headers: {
                            'Authorization': `Bearer ${authToken}`,
                            'Content-Type': 'application/json'
                        }
                    }
                )

                if(!incrementUserCourseProgress.ok){
                    const errorData = await incrementUserCourseProgress.json();
                    throw new Error(errorData.detail || "Failed to increment userCourseProgress")
                }

                const updatedProgress = await incrementUserCourseProgress.json();
                setUserCourseProgress(updatedProgress);
            } catch(err){
                setError(err instanceof Error ? err.message : "Error in updating userCourseProgress.");
            } finally{
                setIsLoading(false);
            }
        }

        setResource(null);
        router.replace("/")
    }

    const handleWordClick = (word: VocabWordResponse) => {
        // Stop any currently playing audio
        if (audioRef.current) {
            audioRef.current.pause();
            audioRef.current.currentTime = 0;
        }
        
        // Set the audio source and play
        if (audioRef.current && word.vocab_audio) {
            audioRef.current.src = word.vocab_audio;
            audioRef.current.play()
                .then(() => setPlayingWordId(word.id))
                .catch(err => setError(err instanceof Error ? err.message : "Failed to play audio."));
        }
    }

    const handleAudioEnded = () => {
        setPlayingWordId(null);
    }

    return(
        <div className={styles.container}>
            {/* Top Bar with Metadata */}
            <div className={styles.topBar}>
                <div className={styles.breadcrumb}>
                    <span className={styles.course}>{resource.course}</span>
                    <span className={styles.separator}>›</span>
                    <span className={styles.unit}>{resource.unit}</span>
                    <span className={styles.separator}>›</span>
                    <span className={styles.section}>{resource.section}</span>
                </div>
                <div className={styles.lectureHeader}>
                    <h1 className={styles.title}>{resource.title}</h1>
                    <span className={styles.moduleNumber}>Module {resource.number}</span>
                </div>
            </div>

            {/* Content Area */}
            <div className={styles.contentWrapper}>
                <div className={styles.content}>
                    <div className={styles.vocabInfo}>
                        <h2 className={styles.vocabTitle}>Vocabulary Words</h2>
                        <p className={styles.vocabSubtitle}>
                            {userCourseProgress?.dialect 
                                ? `Showing words for ${userCourseProgress.dialect} dialect`
                                : "Showing universal vocabulary"}
                        </p>
                    </div>

                    {filteredVocabWords.length === 0 ? (
                        <div className={styles.emptyState}>
                            <p>No vocabulary words available for your dialect.</p>
                        </div>
                    ) : (
                        <div className={styles.tableWrapper}>
                            <audio ref={audioRef} onEnded={handleAudioEnded} />
                            <table className={styles.vocabTable}>
                                <thead>
                                    <tr>
                                        <th className={styles.meaningHeader}>Meaning</th>
                                        <th className={styles.arabicHeader}>Arabic</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {filteredVocabWords.map((word) => (
                                        <tr key={word.id} className={styles.vocabRow}>
                                            <td className={styles.meaningCell}>{word.meaning}</td>
                                            <td className={styles.arabicCell}>
                                                <button 
                                                    className={`${styles.arabicButton} ${playingWordId === word.id ? styles.playing : ''}`}
                                                    onClick={() => handleWordClick(word)}
                                                    aria-label={`Play audio for ${word.word}`}
                                                >
                                                    {word.word}
                                                    <svg className={styles.audioIcon} xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                                                        {playingWordId === word.id ? (
                                                            <path d="M6 4h2v12H6V4zm6 0h2v12h-2V4z" />
                                                        ) : (
                                                            <path d="M10 3.75a2 2 0 10-4 0v8.5a2 2 0 104 0v-8.5zM17.25 8a.75.75 0 00-1.5 0v4a.75.75 0 001.5 0V8zM4.5 8a.75.75 0 00-1.5 0v4a.75.75 0 001.5 0V8z" />
                                                        )}
                                                    </svg>
                                                </button>
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    )}
                </div>
            </div>

            {/* Navigation Footer */}
            <div className={styles.footer}>
                <button 
                    className={styles.homeButton}
                    onClick={handleHomeNav}
                >
                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                        <path fillRule="evenodd" d="M9.293 2.293a1 1 0 011.414 0l7 7A1 1 0 0117 11h-1v6a1 1 0 01-1 1h-2a1 1 0 01-1-1v-3a1 1 0 00-1-1H9a1 1 0 00-1 1v3a1 1 0 01-1 1H5a1 1 0 01-1-1v-6H3a1 1 0 01-.707-1.707l7-7z" clipRule="evenodd" />
                    </svg>
                    Home
                </button>
                <button 
                    className={styles.continueButton}
                    onClick={handleNext}
                    disabled={isLoading}
                >
                    {isLoading ? 'Loading...' : 'Continue'}
                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                        <path fillRule="evenodd" d="M3 10a.75.75 0 01.75-.75h10.638L10.23 5.29a.75.75 0 111.04-1.08l5.5 5.25a.75.75 0 010 1.08l-5.5 5.25a.75.75 0 11-1.04-1.08l4.158-3.96H3.75A.75.75 0 013 10z" clipRule="evenodd" />
                    </svg>
                </button>
            </div>

            {error && (
                <div className={styles.errorToast}>
                    {error}
                </div>
            )}
        </div>
    );
}

export default VocabLecture;
