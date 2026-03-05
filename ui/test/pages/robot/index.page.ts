import { $ } from "@wdio/globals";
import Page from "../page";

class RobotListPage extends Page {

  public get btnNew() {
    return $('#new');
  }

  public open() {
    return super.open('/robot')
  }
}

export default new RobotListPage();
