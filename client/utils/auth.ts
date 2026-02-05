/**
 * Auth utility functions for handling authentication errors
 */

/**
 * Checks if an error response indicates an expired or invalid token
 */
export function isAuthError(error: any): boolean {
    if (!error) return false;
    
    const errorMessage = error.message?.toLowerCase() || error.detail?.toLowerCase() || '';
    
    return (
        errorMessage.includes('token is expired') ||
        errorMessage.includes('invalid jwt') ||
        errorMessage.includes('token has invalid claims') ||
        errorMessage.includes('unable to parse or verify signature') ||
        errorMessage.includes('unauthorized') ||
        errorMessage.includes('authentication failed')
    );
}

/**
 * Handles authentication errors by clearing storage and redirecting to login
 */
export function handleAuthError(router: any, setters?: {
    setUser?: (user: any) => void,
    setUserCourseProgress?: (progress: any) => void,
    setModules?: (modules: any) => void,
    setResource?: (resource: any) => void
}): void {
    // Clear all auth-related data from localStorage
    localStorage.removeItem('token');
    
    // Clear all context state if setters provided
    if (setters) {
        setters.setUser?.(null);
        setters.setUserCourseProgress?.(null);
        setters.setModules?.(null);
        setters.setResource?.(null);
    }
    
    // Redirect to login
    router.replace('/login');
}

/**
 * Wrapper for fetch that automatically handles auth errors
 */
export async function authFetch(url: string, options: RequestInit = {}): Promise<Response> {
    const token = localStorage.getItem('token');
    
    if (!token) {
        throw new Error('No authentication token found');
    }
    
    const headers = {
        ...options.headers,
        'Authorization': `Bearer ${token}`
    };
    
    const response = await fetch(url, { ...options, headers });
    
    // Check for auth errors (401, 403)
    if (response.status === 401 || response.status === 403) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || 'Authentication failed');
    }
    
    return response;
}
