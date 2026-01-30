'use client'

import { useResource } from "@/context/ResourceContext"
import { useUser } from "@/context/UserContext";
import { useUserCourseProgress } from "@/context/UserCourseProgressContext";
import { UpdateUserCourseProgressDialectRequest } from "@/types/request_models/UpdateUserCourseProgressDialectRequest";
import { DialectResponse, DialectSelectionResponse } from "@/types/response_models/ResourceResponse";
import { useRouter } from "next/navigation";
import { useState } from "react";
import DialectCard from "@/components/DialectCard";
import styles from "./DialectSelection.module.css";


const DialectSelection = () => {
    const router = useRouter();

    const {resource, setResource} = useResource();
    const {userCourseProgress, setUserCourseProgress} = useUserCourseProgress();
    const {user, setUser} = useUser();

    const [isLoading, setIsLoading] = useState<boolean>(false)
    const [error, setError] = useState<string>("")

    if (!resource || !resource.resource) {
        return (
            <div className={styles.container}>
                <div className={styles.loading}>Loading dialect selection...</div>
            </div>
        );
    }

    const dialectSelections = resource.resource as DialectSelectionResponse;
    const dialects = dialectSelections.dialects;

    const handleHomeNav = () => {
        setResource(null);
        router.replace("/");
    }

    const handleDialectSelection = async (dialect: DialectResponse) => {
        if(userCourseProgress!.curr_module === resource.number){
            setIsLoading(true);
            const authToken = localStorage.getItem("token");
            
            try {
                // 1. Increment progress
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

                // 2. Set user dialect
                const setUserDialectResponse = await fetch(
                    `${process.env.NEXT_PUBLIC_SERVER_URL}/user/current-dialect/${dialect.dialect}`,
                    {
                        method: "PUT",
                        headers: {
                            'Authorization': `Bearer ${authToken}`,
                            'Content-Type': 'application/json'
                        }
                    }
                )

                if(!setUserDialectResponse.ok){
                    const errorData = await setUserDialectResponse.json();
                    throw new Error(errorData.detail || "Failed to set user dialect")
                }
                
                const newUserData = await setUserDialectResponse.json();
                setUser(newUserData);

                // 3. Set userCourseProgress dialect
                const setUserCourseProgressDialectRequest: UpdateUserCourseProgressDialectRequest = {
                    id: userCourseProgress!.id,
                    dialect: dialect.dialect
                }

                const setUserCourseProgressDialectResponse = await fetch(
                    `${process.env.NEXT_PUBLIC_SERVER_URL}/user-course-progress/dialect`,
                    {
                        method: "PUT",
                        headers: {
                            'Authorization': `Bearer ${authToken}`,
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify(setUserCourseProgressDialectRequest)
                    }
                )

                if(!setUserCourseProgressDialectResponse.ok){
                    const errorData = await setUserCourseProgressDialectResponse.json();
                    throw new Error(errorData.detail || "Failed to set userCourseProgress dialect")
                }
                
                const newUserCourseProgressData = await setUserCourseProgressDialectResponse.json();
                setUserCourseProgress(newUserCourseProgressData);

                // Clear resource and navigate home
                setResource(null);
                router.replace("/")
            } catch(err){
                setError(err instanceof Error ? err.message : "Error in updating user dialect.");
                setIsLoading(false);
            }
        } else {
            // If not on current module, just go back home
            setResource(null);
            router.replace("/")
        }
    }

    return(
        <div className={styles.container}>
            <div className={styles.header}>
                <button className={styles.backButton} onClick={handleHomeNav}>
                    ← Back to Home
                </button>
                <h1 className={styles.title}>Choose Your Dialect</h1>
                <p className={styles.subtitle}>Select the Arabic dialect you want to learn</p>
            </div>

            {error && (
                <div className={styles.errorMessage}>
                    <p>{error}</p>
                </div>
            )}

            {isLoading && (
                <div className={styles.loadingOverlay}>
                    <div className={styles.spinner}></div>
                    <p>Setting up your dialect...</p>
                </div>
            )}

            <div className={styles.grid}>
                {dialects.map((dialect) => (
                    <DialectCard 
                        key={dialect.id} 
                        dialect={dialect} 
                        onDialectClick={handleDialectSelection} 
                    />
                ))}
            </div>
        </div>
    );
}

export default DialectSelection;
