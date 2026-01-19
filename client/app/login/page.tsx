'use client'

import { useUser } from "@/context/UserContext";
import { LoginRequest } from "@/types/request_models/LoginRequest";
import { useRouter } from "next/navigation";
import { useState } from "react";
import Link from "next/link";
import styles from './login.module.css';
import { useUserCourseProgress } from "@/context/UserCourseProgressContext";

export default function Login() {
    const [email, setEmail] = useState<string>("");
    const [password, setPassword] = useState<string>("");
    const [error, setError] = useState<string>("");
    const [isLoading, setIsLoading] = useState<boolean>(false);

    const {setUser} = useUser();
    const {userCourseProgress, setUserCourseProgress} = useUserCourseProgress();
    const router = useRouter();

    const validateEmail = (email: string): string | null => {
        if (!email) {
            return "Email is required";
        }
        if (!email.includes('@')) {
            return "Please enter a valid email address";
        }
        if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
            return "Email format is invalid";
        }
        return null;
    }

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();

        const emailValidation: string | null = validateEmail(email);

        if(emailValidation){
            setError(emailValidation);
            return;
        } else if(password.length < 8){
            setError("Password must be at least 8 characters.");
            return;
        }

        setIsLoading(true);

        try{
            const loginRequest: LoginRequest = {
                email: email,
                password: password,
            };

            const response = await fetch(
                `${process.env.NEXT_PUBLIC_SERVER_URL}/auth/login`,
                {
                    method: "POST",
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(loginRequest)
                }
            );

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || "Login failed");
            }

            const data = await response.json();

            if(!data.user || !data.token){
                throw new Error("Failed to get user or token data after login endpoint.");
            }

            const tokenData = data.token;
            const userData = data.user;

            localStorage.setItem("token", tokenData);
            setUser(userData);

            if(userData.current_course){
                const getUserCourseProgressResponse = await fetch(
                  `${process.env.NEXT_PUBLIC_SERVER_URL}/user-course-progress/?user_id=${userData.id}&course=${userData.current_course}`,
                  {
                    headers: { 'Authorization': `Bearer ${tokenData}` }
                  }
                )
                
                // If we dont have a progress, we clear the user's course and go to language selection.
                if(getUserCourseProgressResponse.status === 404){
                  const clearUserCourseResponse = await fetch(
                    `${process.env.NEXT_PUBLIC_SERVER_URL}/user/current-course/clear`,
                    {
                      method: "PUT",
                      headers: { 'Authorization': `Bearer ${tokenData}` }
                    }
                  );
                  
                  // IDK what do here for now
                  if(!clearUserCourseResponse.ok){
                    const errorData = await clearUserCourseResponse.json();
                    throw new Error(errorData.detail || "Error in clearing user course when progress not found.")
                  }
    
                  const clearUserCourseData = await clearUserCourseResponse.json();
                  setUser(clearUserCourseData);
                  
                  router.replace("/language-selection");
                }
    
                const userCourseProgressData = await getUserCourseProgressResponse.json();
                setUserCourseProgress(userCourseProgressData);
    
                router.replace("/");
            } else {
                router.replace("/language-selection");
            }
        } catch(err){
            console.error(`Error on login: ${err}`);
            setError(err instanceof Error ? err.message : "An error occurred during login");
        } finally{
            setIsLoading(false);
        }
    }

    return(
        <div className={styles.container}>
            <div className={styles.card}>
                <div className={styles.header}>
                    <h1 className={styles.logo}>Takallem</h1>
                    <h2 className={styles.title}>Welcome Back</h2>
                    <p className={styles.subtitle}>Log in to continue your Arabic journey</p>
                </div>
                
                <form onSubmit={handleSubmit} className={styles.form}>
                    {error && (
                        <div className={styles.error}>
                            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.28 7.22a.75.75 0 00-1.06 1.06L8.94 10l-1.72 1.72a.75.75 0 101.06 1.06L10 11.06l1.72 1.72a.75.75 0 101.06-1.06L11.06 10l1.72-1.72a.75.75 0 00-1.06-1.06L10 8.94 8.28 7.22z" clipRule="evenodd" />
                            </svg>
                            {error}
                        </div>
                    )}
                    
                    <div className={styles.inputGroup}>
                        <label htmlFor="email" className={styles.label}>Email</label>
                        <input 
                            id="email"
                            name="email"
                            type="email"
                            placeholder="you@example.com"
                            className={styles.input}
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            disabled={isLoading}
                            required
                        />
                    </div>

                    <div className={styles.inputGroup}>
                        <label htmlFor="password" className={styles.label}>Password</label>
                        <input 
                            id="password"
                            name="password"
                            type="password"
                            placeholder="••••••••"
                            className={styles.input}
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            disabled={isLoading}
                            required
                        />
                    </div>

                    <button 
                        type="submit" 
                        className={styles.button}
                        disabled={isLoading}
                    >
                        {isLoading ? (
                            <span className={styles.spinner}></span>
                        ) : (
                            'Log In'
                        )}
                    </button>
                </form>
                
                <div className={styles.footer}>
                    <p>Don't have an account? <Link href="/signup" className={styles.link}>Create Account</Link></p>
                </div>
            </div>
        </div>
    );
}
