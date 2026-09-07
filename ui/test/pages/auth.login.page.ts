import { $ } from "@wdio/globals";
import Page from "./page";

/**
 * Our app's /login page (ui/src/pages/login.vue -> LoginForm.vue).
 * Renders a single SSO submit button that calls UserManager.signinRedirect().
 */
class AuthLoginPage extends Page {
  /** The SSO button is the only submit control on the login card. */
  public get ssoButton() {
    return $('button[type="submit"]');
  }

  public get title() {
    return $("h2=Log in to your account");
  }

  public open() {
    return super.open("/login");
  }
}

export default new AuthLoginPage();
