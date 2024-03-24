const { Router } = require("express");
const administration = require("../controllers/administration");

const app = Router();

app.get("/clean", administration.clean);
app.get("/getStats", administration.getStats);
app.post("/log", administration.log);

module.exports = app;
