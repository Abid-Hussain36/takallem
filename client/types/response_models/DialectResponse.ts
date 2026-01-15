import { AvailableDialect } from "../enums";

export interface DialectResponse {
    id: number;
    dialect: AvailableDialect;
    image: string;
    text_color: string;
}
