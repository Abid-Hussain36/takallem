'use client'

import { useResource } from "@/context/ResourceContext"
import { InfoLectureResponse } from "@/types/response_models/ResourceResponse";
import ReactMarkdown from 'react-markdown';
import styles from './InfoLecture.module.css';
import { useRouter } from "next/navigation";
import { useModules } from "@/context/ModulesContext";
import { useUserCourseProgress } from "@/context/UserCourseProgressContext";
import { useState } from "react";


const InfoLecture = () => {
    const router = useRouter();

    const {resource, setResource} = useResource();
    //const {modules, setModules} = useModules();
    const {userCourseProgress, setUserCourseProgress} = useUserCourseProgress();

    const [isLoading, setIsLoading] = useState<boolean>(false)
    const [error, setError] = useState<string>("")

    if (!resource || !resource.resource) {
        return <div className={styles.loading}>Loading lecture...</div>;
    }

    const lectureData = resource.resource as InfoLectureResponse;

    const handleHomeNav = () => {
        setResource(null);
        router.replace("/");
    }

    const handleNext = async () => {
        if(userCourseProgress!.curr_module === resource.number){
            setIsLoading(true);
            const authToken = localStorage.getItem("token");

            try {
                const incrementUserCourseProgress = await fetch(
                    `${process.env.NEXT_PUBLIC_SERVER_URL}/user-course-progress/curr_module/increment/${userCourseProgress!.id}`,
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
            } catch(err){
                setError(err instanceof Error ? err.message : "Error in updating userCourseProgress.");
            } finally{
                setIsLoading(false);
            }
        }

        setResource(null);
        router.replace("/");
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
                    {lectureData.content.map((markdownSection, index) => (
                        <div key={index} className={styles.section}>
                            <ReactMarkdown>{markdownSection}</ReactMarkdown>
                        </div>
                    ))}
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
        </div>
    );
}

export default InfoLecture;