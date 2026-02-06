describe('Robot List', () => {
  it('should display a collection of robots', () => {
    cy.visit('/robot');
    cy.get('.robot-item').should('be.visible');
  })
});
