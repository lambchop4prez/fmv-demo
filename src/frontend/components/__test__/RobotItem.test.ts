import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/vue";
import RobotItem from "../RobotItem.vue";

const fakeRobot = {
  name: "Fake",
  is_great: false,
};

describe("RobotItem", () => {
  it("should render with the robots name", async () => {
    render(RobotItem, { props: { robot: fakeRobot } });
    expect(await screen.findByText(fakeRobot.name)).toBeInTheDocument();
  });
});
