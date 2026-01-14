import { createContext, useContext, useState, ReactNode } from "react";
import { UserResponse } from "@/types/response_models/UserResponse";

interface UserContextType {
    user: UserResponse | null;
    setUser: (user: UserResponse | null) => void;
}

const UserContext = createContext<UserContextType | undefined>(undefined);

export function UserProvider({ children }: { children: ReactNode }) {
    const [user, setUser] = useState<UserResponse | null>(null);

    return (
        <UserContext.Provider value={{ user, setUser }}>
            {children}
        </UserContext.Provider>
    );
}

export function useUser() {
    const context = useContext(UserContext);
    if (!context) {
        throw new Error("useUser must be used within UserProvider");
    }
    return context;
}
