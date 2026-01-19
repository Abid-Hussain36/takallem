import { Gender } from "../enums";

export interface UpdateUserRequest {
  first_name: string | null;
  last_name: string | null;
  gender: Gender | null;
}
