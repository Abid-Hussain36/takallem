import { AvailableCourse, AvailableDialect } from "../enums";

export default interface CreateUserCourseProgressRequest {
  id: number;
  course: AvailableCourse;
  default_dialect: AvailableDialect | null;
  total_modules: number;
}
