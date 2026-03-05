import { browser, expect } from '@wdio/globals'
import HomePage from '../pages/index.page'

describe('Home page', () => {
  it('should display a go button', async () => {
    await HomePage.open();
    await expect(HomePage.btnGo).toHaveText("GO");
  });
  it('should have a title', async () => {
    await HomePage.open();
    await expect(browser).toHaveTitle('Home');
  });
  it('should navigate on button click', async () => {
    await HomePage.open();
    await HomePage.go();
    await expect(browser).toHaveUrl(expect.stringContaining('robot'))
  });
})
