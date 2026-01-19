import { createContext, useContext, useState, ReactNode } from "react";
import { UserCourseProgressResponse } from "@/types/response_models/UserCourseProgressResponse";

// We outline the object being stored in our context
interface UserCourseProgressContextType {
  userCourseProgress: UserCourseProgressResponse | null;
  setUserCourseProgress: (progress: UserCourseProgressResponse | null) => void;
}

const UserCourseProgressContext = createContext<UserCourseProgressContextType | undefined>(
  undefined
);

export function UserCourseProgressProvider({ children }: { children: ReactNode }) {
  const [userCourseProgress, setUserCourseProgress] =
    useState<UserCourseProgressResponse | null>(null);

  return (
    <UserCourseProgressContext.Provider value={{ userCourseProgress, setUserCourseProgress }}>
      {children}
    </UserCourseProgressContext.Provider>
  );
}

export function useUserCourseProgress() {
  const context = useContext(UserCourseProgressContext);
  if (!context) {
    throw new Error("useUserCourseProgress must be used within UserCourseProgressProvider");
  }
  return context;
}
