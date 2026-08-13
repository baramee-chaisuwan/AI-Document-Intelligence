const PUBLIC_PATHS = new Set([
    "/login",
    "/register",
    "/forgot-password",
    "/verify-reset-otp",
    "/reset-password",
]);

const ADMIN_PATHS = new Set([
    "/export",
]);


export function isPublicPath(pathname: string): boolean {
    return PUBLIC_PATHS.has(pathname);
}


export function isAdminPath(pathname: string): boolean {
    return ADMIN_PATHS.has(pathname);
}
