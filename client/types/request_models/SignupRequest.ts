import { AvailableCourse, AvailableDialect, Gender } from "../enums"

export interface SignupRequest {
    email: string
    password: string
    username: string
    first_name: string
    last_name: string | null
    gender: Gender
    current_course: AvailableCourse | null
    current_dialect: AvailableDialect | null
    languages_learning: string[]
    languages_learned: string[]
}