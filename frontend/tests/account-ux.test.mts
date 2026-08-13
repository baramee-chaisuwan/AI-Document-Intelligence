import assert from "node:assert/strict";
import test from "node:test";

import {
    accountInitials,
    passwordInputType,
    passwordToggleLabel,
    profileDetails,
    validatePasswordChange,
    validateProfilePhoto,
    PROFILE_PATH,
} from "../lib/account-ux.ts";
import { isPublicPath } from "../lib/route-access.ts";
import type { AuthUser } from "../types/auth.ts";


const user: AuthUser = {
    id: 7,
    email: "recruiter@example.com",
    full_name: "Baramee Chaisuwan",
    role: "admin",
    is_active: true,
    created_at: "2026-08-13T00:00:00Z",
    updated_at: "2026-08-13T00:00:00Z",
    has_profile_image: false,
};


test("password visibility defaults hidden and exposes matching labels", () => {
    assert.equal(passwordInputType(false), "password");
    assert.equal(passwordToggleLabel(false), "Show password");
    assert.equal(passwordInputType(true), "text");
    assert.equal(passwordToggleLabel(true), "Hide password");
});


test("authenticated profile presents only safe existing account fields", () => {
    assert.deepEqual(profileDetails(user), [
        { label: "Name", value: "Baramee Chaisuwan" },
        { label: "Email", value: "recruiter@example.com" },
        { label: "Role", value: "Administrator" },
        { label: "Status", value: "Active" },
        { label: "Member since", value: "Aug 13, 2026" },
    ]);
    assert.equal(accountInitials(user.full_name), "BC");
});


test("profile photo validation accepts supported images within 5 MB", () => {
    assert.equal(validateProfilePhoto({ type: "image/png", size: 1024 }), null);
    assert.match(validateProfilePhoto({ type: "image/gif", size: 1024 }) ?? "", /JPEG/);
    assert.match(validateProfilePhoto({ type: "image/jpeg", size: 6 * 1024 * 1024 }) ?? "", /5 MB/);
});


test("password change validation preserves secure account behavior", () => {
    assert.equal(validatePasswordChange("old", "NewPassword123!", "NewPassword123!"), null);
    assert.match(validatePasswordChange("old", "short", "short") ?? "", /8 characters/);
    assert.match(validatePasswordChange("old", "NewPassword123!", "Different123!") ?? "", /do not match/);
});


test("navbar identity target is the protected profile route", () => {
    assert.equal(PROFILE_PATH, "/profile");
    assert.equal(isPublicPath(PROFILE_PATH), false);
    assert.equal(isPublicPath("/login"), true);
});
