import { AvailableCourse, AvailableDialect } from "../enums";

export interface ModuleResponse {
    id: number;
    course: AvailableCourse;
    dialect: AvailableDialect | null;
    unit: string;
    section: string;
    title: string;
    number: number;
    resource_id: number
}
