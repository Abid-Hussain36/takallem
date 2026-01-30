import { AvailableCourse, AvailableDialect } from "../enums";

export interface UpdateUserCourseProgressDialectRequest {
  id: number;
  dialect: AvailableDialect;
}
