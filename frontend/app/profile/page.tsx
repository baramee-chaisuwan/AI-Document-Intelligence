"use client";

import { ChangeEvent, FormEvent, useRef, useState } from "react";
import { Camera, CheckCircle2, ShieldCheck, Trash2 } from "lucide-react";

import PasswordInput from "@/components/auth/PasswordInput";
import ProfileAvatar from "@/components/account/ProfileAvatar";
import AppLayout from "@/components/layout/AppLayout";
import { useAuth } from "@/contexts/AuthContext";
import {
    accountRoleLabel,
    profileDetails,
    validatePasswordChange,
    validateProfilePhoto,
} from "@/lib/account-ux";
import {
    changePassword,
    removeProfilePhoto,
    updateCurrentUser,
    uploadProfilePhoto,
} from "@/services/auth";


export default function ProfilePage() {
    const { user, refreshUser, logout } = useAuth();
    const fileInput = useRef<HTMLInputElement>(null);
    const [editing, setEditing] = useState(false);
    const [fullName, setFullName] = useState(user?.full_name ?? "");
    const [profileBusy, setProfileBusy] = useState(false);
    const [profileMessage, setProfileMessage] = useState<string | null>(null);
    const [profileError, setProfileError] = useState<string | null>(null);
    const [passwords, setPasswords] = useState({
        current_password: "",
        new_password: "",
        confirm_password: "",
    });
    const [passwordBusy, setPasswordBusy] = useState(false);
    const [passwordError, setPasswordError] = useState<string | null>(null);

    if (!user) return null;

    const currentUser = user;
    const details = profileDetails(currentUser);

    function beginEdit() {
        setFullName(currentUser.full_name);
        setProfileError(null);
        setProfileMessage(null);
        setEditing(true);
    }

    function cancelEdit() {
        setFullName(currentUser.full_name);
        setProfileError(null);
        setEditing(false);
    }

    async function saveProfile(event: FormEvent) {
        event.preventDefault();
        const normalized = fullName.trim();
        if (!normalized) {
            setProfileError("Full name cannot be blank.");
            return;
        }
        setProfileBusy(true);
        setProfileError(null);
        setProfileMessage("Saving profile…");
        try {
            await updateCurrentUser({ full_name: normalized });
            await refreshUser();
            setEditing(false);
            setProfileMessage("Profile updated.");
        } catch (error) {
            setProfileError(error instanceof Error ? error.message : "Unable to update your profile.");
        } finally {
            setProfileBusy(false);
        }
    }

    async function selectPhoto(event: ChangeEvent<HTMLInputElement>) {
        const photo = event.target.files?.[0];
        event.target.value = "";
        if (!photo) return;
        const validationError = validateProfilePhoto(photo);
        if (validationError) {
            setProfileError(validationError);
            return;
        }
        setProfileBusy(true);
        setProfileError(null);
        setProfileMessage("Uploading profile photo…");
        try {
            await uploadProfilePhoto(photo);
            await refreshUser();
            setProfileMessage("Profile photo updated.");
        } catch (error) {
            setProfileError(error instanceof Error ? error.message : "Unable to upload the profile photo.");
        } finally {
            setProfileBusy(false);
        }
    }

    async function removePhoto() {
        setProfileBusy(true);
        setProfileError(null);
        setProfileMessage("Removing profile photo…");
        try {
            await removeProfilePhoto();
            await refreshUser();
            setProfileMessage("Profile photo removed.");
        } catch (error) {
            setProfileError(error instanceof Error ? error.message : "Unable to remove the profile photo.");
        } finally {
            setProfileBusy(false);
        }
    }

    async function submitPassword(event: FormEvent) {
        event.preventDefault();
        const validationError = validatePasswordChange(
            passwords.current_password,
            passwords.new_password,
            passwords.confirm_password
        );
        if (validationError) {
            setPasswordError(validationError);
            return;
        }
        setPasswordBusy(true);
        setPasswordError(null);
        try {
            await changePassword(passwords);
            logout();
        } catch (error) {
            setPasswordError(error instanceof Error ? error.message : "Unable to change your password.");
            setPasswordBusy(false);
        }
    }

    const cardClass = "rounded-2xl border border-gray-200 bg-white p-6 shadow-sm";
    const buttonClass = "rounded-lg px-4 py-2 text-sm font-semibold transition disabled:cursor-not-allowed disabled:opacity-50";

    return (
        <AppLayout title="Profile" description="Manage your recruiter account and security.">
            <div className="grid gap-6 xl:grid-cols-[1.15fr_0.85fr]">
                <div className="space-y-6">
                    <section className={cardClass}>
                        <div className="flex flex-col gap-5 sm:flex-row sm:items-center">
                            <ProfileAvatar user={user} className="h-24 w-24" textClassName="text-2xl" />
                            <div className="min-w-0 flex-1">
                                <h2 className="truncate text-2xl font-semibold text-slate-900">{user.full_name}</h2>
                                <p className="mt-1 truncate text-sm text-gray-500">{user.email}</p>
                                <div className="mt-3 flex flex-wrap gap-2 text-xs font-semibold">
                                    <span className="rounded-full bg-blue-50 px-3 py-1 text-blue-700">{accountRoleLabel(user.role)}</span>
                                    <span className="rounded-full bg-emerald-50 px-3 py-1 text-emerald-700">Active</span>
                                </div>
                            </div>
                            <div className="flex flex-wrap gap-2">
                                <input ref={fileInput} type="file" accept="image/jpeg,image/png,image/webp" onChange={selectPhoto} className="hidden" />
                                <button type="button" disabled={profileBusy} onClick={() => fileInput.current?.click()} className={`${buttonClass} bg-blue-600 text-white hover:bg-blue-700`}>
                                    <Camera size={16} className="mr-2 inline" />
                                    {user.has_profile_image ? "Change photo" : "Upload photo"}
                                </button>
                                {user.has_profile_image && (
                                    <button type="button" disabled={profileBusy} onClick={removePhoto} className={`${buttonClass} border border-red-200 text-red-600 hover:bg-red-50`}>
                                        <Trash2 size={16} className="mr-2 inline" />Remove
                                    </button>
                                )}
                            </div>
                        </div>
                        {profileMessage && <p aria-live="polite" className="mt-4 text-sm text-emerald-700">{profileMessage}</p>}
                        {profileError && <p role="alert" className="mt-4 text-sm text-red-600">{profileError}</p>}
                    </section>

                    <section className={cardClass}>
                        <div className="flex items-center justify-between gap-4">
                            <h2 className="text-lg font-semibold text-slate-900">Personal Information</h2>
                            {!editing && <button type="button" onClick={beginEdit} className={`${buttonClass} border border-gray-200 text-gray-700 hover:bg-gray-50`}>Edit</button>}
                        </div>
                        {editing ? (
                            <form onSubmit={saveProfile} className="mt-5">
                                <label htmlFor="profile-full-name" className="text-sm font-medium text-gray-700">Full name</label>
                                <input id="profile-full-name" value={fullName} maxLength={255} disabled={profileBusy} onChange={(event) => setFullName(event.target.value)} className="mt-2 w-full rounded-xl border border-gray-300 px-4 py-3 outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-100" />
                                <div className="mt-4 flex gap-2">
                                    <button type="submit" disabled={profileBusy} className={`${buttonClass} bg-blue-600 text-white hover:bg-blue-700`}>Save</button>
                                    <button type="button" disabled={profileBusy} onClick={cancelEdit} className={`${buttonClass} border border-gray-200 text-gray-700 hover:bg-gray-50`}>Cancel</button>
                                </div>
                            </form>
                        ) : (
                            <dl className="mt-5 divide-y divide-gray-100">
                                {details.slice(0, 2).map((detail) => <DetailRow key={detail.label} {...detail} />)}
                            </dl>
                        )}
                    </section>

                    <section className={cardClass}>
                        <h2 className="text-lg font-semibold text-slate-900">Account Information</h2>
                        <dl className="mt-5 divide-y divide-gray-100">
                            {details.slice(2).map((detail) => <DetailRow key={detail.label} {...detail} icon={detail.label === "Role"} />)}
                        </dl>
                    </section>
                </div>

                <section className={`${cardClass} h-fit`}>
                    <h2 className="text-lg font-semibold text-slate-900">Security</h2>
                    <p className="mt-1 text-sm text-gray-500">Changing your password signs you out of all active sessions.</p>
                    <form onSubmit={submitPassword} className="mt-5 space-y-4">
                        <PasswordField id="current-password" label="Current password" value={passwords.current_password} disabled={passwordBusy} autoComplete="current-password" onChange={(value) => setPasswords({ ...passwords, current_password: value })} />
                        <PasswordField id="new-password" label="New password" value={passwords.new_password} disabled={passwordBusy} autoComplete="new-password" onChange={(value) => setPasswords({ ...passwords, new_password: value })} />
                        <PasswordField id="confirm-password" label="Confirm new password" value={passwords.confirm_password} disabled={passwordBusy} autoComplete="new-password" onChange={(value) => setPasswords({ ...passwords, confirm_password: value })} />
                        {passwordError && <p role="alert" className="text-sm text-red-600">{passwordError}</p>}
                        <button type="submit" disabled={passwordBusy} className={`${buttonClass} bg-slate-900 text-white hover:bg-slate-800`}>
                            <CheckCircle2 size={16} className="mr-2 inline" />{passwordBusy ? "Changing…" : "Change password"}
                        </button>
                    </form>
                </section>
            </div>
        </AppLayout>
    );
}


function DetailRow({ label, value, icon = false }: { label: string; value: string; icon?: boolean }) {
    return <div className="grid gap-1 py-4 sm:grid-cols-[10rem_1fr]"><dt className="text-sm font-medium text-gray-500">{label}</dt><dd className="flex items-center gap-2 break-words text-sm font-semibold text-slate-900">{icon && <ShieldCheck size={16} className="text-green-600" aria-hidden="true" />}{value}</dd></div>;
}


function PasswordField({ id, label, value, disabled, autoComplete, onChange }: { id: string; label: string; value: string; disabled: boolean; autoComplete: string; onChange: (value: string) => void }) {
    return <div><label htmlFor={id} className="text-sm font-medium text-gray-700">{label}</label><PasswordInput id={id} value={value} disabled={disabled} autoComplete={autoComplete} onChange={(event) => onChange(event.target.value)} /></div>;
}
