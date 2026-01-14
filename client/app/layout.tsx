'use client'
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import { UserProvider, useUser } from "@/context/UserContext";
import { useRouter, usePathname } from "next/navigation";
import { useEffect, useState } from "react";

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
        if (!isPublicRoute) router.replace("/login");
        setIsLoading(false);
        return;
      }

      // Fetch user if we have token but no user data
      if (!user) {
        try {
          const response = await fetch(
            `${process.env.NEXT_PUBLIC_SERVER_URL}/user/me`,
            {
              headers: { 'Authorization': `Bearer ${token}` }
            }
          );

          if (!response.ok) throw new Error("Failed to fetch user");

          const userData = await response.json();
          setUser(userData);
          
          if (isPublicRoute) router.replace("/"); // If we're on a public route like signup or login, we route to the home page
        } catch (err) {
          console.error("Auth error:", err);
          localStorage.removeItem("token");
          if (!isPublicRoute) router.replace("/login");
        }
      } else if (isPublicRoute) {
        router.replace("/");
      }

      setIsLoading(false);
    };

    checkAuth();
  }, [pathname, user]); // Only rerun when route changes or user logs in/out

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
          <LayoutContent>{children}</LayoutContent>
        </UserProvider>
      </body>
    </html>
  );
}
