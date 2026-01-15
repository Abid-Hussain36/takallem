import { AvailableCourse } from "../enums";
import { PolymorphicResource } from "./ResourceResponse";

export interface ModuleResponse {
    id: number;
    course: AvailableCourse;
    unit: string;
    section: string;
    title: string;
    number: number;
    resource: PolymorphicResource;  // Polymorphic resource with full nested data
}
