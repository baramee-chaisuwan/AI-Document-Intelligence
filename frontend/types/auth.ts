export type UserRole = "admin" | "recruiter";


export interface AuthUser {
    id: number;
    email: string;
    full_name: string;
    role: UserRole;
    is_active: boolean;
    created_at: string;
    updated_at: string;
    has_profile_image: boolean;
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


export interface MessageResponse {
    message: string;
}


export interface PasswordResetTokenResponse {
    reset_token: string;
    token_type: "password_reset";
    expires_in: number;
}


export interface ProfileUpdateRequest {
    full_name: string;
}


export interface ChangePasswordRequest {
    current_password: string;
    new_password: string;
    confirm_password: string;
}
