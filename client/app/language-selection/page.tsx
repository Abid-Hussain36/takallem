"use client";

import LanguageCard from "@/components/LanguageCard";
import { LanguageResponse } from "@/types/response_models/LanguageResponse";
import { CourseResponse } from "@/types/response_models/CourseResponse";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import styles from "./LanguageSelection.module.css";

const LanguageSelection = () => {
  const [languages, setLanguages] = useState<LanguageResponse[] | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string>("");
  const router = useRouter();

  useEffect(() => {
    const getLanguages = async () => {
      try {
        if(localStorage.getItem("languageCourses")){
          localStorage.removeItem("languageCourses");
        }
        
        const languageResponse = await fetch(
          `${process.env.NEXT_PUBLIC_SERVER_URL}/languages`
        );

        if (!languageResponse.ok) {
          const errorData = await languageResponse.json();
          throw new Error(errorData.detail || "Language fetching failed");
        }

        const languages = await languageResponse.json();

        if(!languages){
          throw new Error("Failed to fetch language data.");
        }

        setLanguages(languages);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load languages");
      } finally{
        setIsLoading(false);
      }
    };

    getLanguages();
  }, []);

  const handleLanguageSelect = (courses: CourseResponse[]) => {
    localStorage.setItem("languageCourses", JSON.stringify(courses));
    router.push('/language-selection/course-selection');
  };

  if (isLoading) {
    return (
      <div className={styles.container}>
        <div className={styles.loading}>
          <div className={styles.spinner}></div>
          <p>Loading languages...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className={styles.container}>
        <div className={styles.error}>
          <h2>Error</h2>
          <p>{error}</p>
        </div>
      </div>
    );
  }

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <h1 className={styles.title}>Choose Your Language</h1>
        <p className={styles.subtitle}>Start your learning journey today</p>
      </div>

      <div className={styles.grid}>
        {languages &&
          languages.map((language) => (
            <LanguageCard
              key={language.id}
              language={language}
              onLanguageSelect={handleLanguageSelect}
            />
          ))}
      </div>
    </div>
  );
};

export default LanguageSelection;
