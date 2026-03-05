import { $ } from "@wdio/globals";
import Page from "./page";

class HomePage extends Page {

  public get btnGo() {
    return $('#go');
  }

  public async go() {
    await this.btnGo.click();
  }

  public open() {
    return super.open('/')
  }
}
export default new HomePage();
