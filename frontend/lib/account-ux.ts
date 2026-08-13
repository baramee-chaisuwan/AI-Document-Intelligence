import type { AuthUser, UserRole } from "../types/auth.ts";


export const PROFILE_PATH = "/profile";


export function passwordInputType(
    isVisible: boolean
): "text" | "password" {
    return isVisible ? "text" : "password";
}


export function passwordToggleLabel(
    isVisible: boolean
): "Hide password" | "Show password" {
    return isVisible ? "Hide password" : "Show password";
}


export function accountInitials(fullName: string): string {
    return fullName
        .split(/\s+/)
        .filter(Boolean)
        .slice(0, 2)
        .map((part) => part[0]?.toUpperCase())
        .join("") || "AI";
}


export function accountRoleLabel(role: UserRole): string {
    return role === "admin" ? "Administrator" : "Recruiter";
}


export function profileDetails(user: AuthUser) {
    return [
        { label: "Name", value: user.full_name },
        { label: "Email", value: user.email },
        { label: "Role", value: accountRoleLabel(user.role) },
    ];
}
