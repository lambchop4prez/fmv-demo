import { $ } from "@wdio/globals";
import Page from "../page"

class RobotProfilePage extends Page {

  public get name() {
    return $('h3');
  }
  public open(name: string) {
    return super.open(`/robot/${name}`);
  }
}

export default new RobotProfilePage();
