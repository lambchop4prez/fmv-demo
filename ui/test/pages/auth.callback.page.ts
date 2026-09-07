import { $ } from "@wdio/globals";
import Page from "./page";

/**
 * OIDC callback page (ui/src/pages/callback.vue).
 *
 * Success path: renders a spinner + "Processing SSO login...", completes the
 * code flow via signinCallback(), POSTs the id_token to /auth/login (D1=a)
 * and router.push("/robot"). On any failure it renders an error block:
 * <h2>Error</h2>, the message, and a "Back" button.
 */
class AuthCallbackPage extends Page {
  public get processing() {
    return $("h2=Processing SSO login...");
  }

  /** Error heading — callback.vue renders t("error") == "Error" in an h2. */
  public get errorHeading() {
    return $("h2=Error");
  }

  public get errorBackButton() {
    return $("button=Back");
  }

  public open(query = "") {
    return super.open(`/callback${query}`);
  }
}

export default new AuthCallbackPage();
