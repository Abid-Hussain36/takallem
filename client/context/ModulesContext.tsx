import { createContext, useContext, useState, ReactNode } from "react";
import { ModuleResponse } from "@/types/response_models/ModuleResponse";

// We outline the object being stored in our context
interface ModulesContextType {
    modules: ModuleResponse[] | null;
    setModules: (modules: ModuleResponse[] | null) => void;
}

const ModulesContext = createContext<ModulesContextType | undefined>(undefined);

export function ModulesProvider({ children }: { children: ReactNode }) {
    const [modules, setModules] = useState<ModuleResponse[] | null>(null);

    return (
        <ModulesContext.Provider value={{ modules, setModules }}>
            {children}
        </ModulesContext.Provider>
    );
}

export function useModules() {
    const context = useContext(ModulesContext);
    if (!context) {
        throw new Error("useModules must be used within ModulesProvider");
    }
    return context;
}
