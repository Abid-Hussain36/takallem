'use client'
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import { UserProvider, useUser } from "@/context/UserContext";
import { UserCourseProgressProvider, useUserCourseProgress } from "@/context/UserCourseProgressContext";
import { ModulesProvider } from "@/context/ModulesContext";
import { useRouter, usePathname } from "next/navigation";
import { useEffect, useState } from "react";
import { ResourceProvider } from "@/context/ResourceContext";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

function LayoutContent({ children }: { children: React.ReactNode }) {
  const { user, setUser } = useUser();
  const {userCourseProgress, setUserCourseProgress} = useUserCourseProgress()
  const router = useRouter();
  const pathname = usePathname(); // Used to access the current URL path in the browser
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const checkAuth = async () => {
      const token = localStorage.getItem("token");
      const publicRoutes = ['/login', '/signup'];
      const isPublicRoute = publicRoutes.includes(pathname);

      // If we don't have a token and we are on a non-public page, we route to login
      if (!token) {
        setIsLoading(false);
        if (!isPublicRoute) router.replace("/login");
        return;
      }

      if (!user) {
        try {
          // Fetch user if we have token but no user data
          const response = await fetch(
            `${process.env.NEXT_PUBLIC_SERVER_URL}/user/me`,
            {
              headers: { 'Authorization': `Bearer ${token}` }
            }
          );

          // If user not found, we route to the login screen
          if (!response.ok){
            setIsLoading(false);
            localStorage.removeItem("token")
            router.replace("/login");
            return;
          }

          const userData = await response.json();
          setUser(userData);

          // SET USER PROGRESS HERE!!!

          // We check if the user's currently taking a course and set the progress
          if(userData.current_course){
            const getUserCourseProgressResponse = await fetch(
              `${process.env.NEXT_PUBLIC_SERVER_URL}/user-course-progress/?user_id=${userData.id}&course=${userData.current_course}`,
              {
                headers: { 'Authorization': `Bearer ${token}` }
              }
            )
            
            // If we dont have a progress, we clear the user's course and go to language selection.
            if(getUserCourseProgressResponse.status === 404){
              const clearUserCourseResponse = await fetch(
                `${process.env.NEXT_PUBLIC_SERVER_URL}/user/current-course/clear`,
                {
                  method: "PUT",
                  headers: { 'Authorization': `Bearer ${token}` }
                }
              );
              
              if(!clearUserCourseResponse.ok){
                setIsLoading(false);
                const errorData = await clearUserCourseResponse.json();
                throw new Error(errorData.detail || "Error in clearing user course when progress not found.")
              }

              const clearUserCourseData = await clearUserCourseResponse.json();
              setUser(clearUserCourseData);
              
              setIsLoading(false);
              router.replace("/language-selection");
              return;
            }

            const userCourseProgressData = await getUserCourseProgressResponse.json();
            setUserCourseProgress(userCourseProgressData);

            setIsLoading(false);
            router.replace("/");
            return;
          } else{
            setIsLoading(false);
            router.replace("/language-selection");
            return;
          }
        } catch (err) {
          console.error("Auth error:", err);
          localStorage.removeItem("token");
          if (!isPublicRoute) router.replace("/login");
        }
      } else if(!user.current_course){
        setIsLoading(false);
        setUserCourseProgress(null); // Just in case
        router.replace("/language-selection");
        return;
      } else if (isPublicRoute) {
        const getUserCourseProgressResponse = await fetch(
          `${process.env.NEXT_PUBLIC_SERVER_URL}/user-course-progress/?user_id=${user.id}&course=${user.current_course}`,
          {
            headers: { 'Authorization': `Bearer ${token}` }
          }
        )

        if(getUserCourseProgressResponse.status === 404){
          const clearUserCourseResponse = await fetch(
            `${process.env.NEXT_PUBLIC_SERVER_URL}/user/current-course/clear`,
            {
              method: "PUT",
              headers: { 'Authorization': `Bearer ${token}` }
            }
          );

          const clearUserCourseData = await clearUserCourseResponse.json();
          setUser(clearUserCourseData);
          
          setIsLoading(false);
          router.replace("/language-selection");
          return;
        }

        const userCourseProgressData = await getUserCourseProgressResponse.json();
        setUserCourseProgress(userCourseProgressData);

        setIsLoading(false);
        router.replace("/");
        return;
      }
    };

    checkAuth();
  }, []);

  if (isLoading) {
    return (
      <div style={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        height: '100vh',
        fontSize: '1.5rem'
      }}>
        Loading...
      </div>
    );
  }

  return <>{children}</>;
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased`}
      >
        <UserProvider>
          <UserCourseProgressProvider>
            <ModulesProvider>
              <ResourceProvider>
                <LayoutContent>{children}</LayoutContent>
              </ResourceProvider>
            </ModulesProvider>
          </UserCourseProgressProvider>
        </UserProvider>
      </body>
    </html>
  );
}
