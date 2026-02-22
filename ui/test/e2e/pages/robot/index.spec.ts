import type { components } from '~/client/api';
type RobotProfile = components['schemas']['RobotProfile'];
describe('Robot List', () => {
  before(() => {
    cy.fixture('seed').then((data: Array<RobotProfile>) => {
      data.forEach((element: RobotProfile) => {
        cy.request("POST", 'http://localhost:8000/api/v1/robot/', element);
      });
    });
  })
  it('should display a collection of robots', () => {
    cy.visit('/robot');
    cy.get('.robot-item', { timeout: 80000 }).should('be.visible');
  })
});
