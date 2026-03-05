import { expect } from '@wdio/globals';
import RobotListPage from '../../pages/robot/index.page';

describe('Robot List Page', () => {
  it('should display a new button', async () => {
    await RobotListPage.open();
    await expect(RobotListPage.btnNew).toBeDisplayed();
    await expect(RobotListPage.btnNew).toHaveText('New');
  });
});
