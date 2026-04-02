const BACKEND_URL = Cypress.env("BACKEND_URL") || "http://localhost:8000";
const SAVE_SUBJECT_RATINGS_URL = `${BACKEND_URL}/api/save-subject-ratings/`;

function saveSubjectRatings(rows) {
  return cy.request({
    method: "POST",
    url: SAVE_SUBJECT_RATINGS_URL,
    body: { rows },
    headers: {
      "Content-Type": "application/json",
    },
    failOnStatusCode: false,
  });
}

describe("SD-59 Subject Interest Levels", () => {
  it("AC1 - allows marking subject interest levels", () => {
    const rows = [
      { semester: 1, subject: "Mathematics", stars: 5 },
      { semester: 1, subject: "Physics", stars: 3 },
    ];

    saveSubjectRatings(rows).then((response) => {
      expect(response.status).to.eq(200);
      expect(response.body).to.have.property("count", 2);
    });
  });

  it("AC2 - allows changing selected interest level before saving", () => {
    const rows = [
      { semester: 2, subject: "Algorithms", stars: 2 },
    ];

    // User updates the selected level before pressing save.
    rows[0].stars = 4;

    saveSubjectRatings(rows).then((response) => {
      expect(response.status).to.eq(200);
      expect(response.body).to.have.property("count", 1);
    });
  });

  it("AC3 - saves selected levels and returns success confirmation", () => {
    const rows = [
      { semester: 3, subject: "Databases", stars: 5 },
      { semester: 3, subject: "Operating Systems", stars: 4 },
    ];

    saveSubjectRatings(rows).then((response) => {
      expect(response.status).to.eq(200);
      expect(response.body).to.have.property("count");
      expect(response.body.count).to.be.greaterThan(0);
    });
  });
});