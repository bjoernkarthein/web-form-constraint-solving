const { Router } = require("express");
const administration = require("../controllers/administration");

const app = Router();

app.get("/clean", administration.clean);
app.post("/log", administration.log);

module.exports = app;
