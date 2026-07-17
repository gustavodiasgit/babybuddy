describe("Sleep registration", () => {
  beforeEach(() => {
    cy.login();
  });

  it("registers a completed sleep period", () => {
    cy.visit("http://127.0.0.1:8000/sleep/add/");

    cy.get('input[name="start"]').clear().type("2026-07-15T22:00");

    cy.get('input[name="end"]').clear().type("2026-07-16T06:00");

    cy.contains("button", "Submit").click();
  });
});
