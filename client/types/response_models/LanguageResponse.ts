import { AvailableLanguage } from "../enums";
import { DialectResponse } from "./DialectResponse";
import { CourseResponse } from "./CourseResponse";

export interface LanguageResponse {
    id: number;
    language: AvailableLanguage;
    image: string;
    text_color: string;
    dialects: DialectResponse[];
    courses: CourseResponse[];
}
