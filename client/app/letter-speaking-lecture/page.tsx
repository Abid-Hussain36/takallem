'use client'

import { useResource } from "@/context/ResourceContext"
import { LetterSpeakingLectureResponse } from "@/types/response_models/ResourceResponse";
import ReactMarkdown from 'react-markdown';
import styles from './LetterSpeakingLecture.module.css';
import { useRouter } from "next/navigation";
import { useUserCourseProgress } from "@/context/UserCourseProgressContext";
import { useState, useEffect, useRef } from "react";

const LetterSpeakingLecture = () => {
    const router = useRouter();

    const {resource, setResource} = useResource();
    const {userCourseProgress, setUserCourseProgress} = useUserCourseProgress();

    const [isLoading, setIsLoading] = useState<boolean>(false);
    const [error, setError] = useState<string>("");
    const [stage, setStage] = useState<'initial' | 'content'>('initial');
    const [isPlaying, setIsPlaying] = useState<boolean>(false);
    const [hasPlayedOnce, setHasPlayedOnce] = useState<boolean>(false);

    const audioRef = useRef<HTMLAudioElement | null>(null);

    if (!resource || !resource.resource) {
        return <div className={styles.loading}>Loading lecture...</div>;
    }

    const lectureData = resource.resource as LetterSpeakingLectureResponse;
    const letter = lectureData.letter;
    const letterAudio = lectureData.letter_audio;
    const wordAudios = lectureData.word_audios;
    const content = lectureData.content;

    // Extract letter from title (format: "ا — Alif")
    const titleParts = resource.title.split(' — ');
    const letterChar = titleParts[0];
    const letterName = titleParts[1] || '';

    // Audio event listeners
    useEffect(() => {
        const audio = audioRef.current;
        if (!audio) return;

        const handleAudioEnd = () => {
            setIsPlaying(false);
            setHasPlayedOnce(true);
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
    }, []); // Empty array - setup once on mount

    const handlePlayLetter = async () => {
        if (audioRef.current) {
            if (isPlaying) {
                audioRef.current.pause();
            } else {
                try {
                    await audioRef.current.play();
                } catch (err) {
                    console.error("Failed to play audio:", err);
                    setError("Failed to play audio. Please try again.");
                }
            }
        }
    };

    const handleProceedToContent = () => {
        setStage('content');
    };

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
            setError("Authentication required. Please log in.");
            router.replace("/login");
            return;
        }

        // Increment current module ONLY if we're currently on this module
        // This prevents double-increments if the user revisits this page
        if(userCourseProgress?.curr_module === resource.number){
            setIsLoading(true);

            try {
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
                setIsLoading(false);
                return;
            } finally{
                setIsLoading(false);
            }
        }

        setResource(null);
        router.replace("/");
    }

    // Parse markdown tables and make them interactive
    const renderContent = (markdownText: string, index: number) => {
        // Check if this is a table (starts with |)
        if (markdownText.trim().startsWith('|')) {
            return renderCustomTable(markdownText, index);
        }

        // Otherwise render as normal markdown
        return (
            <div key={index} className={styles.section}>
                <ReactMarkdown>{markdownText}</ReactMarkdown>
            </div>
        );
    };

    const renderCustomTable = (markdownText: string, index: number) => {
        const lines = markdownText.trim().split('\n');
        if (lines.length < 2) return null;

        const headers = lines[0].split('|').filter(h => h.trim());
        const rows = lines.slice(2).map(line => 
            line.split('|').filter(cell => cell.trim())
        );

        // Determine if this is letter forms table or words table
        const isLetterFormsTable = headers.some(h => 
            h.toLowerCase().includes('standalone') || 
            h.toLowerCase().includes('beginning') || 
            h.toLowerCase().includes('ending')
        );

        return (
            <div key={index} className={styles.section}>
                <table className={styles.customTable}>
                    <thead>
                        <tr>
                            {headers.map((header, idx) => (
                                <th key={idx}>{header.trim()}</th>
                            ))}
                        </tr>
                    </thead>
                    <tbody>
                        {rows.map((row, rowIdx) => (
                            <tr key={rowIdx}>
                                {row.map((cell, cellIdx) => (
                                    <td key={cellIdx}>
                                        <span 
                                            className={styles.clickableCell}
                                            onClick={() => handleCellClick(cell.trim(), isLetterFormsTable, cellIdx)}
                                        >
                                            {cell.trim()}
                                        </span>
                                    </td>
                                ))}
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        );
    };

    const handleCellClick = async (cellContent: string, isLetterForm: boolean, cellIndex: number) => {
        if (audioRef.current) {
            audioRef.current.pause();
            audioRef.current.currentTime = 0;
        }

        if (isLetterForm) {
            // Play letter audio for letter forms
            if (audioRef.current) {
                audioRef.current.src = letterAudio;
                try {
                    await audioRef.current.play();
                } catch (err) {
                    console.error("Failed to play letter audio:", err);
                }
            }
        } else {
            // Play word audio from word_audios array
            if (wordAudios && wordAudios[cellIndex]) {
                if (audioRef.current) {
                    audioRef.current.src = wordAudios[cellIndex];
                    try {
                        await audioRef.current.play();
                    } catch (err) {
                        console.error("Failed to play word audio:", err);
                    }
                }
            }
        }
    };

    // Stage 1: Initial letter view
    if (stage === 'initial') {
        return (
            <div className={styles.initialStage}>
                <audio ref={audioRef} src={letterAudio} preload="auto" />
                
                {/* Home Button */}
                <button className={styles.homeButton} onClick={handleHomeNav}>
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <path d="M3 9l9-7 9 7v11a2 2 0 01-2 2H5a2 2 0 01-2-2z"/>
                        <polyline points="9 22 9 12 15 12 15 22"/>
                    </svg>
                    Home
                </button>

                <div className={styles.audioPlayerContainer}>
                    <div className={styles.waveContainer}>
                        <div className={`${styles.wave} ${isPlaying ? styles.active : ''}`}></div>
                        <div className={`${styles.wave} ${isPlaying ? styles.active : ''}`}></div>
                        <div className={`${styles.wave} ${isPlaying ? styles.active : ''}`}></div>
                        <div className={`${styles.wave} ${isPlaying ? styles.active : ''}`}></div>
                    </div>
                    <button 
                        className={styles.letterButton}
                        onClick={handlePlayLetter}
                        aria-label={isPlaying ? "Pause letter audio" : "Play letter audio"}
                    >
                        <span className={styles.letterText}>{letter}</span>
                    </button>
                </div>

                {hasPlayedOnce && (
                    <div className={styles.nextButtonContainer}>
                        <button 
                            className={styles.nextButton}
                            onClick={handleProceedToContent}
                        >
                            Next
                            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                                <path fillRule="evenodd" d="M3 10a.75.75 0 01.75-.75h10.638L10.23 5.29a.75.75 0 111.04-1.08l5.5 5.25a.75.75 0 010 1.08l-5.5 5.25a.75.75 0 11-1.04-1.08l4.158-3.96H3.75A.75.75 0 013 10z" clipRule="evenodd" />
                            </svg>
                        </button>
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

    // Stage 2: Content view
    return(
        <div className={styles.container}>
            <audio ref={audioRef} src={letterAudio} preload="auto" />

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
                    <div className={styles.titleWithSound}>
                        <h1 className={styles.title}>
                            <span 
                                className={styles.letterInTitle}
                                onClick={handlePlayLetter}
                            >
                                {letterChar}
                            </span>
                            {' — ' + letterName}
                        </h1>
                    </div>
                    <span className={styles.moduleNumber}>Module {resource.number}</span>
                </div>
            </div>

            {/* Content Area */}
            <div className={styles.contentWrapper}>
                <div className={styles.content}>
                    {content.map((markdownSection, index) => 
                        renderContent(markdownSection, index)
                    )}
                </div>
            </div>

            {/* Navigation Footer */}
            <div className={styles.footer}>
                <button 
                    className={styles.homeButtonFooter}
                    onClick={handleHomeNav}
                    disabled={isLoading}
                >
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <path d="M3 9l9-7 9 7v11a2 2 0 01-2 2H5a2 2 0 01-2-2z"/>
                        <polyline points="9 22 9 12 15 12 15 22"/>
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

export default LetterSpeakingLecture;
