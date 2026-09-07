import { $, browser, expect } from "@wdio/globals";
import AuthCallbackPage from "../../pages/auth.callback.page";
import AuthLoginPage from "../../pages/auth.login.page";
import MockIdpPage from "../../pages/auth.idp.page";
import RobotListPage from "../../pages/robot/index.page";

/**
 * OIDC auth e2e happy path (oidc-auth subtask 09, docs/oidc-plan.md §7).
 *
 * Drives the full redirect flow against the mock IdP (decision D6,
 * ci/mock-idp, issuer https://localhost:8443/realms/fmv):
 *
 *   /login -> SSO click -> mock IdP authorize -> credentials ->
 *   /callback (code exchange + POST /auth/login session cookie, D1=a) ->
 *   protected /robot renders -> /logout -> session cleared.
 *
 * The main happy path is ONE test because the session cookie must survive
 * across steps; the base config's afterTest() reloads the browser session
 * between tests, so each test starts logged out.
 *
 * Notes:
 * - apiBase: the ci container stack serves the API over http://localhost:8000;
 *   the dev flow serves it over https (uvicorn --ssl-*). Derived from baseUrl.
 * - apiStatus() returns 0 when the fetch itself is blocked (CORS/network) so
 *   failures report a number instead of throwing inside the browser.
 */

/** GET an API path from the app origin with the session cookie attached.
 * The API base is derived from the live page origin: the ci stack serves the
 * frontend on http://localhost:8080 + API on http://localhost:8000; the dev
 * flow uses https. Returns 0 when the fetch is blocked (CORS/network). */
async function apiStatus(path: string): Promise<number> {
  return browser.execute(
    async (p: string): Promise<number> => {
      const origin = window.location.origin;
      // Dev API runs on https :8800 (src/mod.just uvicorn --port 8800,
      // same origin as VITE_API_ENDPOINT); the ci stack serves it plain :8000.
      const base = origin.includes(":8080")
        ? "http://localhost:8000/api/v1"
        : "https://localhost:8800/api/v1";
      try {
        const res = await fetch(`${base}${p}`, { credentials: "include" });
        return res.status;
      }
      catch (err) {
        console.log(err)
        // CORS blocked or network error — caller asserts on the number.
        return 0;
      }
    },
    path,
  );
}

describe("OIDC auth happy path", () => {
  it("login via mock IdP establishes a session, /robot renders, logout clears the session", async () => {
    // Arrange: open the login page (public layout, logged-out).
    await AuthLoginPage.open();
    await expect(AuthLoginPage.ssoButton).toBeDisplayed();
    await expect(AuthLoginPage.ssoButton).toHaveText("Login with SSO");

    // Negative guard: before the IdP round-trip there is no session.
    expect(await apiStatus("/robot/")).toBe(401);

    // Act: SSO click triggers UserManager.signinRedirect().
    await AuthLoginPage.ssoButton.click();

    // Assert: browser was redirected to the mock IdP authorize endpoint.
    await browser.waitUntil(async () => (await browser.getUrl()).includes("/realms/fmv/authorize"), {
      timeoutMsg: "never redirected to mock IdP authorize",
    });

    // Act: submit credentials at the mock IdP (accepts any, issues a code).
    await MockIdpPage.acceptCredentials();

    // Assert: IdP 302s to /callback?code=...&state=..., the callback page
    // completes the code flow and exchanges the id_token for the session
    // cookie, then router.push("/robot") lands us on the protected page.
    await browser.waitUntil(async () => (await browser.getUrl()).includes("/robot"), {
      timeoutMsg: "never landed on /robot",
    });

    // Protected robot page renders: New button visible, no error block.
    await expect(RobotListPage.btnNew).toBeDisplayed();
    await expect($("text=Error")).not.toBeDisplayed();

    // Session cookie is established: protected API answers 200 (not 401/403).
    expect(await apiStatus("/robot/")).toBe(200);

    // Act: log out through the app's logout page.
    await browser.url("/logout");

    // Assert: logout completes and the app lands on the login page
    // (logout.vue router.push("/login"); stays on /logout if the flow breaks).
    await browser.waitUntil(async () => (await browser.getUrl()).endsWith("/login"), {
      timeoutMsg: "logout did not land on /login",
    });

    // Session is cleared: protected API 401, and the layout guard now
    // bounces /robot to /login before the page can fetch the list.
    expect(await apiStatus("/robot/")).toBe(401);
    await browser.url("/robot");
    await browser.waitUntil(async () => (await browser.getUrl()).includes("/login"), {
      timeoutMsg: "guard did not redirect /robot to /login after logout",
    });
  });

  it("rejects the protected robot API without a session", async () => {
    // Arrange: fresh browser session (afterTest reload), no login.
    await AuthLoginPage.open();

    // Act + Assert: cookie-only protection answers 401 (unauthenticated).
    expect(await apiStatus("/robot/")).toBe(401);

    // The default-layout guard probes GET /auth/session on mount; with no
    // session it redirects to /login before the page ever fetches the list.
    await browser.url("/robot");
    await browser.waitUntil(async () => (await browser.getUrl()).includes("/login"), {
      timeoutMsg: "guard did not redirect /robot to /login",
    });
  });

  it("callback page surfaces an error for a tampered redirect", async () => {
    // Arrange + Act: hit /callback with a state/code the app never issued.
    await AuthCallbackPage.open("?state=tampered-state&code=tampered-code");

    // Assert: signinCallback() rejects with unknown state; the error block
    // (heading + Back button) renders instead of hanging on "Processing".
    await expect(AuthCallbackPage.errorHeading).toBeDisplayed();
    await expect(AuthCallbackPage.errorBackButton).toBeDisplayed();
  });
});
