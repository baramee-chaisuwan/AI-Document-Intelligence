export type UserRole = "admin" | "recruiter";


export interface AuthUser {
    id: number;
    email: string;
    full_name: string;
    role: UserRole;
    is_active: boolean;
    created_at: string;
    updated_at: string;
}


export interface LoginCredentials {
    email: string;
    password: string;
}


export interface RegisterCredentials {
    full_name: string;
    email: string;
    password: string;
}


export interface AccessTokenResponse {
    access_token: string;
    token_type: "bearer";
    expires_in: number;
}
