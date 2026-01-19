import { AvailableCourse, AvailableDialect } from "../enums";

export interface UpdateUserCourseProgressDialectRequest {
  id: number;
  course: AvailableCourse;
  dialect: AvailableDialect;
}
