const RESET_EMAIL_KEY = "ats_password_reset_email";
const RESET_TOKEN_KEY = "ats_password_reset_token";


function storage(): Storage | null {
    return typeof window === "undefined"
        ? null
        : window.sessionStorage;
}


export function setResetEmail(email: string): void {
    storage()?.setItem(RESET_EMAIL_KEY, email);
}


export function getResetEmail(): string | null {
    return storage()?.getItem(RESET_EMAIL_KEY) ?? null;
}


export function setResetToken(token: string): void {
    storage()?.setItem(RESET_TOKEN_KEY, token);
}


export function getResetToken(): string | null {
    return storage()?.getItem(RESET_TOKEN_KEY) ?? null;
}


export function clearPasswordResetState(): void {
    storage()?.removeItem(RESET_EMAIL_KEY);
    storage()?.removeItem(RESET_TOKEN_KEY);
}
