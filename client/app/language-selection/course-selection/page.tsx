"use client";

import CourseCard from "@/components/CourseCard";
import { CourseResponse } from "@/types/response_models/CourseResponse";
import { AvailableCourse } from "@/types/enums";
import { useUser } from "@/context/UserContext";
import { useUserCourseProgress } from "@/context/UserCourseProgressContext";
import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import styles from "./CourseSelection.module.css";
import CreateUserCourseProgressRequest from "@/types/request_models/CreateUserCourseProgressRequest";


const CourseSelection = () => {
  const [courses, setCourses] = useState<CourseResponse[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string>("");

  const { user, setUser } = useUser();
  const { userCourseProgress, setUserCourseProgress } = useUserCourseProgress();
  const router = useRouter();

  useEffect(() => {
    // Retrieve courses from localStorage
    const storedCourses = localStorage.getItem("languageCourses");
    if (storedCourses) {
      try {
        const parsedCourses = JSON.parse(storedCourses);
        setCourses(parsedCourses);
      } catch (err) {
        setError("Failed to load courses from localStorage");
      }
    } else{
      router.back();
    }
  }, []);

  const handleBack = () => {
    if(localStorage.getItem("languageCourses")){
      localStorage.removeItem("languageCourses");
    }
    router.back()
  }

  const handleCourseClick = async (course: CourseResponse) => {
    setIsLoading(true);
    const token = localStorage.getItem("token");

    if (!token) {
      setError("User is not authenticated");
      setIsLoading(false);
      localStorage.removeItem("languageCourses");
      setUser(null);
      router.replace("/login");
    }

    try {
      // 1. Updating the user's current course
      const userCourseUpdateResponse = await fetch(
      `${process.env.NEXT_PUBLIC_SERVER_URL}/user/current-course/${course.course_name}`,
        {
          method: "PUT",
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          },
        }
      );

      if(!userCourseUpdateResponse.ok){
        const error_data = await userCourseUpdateResponse.json();
        throw new Error(error_data.detail || "Failed to update user's current course.")
      }

      // 2. Updating the user's languages learning
      const userLanguagesLearningUpdateResponse = await fetch(
        `${process.env.NEXT_PUBLIC_SERVER_URL}/user/language-learning/add/${course.language}`,
        {
          method: "PUT",
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        }
      );

      if(!userLanguagesLearningUpdateResponse.ok){
        const errorData = await userLanguagesLearningUpdateResponse.json();
        throw new Error(errorData.detail || "Failed to update user's languages learning list.");
      }

      // 3. Creating a new UserCourseProgress for selected course
      const createUserCourseProgressRequest: CreateUserCourseProgressRequest = {
        id: user!.id, 
        course: course.course_name, 
        default_dialect: course.default_dialect, 
        total_modules: course.total_modules
      };

      const createUserCourseProgressResponse = await fetch(
        `${process.env.NEXT_PUBLIC_SERVER_URL}/user-course-progress/`,
        {
          method: "POST",
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(createUserCourseProgressRequest)
        }
      )

      if(!createUserCourseProgressResponse.ok){
        const errorData = await createUserCourseProgressResponse.json();
        throw new Error(errorData.detail || "Failed to create user course progress")
      }

      const updatedUser = await userLanguagesLearningUpdateResponse.json();
      const createdUserCourseProgress = await createUserCourseProgressResponse.json();

      setUser(updatedUser);
      setUserCourseProgress(createdUserCourseProgress);

      if(updatedUser && createdUserCourseProgress && updatedUser.current_course){
        localStorage.removeItem("languageCourses");
        router.replace("/");
      } else{
        const userNull = user === null;
        const progressNull = userCourseProgress === null;
        const currCourseNull = user?.current_course === null;
        throw new Error(`Failed to set user's course data after API calls. user: ${userNull}, progress: ${progressNull}, course: ${currCourseNull}`)
      }
      
    } catch(err){
      setError(err instanceof Error ? err.message : "Error in accessing course.");
    } finally{
      setIsLoading(false);
    }
  };

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <button className={styles.backButton} onClick={handleBack}>
          ← Back
        </button>
        <h1 className={styles.title}>Choose Your Course</h1>
        <p className={styles.subtitle}>Select the course level that fits you best</p>
      </div>

      {error && (
        <div className={styles.errorMessage}>
          <p>{error}</p>
        </div>
      )}

      {isLoading && (
        <div className={styles.loadingOverlay}>
          <div className={styles.spinner}></div>
          <p>Setting up your course...</p>
        </div>
      )}

      <div className={styles.grid}>
        {courses.map((course) => (
          <CourseCard key={course.id} course={course} onCourseClick={handleCourseClick} />
        ))}
      </div>
    </div>
  );
};

export default CourseSelection;
