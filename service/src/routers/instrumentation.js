const { Router } = require("express");
const instrumentation = require("../controllers/instrumentation");

const app = Router();

app.post("/instrument", instrumentation.instrument);

module.exports = app;
