import { AvailableCourse, AvailableDialect } from "../enums";
import { PolymorphicResource } from "./ResourceResponse";

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
