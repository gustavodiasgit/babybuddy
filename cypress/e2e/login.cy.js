describe("Authentication", () => {
  it("logs in with valid credentials", () => {
    cy.login();

    cy.get("body").should("be.visible");
  });
});
