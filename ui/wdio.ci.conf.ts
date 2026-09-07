import { browser } from '@wdio/globals';
import { config as shared } from './wdio.conf';

export const config: WebdriverIO.Config = {
  ...shared,
  ...{
    baseUrl: 'http://localhost:8080',

    capabilities: [{
      browserName: 'chrome',
      // FLAGGED (subtask 09): the mock IdP (ci/mock-idp, :8443) self-signs
      // TLS inside the container; headless Chrome here has no mkcert CA.
      // acceptInsecureCerts keeps e2e runnable against local self-signed TLS.
      acceptInsecureCerts: true,
      'goog:chromeOptions': {

        args: ['start-maximized', 'headless', 'disable-gpu']
      }
    }],
    async afterTest(test, context, result) {
      if (result.error) {
        // Titles can contain '/' and ',' (e.g. "...session, /robot renders...");
        // unsanitized they make saveScreenshot write into missing subdirectories.
        const safeTitle = test.title.replace(/[^a-zA-Z0-9._-]+/g, '-');
        const screenshot = `./test/logs/FAIL-${browser.capabilities.browserName}-${safeTitle}.png`;
        await browser.saveScreenshot(screenshot);
      }
    },
  }
}
