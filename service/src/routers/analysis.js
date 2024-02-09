const { Router } = require("express");
const analysis = require("../controllers/analysis");

const app = Router();

app.post("/record", analysis.record);
app.post("/candidates", analysis.getConstraintCandidatesForTraces);

module.exports = app;
