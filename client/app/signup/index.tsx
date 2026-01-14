import { Gender } from "@/types/enums";
import { UserResponse } from "@/types/response_models/UserResponse"
import { useState } from "react"


const Signup = () => {
    const [email, setEmail] = useState<string>("");
    const [password, setPassword] = useState<string>("");
    const [username, setUsername] = useState<string>("");
    const [firstName, setFirstName] = useState<string>("");
    const [lastName, setLastName] = useState<string | null>(null);
    const [gender, setGender] = useState<Gender | null>(null);

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

        const emailValidation: string | null = validateEmail(email)

        if(emailValidation){
            alert(emailValidation)
            return;
        } else if(password.length < 8){
            alert("Password must be at least 8 characters.");
            return;
        } else if(!username){
            alert("Username is required");
            return;
        } else if(!firstName){
            alert("First Name is required");
            return;
        } else if(!gender){
            alert("Gender is required");
            return;
        }

        const submittedLastName: string | null = (lastName && lastName?.length > 0) ? lastName : null
    }

    return(
        <form>
            <input 
                name="email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
            />
            <input 
                name="password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
            />
            <input 
                name="username"
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
            />
            <input 
                name="first_name"
                type="text"
                value={firstName}
                onChange={(e) => setFirstName(e.target.value)}
            />
            <input 
                name="last_name"
                type="text"
                value={lastName ? lastName : ""}
                onChange={(e) => setLastName(e.target.value)}
            />
            {/* Gender Radio Button Group */}
            <div>
                <label>Gender:</label>
                
                <label>
                    <input 
                        type="radio"
                        name="gender"
                        value={Gender.MALE}
                        checked={gender === Gender.MALE}
                        onChange={(e) => setGender(e.target.value as Gender)}
                    />
                    Male
                </label>
                
                <label>
                    <input 
                        type="radio"
                        name="gender"
                        value={Gender.FEMALE}
                        checked={gender === Gender.FEMALE}
                        onChange={(e) => setGender(e.target.value as Gender)}
                    />
                    Female
                </label>
            </div>

            <button type="submit">Sign Up</button>
        </form>
    )
}