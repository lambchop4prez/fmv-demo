describe('The main page', () => {
  it('displays the Go button.', function () {
    cy.visit("/");
    cy.get('#go').should('be.visible');
    cy.get('#go').click();
    cy.url().should('include', '/robot');
  });
});
