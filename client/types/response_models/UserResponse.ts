import { Gender, AvailableCourse, AvailableDialect } from "../enums";
import { UserCourseProgressResponse } from "./UserCourseProgressResponse";

export interface UserResponse {
    id: number;
    email: string;
    username: string;
    first_name: string;
    last_name: string | null;
    gender: Gender;
    current_course: AvailableCourse | null;
    current_dialect: AvailableDialect | null;
    languages_learning: string[];
    languages_learned: string[];
    courses_completed: string[];
    course_progresses: UserCourseProgressResponse[];
}
