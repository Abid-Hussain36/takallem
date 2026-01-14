'use client'

import { Gender } from "@/types/enums";
import { useUser } from "@/context/UserContext";
import { SignupRequest } from "@/types/request_models/SignupRequest";
import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import styles from './signup.module.css';

export default function Signup() {
    const [email, setEmail] = useState<string>("");
    const [password, setPassword] = useState<string>("");
    const [username, setUsername] = useState<string>("");
    const [firstName, setFirstName] = useState<string>("");
    const [lastName, setLastName] = useState<string | null>(null);
    const [gender, setGender] = useState<Gender | null>(null);
    const [error, setError] = useState<string>("");
    const [isLoading, setIsLoading] = useState<boolean>(false);

    const {setUser} = useUser();
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
        setError("");

        const emailValidation: string | null = validateEmail(email);

        if(emailValidation){
            setError(emailValidation);
            return;
        } else if(password.length < 8){
            setError("Password must be at least 8 characters.");
            return;
        } else if(!username){
            setError("Username is required");
            return;
        } else if(!firstName){
            setError("First Name is required");
            return;
        } else if(!gender){
            setError("Gender is required");
            return;
        }

        const submittedLastName: string | null = (lastName && lastName?.length > 0) ? lastName : null;

        setIsLoading(true);
        
        try{
            const signupRequest: SignupRequest = {
                email: email,
                password: password,
                username: username,
                first_name: firstName,
                last_name: submittedLastName,
                gender: gender!,
                current_course: null,
                languages_learning: []
            };

            console.log(process.env.NEXT_PUBLIC_SERVER_URL ? `${process.env.NEXT_PUBLIC_SERVER_URL}/auth/signup` : "URL failed to fetch from env");

            const signupResponse = await fetch(
                `${process.env.NEXT_PUBLIC_SERVER_URL}/auth/signup`,
                {
                    method: "POST",
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(signupRequest)
                }
            );

            console.log("API Request went through");

            if (!signupResponse.ok) {
                const errorData = await signupResponse.json();
                throw new Error(errorData.detail || "Signup failed");
            }

            const data = await signupResponse.json();

            setUser(data.user);
            
            if(data.token){
                localStorage.setItem("token", data.token);
            }

            router.replace("/");
        } catch(err){
            console.error(`Error on signup: ${err}`);
            setError(err instanceof Error ? err.message : "An error occurred during signup");
        } finally {
            setIsLoading(false);
        }
    }

    return(
        <div className={styles.container}>
            <div className={styles.card}>
                <div className={styles.header}>
                    <h1 className={styles.logo}>تكلّم</h1>
                    <h2 className={styles.title}>Start Your Journey</h2>
                    <p className={styles.subtitle}>Create an account to begin learning Arabic</p>
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
                    
                    <div className={styles.row}>
                        <div className={styles.inputGroup}>
                            <label htmlFor="firstName" className={styles.label}>First Name</label>
                            <input 
                                id="firstName"
                                name="first_name"
                                type="text"
                                placeholder="Ahmed"
                                className={styles.input}
                                value={firstName}
                                onChange={(e) => setFirstName(e.target.value)}
                                disabled={isLoading}
                                required
                            />
                        </div>

                        <div className={styles.inputGroup}>
                            <label htmlFor="lastName" className={styles.label}>Last Name (Optional)</label>
                            <input 
                                id="lastName"
                                name="last_name"
                                type="text"
                                placeholder="Ali"
                                className={styles.input}
                                value={lastName ? lastName : ""}
                                onChange={(e) => setLastName(e.target.value)}
                                disabled={isLoading}
                            />
                        </div>
                    </div>

                    <div className={styles.inputGroup}>
                        <label htmlFor="username" className={styles.label}>Username</label>
                        <input 
                            id="username"
                            name="username"
                            type="text"
                            placeholder="Choose a unique username"
                            className={styles.input}
                            value={username}
                            onChange={(e) => setUsername(e.target.value)}
                            disabled={isLoading}
                            required
                        />
                    </div>

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
                            placeholder="At least 8 characters"
                            className={styles.input}
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            disabled={isLoading}
                            required
                        />
                    </div>
                    
                    <div className={styles.inputGroup}>
                        <label className={styles.label}>Gender</label>
                        <div className={styles.radioGroup}>
                            <label className={`${styles.radioLabel} ${gender === Gender.MALE ? styles.radioLabelActive : ''}`}>
                                <input 
                                    type="radio"
                                    name="gender"
                                    value={Gender.MALE}
                                    checked={gender === Gender.MALE}
                                    onChange={(e) => setGender(e.target.value as Gender)}
                                    disabled={isLoading}
                                    className={styles.radioInput}
                                />
                                <span className={styles.radioText}>Male</span>
                            </label>
                            
                            <label className={`${styles.radioLabel} ${gender === Gender.FEMALE ? styles.radioLabelActive : ''}`}>
                                <input 
                                    type="radio"
                                    name="gender"
                                    value={Gender.FEMALE}
                                    checked={gender === Gender.FEMALE}
                                    onChange={(e) => setGender(e.target.value as Gender)}
                                    disabled={isLoading}
                                    className={styles.radioInput}
                                />
                                <span className={styles.radioText}>Female</span>
                            </label>
                        </div>
                    </div>

                    <button 
                        type="submit" 
                        className={styles.button}
                        disabled={isLoading}
                    >
                        {isLoading ? (
                            <span className={styles.spinner}></span>
                        ) : (
                            'Create Account'
                        )}
                    </button>
                </form>
                
                <div className={styles.footer}>
                    <p>Already have an account? <Link href="/login" className={styles.link}>Log In</Link></p>
                </div>
            </div>
        </div>
    );
}
