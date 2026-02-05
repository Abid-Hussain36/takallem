'use client'

import { useResource } from "@/context/ResourceContext"
import { useUserCourseProgress } from "@/context/UserCourseProgressContext";
import { LetterWritingLectureResponse } from "@/types/response_models/ResourceResponse";
import ReactMarkdown from 'react-markdown';
import styles from './LetterWritingLecture.module.css';
import { useRouter } from "next/navigation";
import { useState, useEffect } from "react";

const LetterWritingLecture = () => {
    const router = useRouter();

    const {resource, setResource} = useResource();
    const {userCourseProgress, setUserCourseProgress} = useUserCourseProgress();

    const [isLoading, setIsLoading] = useState<boolean>(false);
    const [error, setError] = useState<string>("");

    if (!resource || !resource.resource) {
        return <div className={styles.loading}>Loading lecture...</div>;
    }

    const lectureData = resource.resource as LetterWritingLectureResponse;

    // Define the order of positions
    const positionOrder = ['Standalone', 'Beginning', 'Middle', 'End'];
    
    // Sort sequences by position order
    const sortedSequences = [...lectureData.letter_writing_sequences].sort((a, b) => {
        return positionOrder.indexOf(a.position) - positionOrder.indexOf(b.position);
    });

    // Get position icon
    const getPositionIcon = (position: string) => {
        switch(position) {
            case 'Standalone': return 'S';
            case 'Beginning': return 'B';
            case 'Middle': return 'M';
            case 'End': return 'E';
            default: return '•';
        }
    };

    // Auto-dismiss error after 5 seconds
    useEffect(() => {
        if (error) {
            const timer = setTimeout(() => setError(""), 5000);
            return () => clearTimeout(timer);
        }
    }, [error]);

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

        if(userCourseProgress!.curr_module === resource.number){
            setIsLoading(true);

            try {
                const incrementUserCourseProgress = await fetch(
                    `${process.env.NEXT_PUBLIC_SERVER_URL}/user-course-progress/curr-module/increment/${userCourseProgress!.id}`,
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

                const newUserCourseProgress = await incrementUserCourseProgress.json();
                setUserCourseProgress(newUserCourseProgress);
                
                setResource(null);
                router.replace("/");
            } catch(err){
                setError(err instanceof Error ? err.message : "Error in updating userCourseProgress.");
            } finally{
                setIsLoading(false);
            }
        } else {
            setResource(null);
            router.replace("/");
        }
    }

    return(
        <div className={styles.container}>
            {/* Top Bar */}
            <div className={styles.topBar}>
                <div className={styles.breadcrumb}>
                    <span className={styles.course}>{resource.course}</span>
                    <span className={styles.separator}>›</span>
                    <span className={styles.unit}>Unit {resource.unit}</span>
                    <span className={styles.separator}>›</span>
                    <span className={styles.section}>Section {resource.section}</span>
                </div>
                <div className={styles.lectureHeader}>
                    <h1 className={styles.title}>{resource.title}</h1>
                    <span className={styles.moduleNumber}>Module {resource.number}</span>
                </div>
            </div>

            {/* Content Wrapper */}
            <div className={styles.contentWrapper}>
                <div className={styles.content}>
                    {/* Markdown Content Sections */}
                    {lectureData.content && lectureData.content.length > 0 && (
                        <>
                            {lectureData.content.map((section, index) => (
                                <div key={index} className={styles.markdownSection}>
                                    <ReactMarkdown>{section}</ReactMarkdown>
                                </div>
                            ))}
                        </>
                    )}

                    {/* Writing Sequences Section */}
                    {sortedSequences.length > 0 && (
                        <div className={styles.sequencesSection}>
                            <h2 className={styles.sequencesSectionTitle}>
                                Letter Writing Sequences — {lectureData.letter}
                            </h2>

                            {sortedSequences.map((sequence, seqIndex) => (
                                <div key={sequence.id} className={styles.positionSection}>
                                    <div className={styles.positionTitle}>
                                        <span className={styles.positionIcon}>
                                            {getPositionIcon(sequence.position)}
                                        </span>
                                        {sequence.position} Position
                                    </div>

                                    <div className={styles.sequenceContainer}>
                                        {/* Reverse the array to show right-to-left for Arabic */}
                                        {[...sequence.sequence_images].reverse().map((image, imgIndex, arr) => (
                                            <div key={imgIndex} style={{ display: 'flex', alignItems: 'center', gap: '1.5rem' }}>
                                                <div className={styles.imageWrapper}>
                                                    <img 
                                                        src={image} 
                                                        alt={`${sequence.position} - Step ${arr.length - imgIndex}`}
                                                        className={styles.sequenceImage}
                                                    />
                                                </div>
                                                
                                                {/* Show arrow except after the last image */}
                                                {imgIndex < arr.length - 1 && (
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
                            ))}
                        </div>
                    )}

                    {sortedSequences.length === 0 && (
                        <div className={styles.emptyState}>
                            No writing sequences available for this lecture.
                        </div>
                    )}
                </div>
            </div>

            {/* Footer */}
            <div className={styles.footer}>
                <button className={`${styles.button} ${styles.homeButton}`} onClick={handleHomeNav}>
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
                    </svg>
                    Home
                </button>
                <button 
                    className={`${styles.button} ${styles.continueButton}`} 
                    onClick={handleNext}
                    disabled={isLoading}
                >
                    {isLoading ? 'Loading...' : 'Continue'}
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
                    </svg>
                </button>
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

export default LetterWritingLecture;
