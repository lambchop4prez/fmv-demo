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
        const screenshot = `./test/logs/FAIL-${browser.capabilities.browserName}-${test.title.split(' ').join('-')}.png`;
        await browser.saveScreenshot(screenshot);
      }
    },
  }
}
