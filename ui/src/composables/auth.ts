import type { User, UserManagerSettings } from "oidc-client-ts";
import { InMemoryWebStorage, UserManager, WebStorageStateStore } from "oidc-client-ts";

// Typed access to the VITE_OIDC_* env vars (provided via .mise.toml).
declare global {
  interface ImportMetaEnv {
    readonly VITE_OIDC_AUTHORITY?: string;
    readonly VITE_OIDC_CLIENT_ID?: string;
    readonly VITE_OIDC_REDIRECT_URI?: string;
    readonly VITE_OIDC_RESPONSE_TYPE?: string;
    readonly VITE_OIDC_SCOPE?: string;
    readonly VITE_OIDC_POST_LOGOUT_REDIRECT_URI?: string;
    readonly VITE_OIDC_SILENT_REDIRECT_URI?: string;
    readonly VITE_API_ENDPOINT?: string;
  }
}

export const apiBaseUrl = import.meta.env.VITE_API_ENDPOINT || "http://localhost:8800/api/v1";

// vite-ssg prerenders on the server, where `window` does not exist.
function appOrigin(): string {
  return typeof window !== "undefined" ? window.location.origin : "";
}

export function useUserManagerSettings(): UserManagerSettings {
  const redirectUri = import.meta.env.VITE_OIDC_REDIRECT_URI || `${appOrigin()}/callback`;
  return {
    // Required provider config; unset values fail at signin with a clear error.
    authority: import.meta.env.VITE_OIDC_AUTHORITY ?? "",
    client_id: import.meta.env.VITE_OIDC_CLIENT_ID ?? "fmv-demo-ui",
    redirect_uri: redirectUri,
    post_logout_redirect_uri: import.meta.env.VITE_OIDC_POST_LOGOUT_REDIRECT_URI || `${appOrigin()}/logout`,
    // Silent renew reuses the callback page; the code flow completes there and
    // re-exchanges the id_token for a fresh session cookie.
    silent_redirect_uri: import.meta.env.VITE_OIDC_SILENT_REDIRECT_URI || redirectUri,
    response_type: import.meta.env.VITE_OIDC_RESPONSE_TYPE ?? "code",
    // The backend User model requires name/picture/email claims.
    scope: import.meta.env.VITE_OIDC_SCOPE ?? "openid profile email",
    automaticSilentRenew: true,
    // D4: keep IdP tokens in memory only — never persisted to localStorage/sessionStorage.
    userStore: new WebStorageStateStore({ store: new InMemoryWebStorage() }),
  };
}

// D1=a: exchange the IdP id_token for the API session cookie.
// Plain fetch because the generated client types do not yet declare the
// Authorization header on /auth/login (backend fix lands in a later subtask).
async function exchangeSession(idToken: string): Promise<void> {
  const response = await fetch(`${apiBaseUrl}/auth/login`, {
    method: "POST",
    headers: {
      "Accept": "application/json",
      "Authorization": `Bearer ${idToken}`,
    },
    credentials: "include",
  });
  if (!response.ok) {
    throw new Error(`Session exchange failed: ${response.status} ${response.statusText}`);
  }
}

// Extends UserManager so callback.vue's `signinCallback()` completes the OIDC
// code flow AND establishes the session cookie in one call (D1=a).
class SessionUserManager extends UserManager {
  async signinCallback(url?: string): Promise<User | undefined> {
    const user = await this.signinRedirectCallback(url);
    if (user?.id_token) {
      await exchangeSession(user.id_token);
    }
    return user;
  }

  // D1=a: server-side logout clears the API session cookie; removeUser drops
  // the in-memory IdP user. Replaces the old signoutSilentCallback flow,
  // which threw when /logout was opened directly (no silent-redirect state).
  async signout(): Promise<void> {
    const response = await fetch(`${apiBaseUrl}/auth/logout`, {
      method: "POST",
      credentials: "include",
    });
    if (!response.ok) {
      throw new Error(`Logout failed: ${response.status} ${response.statusText}`);
    }
    await this.removeUser();
  }
}

let instance: SessionUserManager | null = null;

export function useUserManager(): SessionUserManager {
  instance ??= new SessionUserManager(useUserManagerSettings());
  return instance;
}
