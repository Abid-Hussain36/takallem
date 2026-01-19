'use client'

import { useUser } from "@/context/UserContext";
import { useRouter } from "next/navigation";
import styles from './home.module.css';
import { useEffect, useState } from "react";
import { useModules } from "@/context/ModulesContext";
import { useUserCourseProgress } from "@/context/UserCourseProgressContext";
import CourseProgress from "@/components/CourseProgress";
import ModuleList from "@/components/ModuleList";
import { ModuleResponse } from "@/types/response_models/ModuleResponse";

export default function Home() {
  const { user, setUser } = useUser();
  const { userCourseProgress, setUserCourseProgress } = useUserCourseProgress();
  const {modules, setModules} = useModules();

  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string>("");
  const [token, setToken] = useState<string | null>(null);
  const router = useRouter();

  const handleSignout = () => {
    localStorage.removeItem("token");
    setUser(null);
    setUserCourseProgress(null);
    setModules(null);
    router.replace("/login");
  }

  const handleModuleClick = (module: ModuleResponse) => {
    console.log("Module clicked:", module.number);
    // TODO: Navigate to module page or open module content
  }

  useEffect(() => {
    const getModules = async () => {
      setIsLoading(true);

      if(!user){
        localStorage.removeItem("token");
        setUser(null);
        setUserCourseProgress(null);
        setModules(null);
        router.replace("/login");
      }

      const course = user!.current_course;
      const dialect = user!.current_dialect;

      // Get token from localStorage
      const authToken = localStorage.getItem("token");
      
      if (!authToken) {
        router.replace("/login");
        return;
      }
    
      if(dialect){
        try{
          const modulesResponse = await fetch(
            `${process.env.NEXT_PUBLIC_SERVER_URL}/modules/${course}/${dialect}`,
            {
              method: "GET",
              headers: {
                'Authorization': `Bearer ${authToken}`,
                'Content-Type': 'application/json'
              }
            }
          );
          console.log(modulesResponse);

          if(!modulesResponse.ok){
            const errorData = await modulesResponse.json();
            throw new Error(errorData.detail || "Failed to fetch modules")
          }

          const modulesData = await modulesResponse.json();
          setModules(modulesData);
        } catch(err){
          setError(err instanceof Error ? err.message : "Error in accessing modules with dialect.");
        } finally{
          setIsLoading(false);
        }
      } else{
        try{
          const modulesResponse = await fetch(
            `${process.env.NEXT_PUBLIC_SERVER_URL}/modules/${course}`,
            {
              method: "GET",
              headers: {
                'Authorization': `Bearer ${authToken}`,
                'Content-Type': 'application/json'
              }
            }
          );

          if(!modulesResponse.ok){
            const errorData = await modulesResponse.json();
            throw new Error(errorData.detail || "Failed to fetch modules")
          }

          const modulesData = await modulesResponse.json();
          setModules(modulesData);
        } catch(err){
          setError(err instanceof Error ? err.message : "Error in accessing modules without dialect.");
        } finally{
          setIsLoading(false);
        }
      }
    }
    
    if(!modules || modules.length === 0){
      getModules();
    }
  }, [])

  const handleBadState = () => {
    localStorage.removeItem("token");
    setUser(null);
    setUserCourseProgress(null);
    setModules(null);
    router.replace("/login");
  }

  if (!user || !userCourseProgress || !user.current_course) {
    return <button onClick={handleBadState}>Bad State</button>
  }

  return (
    <div className={styles.container}>
      <nav className={styles.navbar}>
        <div className={styles.navContent}>
          <h1 className={styles.logo}>Takallem</h1>
          <button onClick={handleSignout} className={styles.signoutButton}>
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M3 4.25A2.25 2.25 0 015.25 2h5.5A2.25 2.25 0 0113 4.25v2a.75.75 0 01-1.5 0v-2a.75.75 0 00-.75-.75h-5.5a.75.75 0 00-.75.75v11.5c0 .414.336.75.75.75h5.5a.75.75 0 00.75-.75v-2a.75.75 0 011.5 0v2A2.25 2.25 0 0110.75 18h-5.5A2.25 2.25 0 013 15.75V4.25z" clipRule="evenodd" />
              <path fillRule="evenodd" d="M19 10a.75.75 0 00-.75-.75H8.704l1.048-.943a.75.75 0 10-1.004-1.114l-2.5 2.25a.75.75 0 000 1.114l2.5 2.25a.75.75 0 101.004-1.114l-1.048-.943h9.546A.75.75 0 0019 10z" clipRule="evenodd" />
            </svg>
            Sign Out
          </button>
        </div>
      </nav>

      <main className={styles.main}>
        {isLoading ? (
          <div className={styles.loadingContainer}>
            <div className={styles.spinner}></div>
            <p>Loading your course modules...</p>
          </div>
        ) : error ? (
          <div className={styles.errorContainer}>
            <h2>Error loading modules</h2>
            <p>{error}</p>
          </div>
        ) : modules && modules.length > 0 ? (
          <div className={styles.courseContent}>
            <CourseProgress 
              courseName={user!.current_course || "Your Course"}
              currentModule={userCourseProgress!.curr_module}
              totalModules={userCourseProgress!.total_modules}
            />
            <ModuleList 
              modules={modules}
              currentModule={userCourseProgress!.curr_module}
              onModuleClick={handleModuleClick}
            />
          </div>
        ) : (
          <div className={styles.emptyContainer}>
            <h2>No modules available</h2>
            <p>Please select a course to get started.</p>
            <p>{modules?.toString()}</p>
            <p>{userCourseProgress?.course_name || "Hello"}</p>
            <button onClick={() => console.log(userCourseProgress)}>Click</button>
          </div>
        )}

        <div className={styles.cardsGrid} style={{ display: 'none' }}>
          <div className={styles.card}>
            <div className={styles.cardHeader}>
              <div className={styles.iconWrapper} style={{background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'}}>
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                  <path d="M10 9a3 3 0 100-6 3 3 0 000 6zM6 8a2 2 0 11-4 0 2 2 0 014 0zM1.49 15.326a.78.78 0 01-.358-.442 3 3 0 014.308-3.516 6.484 6.484 0 00-1.905 3.959c-.023.222-.014.442.025.654a4.97 4.97 0 01-2.07-.655zM16.44 15.98a4.97 4.97 0 002.07-.654.78.78 0 00.357-.442 3 3 0 00-4.308-3.517 6.484 6.484 0 011.907 3.96 2.32 2.32 0 01-.026.654zM18 8a2 2 0 11-4 0 2 2 0 014 0zM5.304 16.19a.844.844 0 01-.277-.71 5 5 0 019.947 0 .843.843 0 01-.277.71A6.975 6.975 0 0110 18a6.974 6.974 0 01-4.696-1.81z" />
                </svg>
              </div>
              <h3 className={styles.cardTitle}>Profile</h3>
            </div>
            <div className={styles.cardContent}>
              <div className={styles.infoRow}>
                <span className={styles.infoLabel}>Email:</span>
                <span className={styles.infoValue}>{user!.email}</span>
              </div>
              <div className={styles.infoRow}>
                <span className={styles.infoLabel}>Username:</span>
                <span className={styles.infoValue}>@{user!.username}</span>
              </div>
              <div className={styles.infoRow}>
                <span className={styles.infoLabel}>Name:</span>
                <span className={styles.infoValue}>
                  {user!.first_name} {user!.last_name || ''}
                </span>
              </div>
              <div className={styles.infoRow}>
                <span className={styles.infoLabel}>Gender:</span>
                <span className={styles.infoValue}>{user!.gender}</span>
              </div>
            </div>
          </div>

          <div className={styles.card}>
            <div className={styles.cardHeader}>
              <div className={styles.iconWrapper} style={{background: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)'}}>
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                  <path d="M10.75 16.82A7.462 7.462 0 0115 15.5c.71 0 1.396.098 2.046.282A.75.75 0 0018 15.06v-11a.75.75 0 00-.546-.721A9.006 9.006 0 0015 3a8.963 8.963 0 00-4.25 1.065V16.82zM9.25 4.065A8.963 8.963 0 005 3c-.85 0-1.673.118-2.454.339A.75.75 0 002 4.06v11a.75.75 0 00.954.721A7.506 7.506 0 015 15.5c1.579 0 3.042.487 4.25 1.32V4.065z" />
                </svg>
              </div>
              <h3 className={styles.cardTitle}>Current Course</h3>
            </div>
            <div className={styles.cardContent}>
              {user!.current_course ? (
                <div className={styles.courseInfo}>
                  <div className={styles.courseBadge}>{user!.current_course}</div>
                  <p className={styles.courseDescription}>
                    Continue learning and improve your Arabic skills
                  </p>
                </div>
              ) : (
                <div className={styles.noCourse}>
                  <p>No active course yet</p>
                  <button className={styles.startButton}>Start Learning</button>
                </div>
              )}
            </div>
          </div>

          <div className={styles.card}>
            <div className={styles.cardHeader}>
              <div className={styles.iconWrapper} style={{background: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)'}}>
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.857-9.809a.75.75 0 00-1.214-.882l-3.483 4.79-1.88-1.88a.75.75 0 10-1.06 1.061l2.5 2.5a.75.75 0 001.137-.089l4-5.5z" clipRule="evenodd" />
                </svg>
              </div>
              <h3 className={styles.cardTitle}>Languages Learning</h3>
            </div>
            <div className={styles.cardContent}>
              {user!.languages_learning && user!.languages_learning.length > 0 ? (
                <div className={styles.languagesList}>
                  {user!.languages_learning.map((lang, index) => (
                    <span key={index} className={styles.languageTag}>{lang}</span>
                  ))}
                </div>
              ) : (
                <p className={styles.emptyState}>Start exploring new languages!</p>
              )}
            </div>
          </div>

          <div className={styles.card}>
            <div className={styles.cardHeader}>
              <div className={styles.iconWrapper} style={{background: 'linear-gradient(135deg, #fbc2eb 0%, #a6c1ee 100%)'}}>
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.536-4.464a.75.75 0 10-1.061-1.061 3.5 3.5 0 01-4.95 0 .75.75 0 00-1.06 1.06 5 5 0 007.07 0zM9 8.5c0 .828-.448 1.5-1 1.5s-1-.672-1-1.5S7.448 7 8 7s1 .672 1 1.5zm3 1.5c.552 0 1-.672 1-1.5S12.552 7 12 7s-1 .672-1 1.5.448 1.5 1 1.5z" clipRule="evenodd" />
                </svg>
              </div>
              <h3 className={styles.cardTitle}>Languages Mastered</h3>
            </div>
            <div className={styles.cardContent}>
              {user!.languages_learned && user!.languages_learned.length > 0 ? (
                <div className={styles.languagesList}>
                  {user!.languages_learned.map((lang, index) => (
                    <span key={index} className={styles.languageTagMastered}>{lang} ✓</span>
                  ))}
                </div>
              ) : (
                <p className={styles.emptyState}>Complete your first language to see it here!</p>
              )}
            </div>
          </div>

          <div className={styles.card}>
            <div className={styles.cardHeader}>
              <div className={styles.iconWrapper} style={{background: 'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)'}}>
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M6 3.75A2.75 2.75 0 018.75 1h2.5A2.75 2.75 0 0114 3.75v.443c.572.055 1.14.122 1.706.2C17.053 4.582 18 5.75 18 7.07v3.469c0 1.126-.694 2.191-1.83 2.54-1.952.599-4.024.921-6.17.921s-4.219-.322-6.17-.921C2.694 12.73 2 11.665 2 10.539V7.07c0-1.321.947-2.489 2.294-2.676A41.047 41.047 0 016 4.193V3.75zm6.5 0v.325a41.622 41.622 0 00-5 0V3.75c0-.69.56-1.25 1.25-1.25h2.5c.69 0 1.25.56 1.25 1.25zM10 10a1 1 0 00-1 1v.01a1 1 0 001 1h.01a1 1 0 001-1V11a1 1 0 00-1-1H10z" clipRule="evenodd" />
                  <path d="M3 15.055v-.684c.126.053.255.1.39.142 2.092.642 4.313.987 6.61.987 2.297 0 4.518-.345 6.61-.987.135-.041.264-.089.39-.142v.684c0 1.347-.985 2.53-2.363 2.686a41.454 41.454 0 01-9.274 0C3.985 17.585 3 16.402 3 15.055z" />
                </svg>
              </div>
              <h3 className={styles.cardTitle}>Quick Stats</h3>
            </div>
            <div className={styles.cardContent}>
              <div className={styles.statsGrid}>
                <div className={styles.statItem}>
                  <div className={styles.statValue}>0</div>
                  <div className={styles.statLabel}>Lessons</div>
                </div>
                <div className={styles.statItem}>
                  <div className={styles.statValue}>0</div>
                  <div className={styles.statLabel}>Words</div>
                </div>
                <div className={styles.statItem}>
                  <div className={styles.statValue}>0h</div>
                  <div className={styles.statLabel}>Time</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
