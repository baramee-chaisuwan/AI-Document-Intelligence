"use client";

import {
    createContext,
    useCallback,
    useContext,
    useEffect,
    useMemo,
    useState,
} from "react";

import {
    AUTH_STATE_EVENT,
    clearAccessToken,
    getAccessToken,
    setAccessToken,
} from "@/lib/token-storage";
import {
    getCurrentUser,
    loginUser,
} from "@/services/auth";
import type {
    AuthUser,
    LoginCredentials,
} from "@/types/auth";


interface AuthContextValue {
    user: AuthUser | null;
    loading: boolean;
    isAdmin: boolean;
    login: (
        credentials: LoginCredentials
    ) => Promise<AuthUser>;
    logout: () => void;
    refreshUser: () => Promise<void>;
}


const AuthContext = createContext<
    AuthContextValue | undefined
>(undefined);


export function AuthProvider({
    children,
}: {
    children: React.ReactNode;
}) {

    const [user, setUser] = (
        useState<AuthUser | null>(null)
    );

    const [loading, setLoading] = (
        useState(true)
    );


    const refreshUser = useCallback(
        async () => {

            const token = getAccessToken();

            if (!token) {
                setUser(null);
                setLoading(false);
                return;
            }

            setLoading(true);

            try {

                const currentUser = (
                    await getCurrentUser()
                );

                setUser(currentUser);

            } catch {

                clearAccessToken();
                setUser(null);

            } finally {

                setLoading(false);

            }

        },
        []
    );


    useEffect(() => {

        const initializationTimer = window.setTimeout(
            () => {
                void refreshUser();
            },
            0
        );

        const handleAuthStateChange = () => {

            if (!getAccessToken()) {
                setUser(null);
                setLoading(false);
            }

        };

        window.addEventListener(
            AUTH_STATE_EVENT,
            handleAuthStateChange
        );

        return () => {

            window.clearTimeout(
                initializationTimer
            );

            window.removeEventListener(
                AUTH_STATE_EVENT,
                handleAuthStateChange
            );

        };

    }, [refreshUser]);


    const login = useCallback(
        async (
            credentials: LoginCredentials
        ) => {

            const tokenResponse = await loginUser(
                credentials
            );

            setAccessToken(
                tokenResponse.access_token
            );

            try {

                const currentUser = (
                    await getCurrentUser()
                );

                setUser(currentUser);

                return currentUser;

            } catch (error) {

                clearAccessToken();
                setUser(null);

                throw error;

            }

        },
        []
    );


    const logout = useCallback(() => {

        clearAccessToken();
        setUser(null);

        if (typeof window !== "undefined") {

            window.location.replace(
                "/login"
            );

        }

    }, []);


    const value = useMemo<AuthContextValue>(
        () => ({
            user,
            loading,
            isAdmin: user?.role === "admin",
            login,
            logout,
            refreshUser,
        }),
        [
            user,
            loading,
            login,
            logout,
            refreshUser,
        ]
    );


    return (

        <AuthContext.Provider value={value}>
            {children}
        </AuthContext.Provider>

    );

}


export function useAuth(): AuthContextValue {

    const context = useContext(AuthContext);

    if (!context) {

        throw new Error(
            "useAuth must be used inside AuthProvider"
        );

    }

    return context;

}
