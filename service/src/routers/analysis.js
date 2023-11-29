const { Router } = require("express");
const analysis = require("../controllers/analysis");

const app = Router();

app.post("/record", analysis.record);

module.exports = app;