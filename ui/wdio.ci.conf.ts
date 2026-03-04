import { browser } from '@wdio/globals';
import { config as shared } from './wdio.conf';

export const config: WebdriverIO.Config = {
  ...shared,
  ...{
    baseUrl: 'http://localhost:8080',

    capabilities: [{
      browserName: 'chrome',
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
