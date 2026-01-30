import { AvailableCourse, AvailableDialect, AvailableLanguage } from "../enums";

export default interface CreateUserCourseProgressRequest {
  id: number;
  course: AvailableCourse;
  language: AvailableLanguage;
  default_dialect: AvailableDialect | null;
  total_modules: number;
}
