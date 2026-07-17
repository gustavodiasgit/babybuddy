describe("Feeding registration", () => {
  beforeEach(() => {
    cy.login();
  });

  it("registers a feeding", () => {
    cy.visit("http://127.0.0.1:8000/feedings/add/");

    cy.get("body").should("be.visible");
  });
});
