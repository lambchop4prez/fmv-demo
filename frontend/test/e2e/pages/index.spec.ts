describe('The main page', () => {
    it('displays the Go button.', function () {
        cy.visit("/");
        cy.get('button#go').should('be.visible');
        cy.get('button#go').click();
        cy.url().should('include', '/robot');
    });
});
