import { AvailableCourse, AvailableDialect, AvailableLanguage } from "../enums";

export interface CourseResponse {
    id: number;
    course_name: AvailableCourse;
    total_modules: number;
    image: string;
    text_color: string;
    default_dialect: AvailableDialect | null;
    language: AvailableLanguage;
}
