import { UserResponse } from "./UserResponse";

export interface AuthResponse {
    user: UserResponse;
    token: string;
    token_type: string;
}
