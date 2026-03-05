import { expect } from '@wdio/globals';
import NewRobotPage from '../../pages/robot/new.page';
import RobotProfilePage from '../../pages/robot/name.page';

describe('New Robot Form', () => {
  xit('should display fields', async () => {
    await NewRobotPage.open();
    await expect(NewRobotPage.txtName).toBeDisplayed();
    await expect(NewRobotPage.chkIsGreat).toBeDisplayed();
    await expect(NewRobotPage.txtLocation).toBeDisplayed();
    await expect(NewRobotPage.txtDescription).toBeDisplayed();
  });
  xit('should submit a new robot and navigate to profile', async () => {
    await NewRobotPage.open();
    const robot = {
      name: "Crow",
      is_great: false,
      location: "Satellite of Love",
      description: "You know you want me baby!"
    };
    await NewRobotPage.fill(robot);
    await NewRobotPage.submit();
    await RobotProfilePage.name.waitForDisplayed();
    await expect(RobotProfilePage.name).toHaveText(robot.name);

  });
});
