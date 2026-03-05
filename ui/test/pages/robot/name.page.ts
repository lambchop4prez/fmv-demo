import { $ } from "@wdio/globals";
import Page from "../page"

class RobotProfilePage extends Page {

  public get name() {
    return $('#name');
  }
  public open(name: string) {
    return super.open(`/robot/${name}`);
  }
}

export default new RobotProfilePage();
