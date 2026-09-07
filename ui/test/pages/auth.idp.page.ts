import { $ } from "@wdio/globals";
import Page from "./page";

/**
 * Mock IdP authorize page served by ci/mock-idp/main.py at
 * https://localhost:8443/realms/fmv/authorize (decision D6).
 *
 * The page renders a form with #username, #password and a "Sign in" submit
 * button, plus hidden inputs carrying the original /authorize parameters.
 * The mock accepts ANY credentials and 302s back to redirect_uri with a
 * single-use code.
 *
 * There is no open(): the browser arrives here only via the app's
 * signinRedirect(); the URL is asserted in the spec.
 */
class MockIdpPage extends Page {
  public get username() {
    return $("#username");
  }

  public get password() {
    return $("#password");
  }

  public get btnSubmit() {
    return $('button[type="submit"]');
  }

  /**
   * Hidden input carrying the OIDC redirect_uri the IdP will return to.
   * The spec reads it to decouple from the baked-in VITE_OIDC_REDIRECT_URI
   * (dev/preview/containers may bake different origins).
   */
  public get redirectUri() {
    return $('input[name="redirect_uri"]');
  }

  /** Fill and submit the mock IdP consent form. */
  public async acceptCredentials(username = "e2e-user", password = "e2e-pass") {
    await this.username.waitForDisplayed();
    await this.username.setValue(username);
    await this.password.setValue(password);
    await this.btnSubmit.click();
  }
}

export default new MockIdpPage();
