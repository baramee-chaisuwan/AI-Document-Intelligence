import type { AuthUser, UserRole } from "../types/auth.ts";


export const PROFILE_PATH = "/profile";
export const MAX_PROFILE_PHOTO_BYTES = 5 * 1024 * 1024;
export const PROFILE_PHOTO_TYPES = [
    "image/jpeg",
    "image/png",
    "image/webp",
] as const;


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
        { label: "Status", value: user.is_active ? "Active" : "Inactive" },
        {
            label: "Member since",
            value: new Intl.DateTimeFormat("en", {
                dateStyle: "medium",
            }).format(new Date(user.created_at)),
        },
    ];
}


export function validateProfilePhoto(file: {
    type: string;
    size: number;
}): string | null {
    if (!(PROFILE_PHOTO_TYPES as readonly string[]).includes(file.type)) {
        return "Choose a JPEG, PNG, or WebP image.";
    }
    if (file.size > MAX_PROFILE_PHOTO_BYTES) {
        return "Profile photo must not exceed 5 MB.";
    }
    return null;
}


export function validatePasswordChange(
    currentPassword: string,
    newPassword: string,
    confirmPassword: string
): string | null {
    if (!currentPassword || !newPassword || !confirmPassword) {
        return "Complete all password fields.";
    }
    if (newPassword.length < 8) {
        return "New password must be at least 8 characters.";
    }
    if (new TextEncoder().encode(newPassword).length > 72) {
        return "New password must not exceed 72 UTF-8 bytes.";
    }
    if (newPassword !== confirmPassword) {
        return "New passwords do not match.";
    }
    return null;
}
