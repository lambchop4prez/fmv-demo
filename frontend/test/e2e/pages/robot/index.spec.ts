import type { components } from '~/client/api';
type RobotProfile = components['schemas']['RobotProfile'];
describe('Robot List', () => {
  before(() => {
    cy.fixture('seed').then((data: Array<RobotProfile>) => {
      data.forEach((element: RobotProfile) => {
        cy.task('httpRequest', {
          url: 'http://localhost:8000/v1/robot/',
          body: element
        });
      });
    });
  })
  it('should display a collection of robots', () => {
    cy.visit('/robot');
    cy.get('.robot-item').should('be.visible');
  })
});
