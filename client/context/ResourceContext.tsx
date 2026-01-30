'use client'

import { CachedResource } from "@/types/response_models/ResourceResponse";
import { createContext, useContext, useState, ReactNode } from "react";

// We outline the object being stored in our context
interface ResourceContextType {
    resource: CachedResource | null;
    setResource: (user: CachedResource | null) => void;
}

const ResourceContext = createContext<ResourceContextType | undefined>(undefined);

export function ResourceProvider({ children }: { children: ReactNode }) {
    const [resource, setResource] = useState<CachedResource | null>(null);

    return (
        <ResourceContext.Provider value={{ resource, setResource }}>
            {children}
        </ResourceContext.Provider>
    );
}

export function useResource() {
    const context = useContext(ResourceContext);
    if (!context) {
        throw new Error("useResource must be used within ResourceProvider");
    }
    return context;
}
