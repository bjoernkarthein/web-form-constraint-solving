const { Router } = require("express");
const administration = require("../controllers/administration");

const app = Router();

app.get("/clean", administration.clean);

module.exports = app;
