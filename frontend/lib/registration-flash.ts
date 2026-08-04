const REGISTRATION_SUCCESS_KEY = (
    "ats_registration_success"
);


export function setRegistrationSuccess(): void {

    if (typeof window === "undefined") {
        return;
    }

    window.sessionStorage.setItem(
        REGISTRATION_SUCCESS_KEY,
        "Your recruiter account was created successfully. Sign in to continue."
    );

}


export function consumeRegistrationSuccess():
    string | null {

    if (typeof window === "undefined") {
        return null;
    }

    const message = window.sessionStorage.getItem(
        REGISTRATION_SUCCESS_KEY
    );

    window.sessionStorage.removeItem(
        REGISTRATION_SUCCESS_KEY
    );

    return message;

}
