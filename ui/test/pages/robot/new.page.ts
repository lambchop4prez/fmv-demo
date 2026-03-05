import { $ } from "@wdio/globals";
import Page from "../page";

interface RobotProfile {
  name: string;
  is_great: boolean;
  location: string;
  description: string;
}

class NewRobotPage extends Page {
  public get txtName() {
    return $('#name');
  }

  public get chkIsGreat() {
    return $('#is_great');
  }

  public get txtLocation() {
    return $('#location');
  }

  public get txtDescription() {
    return $('#description');
  }

  public get btnSubmit() {
    return $('form button[type="submit"]');
  }

  public async check(is_great: boolean) {
    if (is_great) {
      await this.chkIsGreat.click();
    }
  }

  public async fill(robot: RobotProfile) {
    await Promise.all([
      this.txtName.setValue(robot.name),
      this.check(robot.is_great),
      this.txtLocation.setValue(robot.location),
      this.txtDescription.setValue(robot.description)
    ])
  }

  public async submit() {
    await this.btnSubmit.click();
  }

  public open() {
    return super.open('/robot/new');
  }
}
export default new NewRobotPage();
