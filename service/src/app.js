const express = require("express");
const cors = require("cors");
const bodyParser = require("body-parser");
const path = require("path");

const { logger } = require("./log");

const administrationController = require("./routers/administration");
const analysisController = require("./routers/analysis");
const instrumentationController = require("./routers/instrumentation");

const app = express();
const PORT = 4000;

app.use(
  cors({
    origin: "*",
  })
);

app.use("/static", express.static(path.join(__dirname, "../static")));

app.use(bodyParser.urlencoded({ extended: false }));
app.use(bodyParser.json());

// routers
app.use("/admin", administrationController);
app.use("/analysis", analysisController);
app.use("/instrumentation", instrumentationController);

app.get("/", (req, res) => {
  res.send(
    "Instrumentation server running. View the logs at /static/server-log.log"
  );
});

app.listen(PORT, () => {
  logger.info(`Instrumentation server started on port ${PORT}...`);
});
