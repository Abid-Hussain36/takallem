import { AvailableCourse, AvailableDialect, AvailableLanguage } from "../enums";

export interface UserCourseProgressResponse {
    id: number;
    course_name: AvailableCourse;
    language: AvailableLanguage;
    dialect: AvailableDialect | null;
    default_dialect: AvailableDialect | null;
    total_modules: number;
    curr_module: number;
    covered_words: Record<string, number>;
    problem_counter: number;
    current_vocab_problem_set: number;
}