import { config as shared } from './wdio.conf';

export const config: WebdriverIO.Config = {
  ...shared,
  ...{
    baseUrl: 'http://localhost:4173',
    capabilities: [{
      browserName: 'chrome',
      'goog:chromeOptions': {
        args: ['start-maximized', 'headless', 'disable-gpu']
      }
    }]
  }
}
