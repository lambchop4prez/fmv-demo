import type { Mock } from "vitest";
import { User, UserManager, WebStorageStateStore } from "oidc-client-ts";
import { afterEach, beforeAll, beforeEach, describe, expect, it, vi } from "vitest";

// auth.ts captures VITE_API_ENDPOINT when the module is first evaluated, so
// the env must be stubbed *before* the module is imported. A static import
// would capture the real env values; the module is therefore imported
// dynamically in beforeAll, after the stubs are in place.
const TEST_ENV = {
  VITE_API_ENDPOINT: "https://api.example.com/api/v1",
  VITE_OIDC_AUTHORITY: "https://idp.example.com/realms/test",
  VITE_OIDC_CLIENT_ID: "fmv-demo-test-client",
  VITE_OIDC_REDIRECT_URI: "https://app.example.com/callback",
  VITE_OIDC_RESPONSE_TYPE: "code",
  VITE_OIDC_SCOPE: "openid profile email offline_access",
  VITE_OIDC_POST_LOGOUT_REDIRECT_URI: "https://app.example.com/logout",
  VITE_OIDC_SILENT_REDIRECT_URI: "https://app.example.com/callback",
} as const;

const CALLBACK_URL = `${TEST_ENV.VITE_OIDC_REDIRECT_URI}?code=test-code&state=test-state`;
const ID_TOKEN = "test-id-token";

type AuthModule = typeof import("../auth");
// Structural stub: exchangeSession only reads ok/status/statusText, so no
// real Response is needed and the assertion stays environment-independent.
type StubResponse = { ok: boolean; status: number; statusText: string };
type FetchStub = (url: RequestInfo | URL, init?: RequestInit) => Promise<StubResponse>;

let useUserManager: AuthModule["useUserManager"];
let useUserManagerSettings: AuthModule["useUserManagerSettings"];

function stubOidcEnv(): void {
  for (const [key, value] of Object.entries(TEST_ENV)) {
    vi.stubEnv(key, value);
  }
}

function jsonResponse(status = 200, statusText = "OK"): StubResponse {
  return { ok: status >= 200 && status < 300, status, statusText };
}

function makeUser(overrides: { id_token?: string } = {}): User {
  return new User({
    access_token: "test-access-token",
    token_type: "Bearer",
    scope: "openid profile email",
    profile: {
      sub: "user-1",
      iss: TEST_ENV.VITE_OIDC_AUTHORITY,
      aud: TEST_ENV.VITE_OIDC_CLIENT_ID,
      exp: 9999999999,
      iat: 1000000000,
    },
    id_token: ID_TOKEN,
    ...overrides,
  });
}

beforeAll(async () => {
  stubOidcEnv();
  const auth = await import("../auth");
  useUserManager = auth.useUserManager;
  useUserManagerSettings = auth.useUserManagerSettings;
});

beforeEach(() => {
  // afterEach unstubs all envs; re-stub so settings assembly stays deterministic
  // for every test regardless of execution order.
  stubOidcEnv();
});

afterEach(() => {
  vi.unstubAllEnvs();
  vi.restoreAllMocks();
  vi.unstubAllGlobals();
});

describe("useUserManagerSettings", () => {
  it("assembles provider settings from VITE_OIDC_* env values", () => {
    const settings = useUserManagerSettings();

    expect(settings.authority).toBe(TEST_ENV.VITE_OIDC_AUTHORITY);
    expect(settings.client_id).toBe(TEST_ENV.VITE_OIDC_CLIENT_ID);
    expect(settings.redirect_uri).toBe(TEST_ENV.VITE_OIDC_REDIRECT_URI);
    expect(settings.scope).toBe(TEST_ENV.VITE_OIDC_SCOPE);
    expect(settings.response_type).toBe(TEST_ENV.VITE_OIDC_RESPONSE_TYPE);
    expect(settings.post_logout_redirect_uri).toBe(TEST_ENV.VITE_OIDC_POST_LOGOUT_REDIRECT_URI);
    expect(settings.silent_redirect_uri).toBe(TEST_ENV.VITE_OIDC_SILENT_REDIRECT_URI);
    expect(settings.automaticSilentRenew).toBe(true);
  });

  it("stores IdP tokens in memory, never in localStorage or sessionStorage", async () => {
    const settings = useUserManagerSettings();

    expect(settings.userStore).toBeInstanceOf(WebStorageStateStore);
    const store = settings.userStore as WebStorageStateStore;

    const storageWrites = vi.spyOn(Storage.prototype, "setItem");
    await store.set("auth-test-probe", "probe-value");

    // The store must round-trip in memory while leaving web storage untouched (D4).
    expect(storageWrites).not.toHaveBeenCalled();
    expect(await store.get("auth-test-probe")).toBe("probe-value");
    expect(window.localStorage.getItem("auth-test-probe")).toBeNull();
    expect(window.sessionStorage.getItem("auth-test-probe")).toBeNull();
  });
});

describe("useUserManager", () => {
  it("returns a single UserManager instance across calls", () => {
    expect(useUserManager()).toBeInstanceOf(UserManager);
    expect(useUserManager()).toBe(useUserManager());
  });
});

describe("signinCallback session exchange (D1=a)", () => {
  let fetchMock: Mock<FetchStub>;

  beforeEach(() => {
    fetchMock = vi.fn<FetchStub>();
    vi.stubGlobal("fetch", fetchMock);
  });

  it("POSTs the id_token to /auth/login with bearer auth and credentials", async () => {
    const signinSpy = vi.spyOn(UserManager.prototype, "signinRedirectCallback").mockResolvedValue(makeUser());
    fetchMock.mockResolvedValue(jsonResponse());

    await useUserManager().signinCallback(CALLBACK_URL);

    expect(signinSpy).toHaveBeenCalledWith(CALLBACK_URL);
    expect(fetchMock).toHaveBeenCalledTimes(1);

    const [url, init] = fetchMock.mock.calls[0];
    expect(url).toBe(`${TEST_ENV.VITE_API_ENDPOINT}/auth/login`);
    expect(init?.method).toBe("POST");

    const headers = new Headers(init?.headers);
    expect(headers.get("authorization")).toBe(`Bearer ${ID_TOKEN}`);
    expect(headers.get("accept")).toBe("application/json");
    expect(init?.credentials).toBe("include");
  });

  it("returns the resolved user after a successful exchange", async () => {
    const user = makeUser();
    vi.spyOn(UserManager.prototype, "signinRedirectCallback").mockResolvedValue(user);
    fetchMock.mockResolvedValue(jsonResponse());

    await expect(useUserManager().signinCallback(CALLBACK_URL)).resolves.toBe(user);
  });

  it("throws when the session exchange responds with a non-2xx status", async () => {
    vi.spyOn(UserManager.prototype, "signinRedirectCallback").mockResolvedValue(makeUser());
    fetchMock.mockResolvedValue(jsonResponse(401, "Unauthorized"));

    // The rejection must surface to callback.vue's error UI.
    await expect(useUserManager().signinCallback(CALLBACK_URL)).rejects.toThrow(/Session exchange failed: 401 Unauthorized/);
  });

  it("does not call /auth/login when the callback resolves without a user", async () => {
    vi.spyOn(UserManager.prototype, "signinRedirectCallback").mockResolvedValue(undefined as unknown as User);

    const user = await useUserManager().signinCallback(CALLBACK_URL);

    expect(user).toBeUndefined();
    expect(fetchMock).not.toHaveBeenCalled();
  });

  it("does not call /auth/login when the user has no id_token", async () => {
    const user = makeUser({ id_token: undefined });
    vi.spyOn(UserManager.prototype, "signinRedirectCallback").mockResolvedValue(user);

    const result = await useUserManager().signinCallback(CALLBACK_URL);

    expect(result).toBe(user);
    expect(result?.id_token).toBeUndefined();
    expect(fetchMock).not.toHaveBeenCalled();
  });
});
