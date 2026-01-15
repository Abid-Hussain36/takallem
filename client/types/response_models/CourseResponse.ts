import { AvailableCourse } from "../enums";

export interface CourseResponse {
    id: number;
    course_name: AvailableCourse;
    image: string;
    text_color: string;
}
