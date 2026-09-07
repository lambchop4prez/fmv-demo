import type { IncomingHttpHeaders } from "node:http";
import https from "node:https";
import { browser } from "@wdio/globals";

/**
 * E2E session bootstrap: establishes the API session cookie without driving
 * the browser through the IdP redirect flow.
 *
 *   1. Node POSTs the mock IdP /authorize form (accepts any credentials,
 *      decision D6) and reads the single-use code from the 302 Location.
 *   2. Node POSTs /token and receives an RS256 id_token signed with the
 *      committed test key (fixtures match the API's static JWKS, D2).
 *   3. The browser POSTs /auth/login with that bearer token, so the signed
 *      session cookie is set in the browser (D1=a), then asserts 200.
 *
 * The layout guard then passes on page loads: the in-memory IdP user store
 * (D4) is empty after every reload, so default.vue probes GET /auth/session,
 * which the injected cookie satisfies.
 *
 * Do NOT use this in auth specs that assert logged-out behavior
 * (test/specs/auth/login.e2e.ts drives the real flow itself).
 */

const MOCK_IDP_ORIGIN = "https://localhost:8443";
const ISSUER = `${MOCK_IDP_ORIGIN}/realms/fmv`;
const CLIENT_ID = "fmv-web";

/**
 * API base derived from baseUrl like login.e2e.ts apiStatus(): the ci stack
 * serves the frontend on http://localhost:8080 with the API on plain
 * http://localhost:8000; dev uses the https uvicorn on :8800 (src/mod.just,
 * same origin the app's VITE_API_ENDPOINT points at).
 */
function apiBase(): string {
  // WDIO v9 exposes the resolved config on browser.options, not browser.config.
  const baseUrl = browser.options.baseUrl ?? "";
  return baseUrl.includes(":8080")
    ? "http://localhost:8000/api/v1"
    : "https://localhost:8800/api/v1";
}

interface HttpResponse {
  status: number;
  headers: IncomingHttpHeaders;
  body: string;
}

/** POST a form to a loopback https URL without TLS verification. */
function httpsPostForm(url: string, form: URLSearchParams): Promise<HttpResponse> {
  return new Promise((resolve, reject) => {
    const payload = form.toString();
    const req = https.request(
      url,
      {
        method: "POST",
        // The mock IdP self-signs when mkcert certs are absent (ci/mock-idp
        // _resolve_tls_paths); loopback test traffic only.
        rejectUnauthorized: false,
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
          "Content-Length": Buffer.byteLength(payload),
        },
      },
      (res) => {
        const chunks: Buffer[] = [];
        res.on("data", chunk => chunks.push(chunk));
        res.on("end", () => resolve({
          status: res.statusCode ?? 0,
          headers: res.headers,
          body: Buffer.concat(chunks).toString("utf8"),
        }));
      },
    );
    req.on("error", reject);
    req.end(payload);
  });
}

/** Mint an id_token from the mock IdP: authorize form -> code -> token. */
export async function mintIdToken(username = "e2e-user"): Promise<string> {
  const redirectUri = `${browser.options.baseUrl ?? "https://localhost:5173"}/callback`;
  const authorize = await httpsPostForm(`${ISSUER}/authorize`, new URLSearchParams({
    client_id: CLIENT_ID,
    redirect_uri: redirectUri,
    response_type: "code",
    scope: "openid profile email",
    state: "e2e-bootstrap-state",
    username,
    password: "e2e-pass",
  }));
  if (authorize.status !== 302) {
    throw new Error(`mock IdP /authorize returned ${authorize.status}: ${authorize.body}`);
  }
  const code = new URL(authorize.headers.location ?? "", MOCK_IDP_ORIGIN)
    .searchParams.get("code");
  if (!code) {
    throw new Error("mock IdP /authorize redirect carried no code");
  }

  const token = await httpsPostForm(`${ISSUER}/token`, new URLSearchParams({
    grant_type: "authorization_code",
    code,
    redirect_uri: redirectUri,
    client_id: CLIENT_ID,
  }));
  if (token.status !== 200) {
    throw new Error(`mock IdP /token returned ${token.status}: ${token.body}`);
  }
  const { id_token: idToken } = JSON.parse(token.body) as { id_token?: string };
  if (!idToken) {
    throw new Error("mock IdP /token response contained no id_token");
  }
  return idToken;
}

/**
 * Establish a logged-in API session in the browser. Call from beforeEach in
 * specs that exercise authenticated pages; afterTest reloads the session, so
 * every test needs its own bootstrap.
 */
export async function loginViaTestSession(username = "e2e-user"): Promise<void> {
  const idToken = await mintIdToken(username);
  // Land on the app origin first (login is public) so the cookie exchange
  // runs from the frontend origin, exactly like the real callback flow.
  await browser.url("/login");
  const status = await browser.execute(
    async (base: string, token: string): Promise<number> => {
      const res = await fetch(`${base}/auth/login`, {
        method: "POST",
        headers: { "Accept": "application/json", "Authorization": `Bearer ${token}` },
        credentials: "include",
      });
      return res.status;
    },
    apiBase(),
    idToken,
  );
  if (status !== 200) {
    throw new Error(`e2e session bootstrap failed: POST /auth/login -> ${status}`);
  }
}
