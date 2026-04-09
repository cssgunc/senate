const TOKEN_KEY = "admin_access_token";

function canUseStorage(): boolean {
    return typeof window !== "undefined" && typeof window.localStorage !== "undefined";
}

export function setToken(token: string): void {
    if (!canUseStorage()) {
        return;
    }
    localStorage.setItem(TOKEN_KEY, token);
}

export function getToken(): string | null {
    if (!canUseStorage()) {
        return null;
    }
    return localStorage.getItem(TOKEN_KEY);
}

export function clearToken(): void {
    if (!canUseStorage()) {
        return;
    }
    localStorage.removeItem(TOKEN_KEY);
}
