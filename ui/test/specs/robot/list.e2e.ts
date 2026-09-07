import { expect } from '@wdio/globals';
import RobotListPage from '../../pages/robot/index.page';
import { loginViaTestSession } from '../../utils/session';

describe('Robot List Page', () => {
  // The default layout guard redirects to /login without a session;
  // bootstrap the API session before each test (afterTest reloads it away).
  beforeEach(async () => {
    await loginViaTestSession();
  });

  it('should display a new button', async () => {
    await RobotListPage.open();
    await expect(RobotListPage.btnNew).toBeDisplayed();
    await expect(RobotListPage.btnNew).toHaveText('New');
  });
});
