import { config as shared } from './wdio.conf';

export const config: WebdriverIO.Config = {
  ...shared,
  ...{
    baseUrl: 'https://localhost:5173',
    capabilities: [{
      browserName: 'chrome',
      // FLAGGED (subtask 09): the mock IdP (ci/mock-idp, :8443) serves a
      // self-signed cert when .cert/ mkcert certs are absent, and the dev
      // API/vite servers use mkcert certs that only trusted machines accept.
      // acceptInsecureCerts keeps e2e runnable against local self-signed TLS.
      // Run `just setup` (mkcert) to get trusted certs instead.
      acceptInsecureCerts: true,
      'goog:chromeOptions': {
        args: ['start-maximized', 'disable-gpu']
      }
    }]
  }
}
