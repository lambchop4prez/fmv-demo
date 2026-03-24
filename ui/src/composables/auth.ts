import { UserManager, UserManagerSettings } from 'oidc-client-ts';


export function useUserManagerSettings(): UserManagerSettings {
  return {
    authority: import.meta.env.VITE_OIDC_ISSUER_URI,
    client_id: import.meta.env.VITE_OIDC_CLIENT_ID,
    redirect_uri: `${window.location.origin}/callback`,
    response_type: "code",
    scope: "openid email profile",
    automaticSilentRenew: true
  }
}

export function useUserManager(): UserManager {
  return new UserManager(useUserManagerSettings())
}

