import { Gender, AvailableCourse } from "../enums";
import { UserCourseProgressResponse } from "./UserCourseProgressResponse";

export interface UserResponse {
    id: number;
    email: string;
    username: string;
    first_name: string;
    last_name: string | null;
    gender: Gender;
    current_course: AvailableCourse | null;
    languages_learning: string[];
    course_progresses: UserCourseProgressResponse[];
}
