const ACCESS_TOKEN_KEY = (
    "ats_access_token"
);

export const AUTH_STATE_EVENT = (
    "ats-auth-state-changed"
);


function isBrowser() {

    return typeof window !== "undefined";

}


export function getAccessToken(): string | null {

    if (!isBrowser()) {
        return null;
    }

    return window.sessionStorage.getItem(
        ACCESS_TOKEN_KEY
    );

}


export function setAccessToken(
    token: string
): void {

    if (!isBrowser()) {
        return;
    }

    window.sessionStorage.setItem(
        ACCESS_TOKEN_KEY,
        token
    );

    window.dispatchEvent(
        new Event(AUTH_STATE_EVENT)
    );

}


export function clearAccessToken(): void {

    if (!isBrowser()) {
        return;
    }

    window.sessionStorage.removeItem(
        ACCESS_TOKEN_KEY
    );

    window.dispatchEvent(
        new Event(AUTH_STATE_EVENT)
    );

}
