const RESET_SUCCESS_KEY = "ats_password_reset_success";


export function setPasswordResetSuccess(
    message: string
): void {
    window.sessionStorage.setItem(
        RESET_SUCCESS_KEY,
        message
    );
}


export function consumePasswordResetSuccess(): string | null {
    const message = window.sessionStorage.getItem(
        RESET_SUCCESS_KEY
    );
    window.sessionStorage.removeItem(RESET_SUCCESS_KEY);
    return message;
}
