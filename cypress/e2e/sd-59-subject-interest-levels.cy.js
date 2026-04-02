describe("SD-59 Subject Interest Levels", () => {
  beforeEach(() => {
    cy.visit("cypress/fixtures/subject-interest-page.html");
  });

  afterEach(function () {
    const safeName = this.currentTest.title
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, "-")
      .replace(/^-|-$/g, "");
    cy.screenshot(`sd-59-${safeName}`, { capture: "viewport" });
  });

  it("AC1 - allows marking subject interest levels", () => {
    cy.contains(".subject-name", "Mathematics").parent().within(() => {
      cy.get(".star").eq(4).click(); // Click 5 stars
    });

    cy.contains(".subject-name", "Physics").parent().within(() => {
      cy.get(".star").eq(2).click(); // Click 3 stars
    });

    cy.contains("button", "Save Selections").click();
    cy.get(".success-message").should("have.class", "show");
  });

  it("AC2 - allows changing selected interest level before saving", () => {
    cy.contains(".subject-name", "Algorithms").parent().within(() => {
      cy.get(".star").eq(1).click(); // First click 2 stars
      cy.get(".rating-value").should("contain", "2");
      cy.get(".star").eq(3).click(); // Then change to 4 stars
      cy.get(".rating-value").should("contain", "4");
    });

    cy.contains("button", "Save Selections").click();
    cy.get(".success-message").should("have.class", "show");
  });

  it("AC3 - saves selected levels and returns success confirmation", () => {
    cy.contains(".subject-name", "Databases").parent().within(() => {
      cy.get(".star").eq(4).click(); // 5 stars
    });

    cy.contains(".subject-name", "Operating Systems").parent().within(() => {
      cy.get(".star").eq(3).click(); // 4 stars
    });

    cy.contains("button", "Save Selections").click();
    cy.get(".success-message")
      .should("have.class", "show")
      .should("contain", "saved successfully");
  });

  it("AC4 - accepts each rating value from 1 to 5", () => {
    for (let stars = 1; stars <= 5; stars++) {
      cy.contains(".subject-name", "Mathematics").parent().within(() => {
        cy.get(".star").eq(stars - 1).click();
        cy.get(".rating-value").should("contain", stars.toString());
      });
    }
  });

  it("AC5 - saves 0 when no rating is selected", () => {
    cy.contains("button", "Reset").click();

    cy.contains(".subject-name", "Mathematics").parent().within(() => {
      cy.get(".rating-value").should("contain", "0");
    });

    cy.contains("button", "Save Selections").click();
    cy.get(".success-message").should("have.class", "show");
  });

  it("AC6 - saved ratings persist after page reload", () => {
    // Select 5 stars for Mathematics and 3 for Physics
    cy.contains(".subject-name", "Mathematics").parent().within(() => {
      cy.get(".star").eq(4).click();
      cy.get(".rating-value").should("contain", "5");
    });

    cy.contains(".subject-name", "Physics").parent().within(() => {
      cy.get(".star").eq(2).click();
      cy.get(".rating-value").should("contain", "3");
    });

    // Save selections
    cy.contains("button", "Save Selections").click();
    cy.get(".success-message").should("have.class", "show");

    // Reload page
    cy.reload();

    // Verify ratings persist from localStorage
    cy.contains(".subject-name", "Mathematics").parent().within(() => {
      cy.get(".rating-value").should("contain", "5");
    });

    cy.contains(".subject-name", "Physics").parent().within(() => {
      cy.get(".rating-value").should("contain", "3");
    });
  });

  it("AC7 - allows saving even when no subjects are rated", () => {
    cy.contains("button", "Reset").click();

    // All subjects have 0 rating
    cy.get(".rating-value").each(($el) => {
      cy.wrap($el).should("contain", "0");
    });

    // Should still allow save with all 0s
    cy.contains("button", "Save Selections").click();
    cy.get(".success-message").should("have.class", "show");
  });
});
