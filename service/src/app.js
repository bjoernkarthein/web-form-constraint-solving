const bodyParser = require("body-parser");
const cors = require("cors");
const express = require("express");
const path = require("path");

const { logger } = require("./log");

const administrationController = require("./routers/administration");
const analysisController = require("./routers/analysis");
const instrumentationController = require("./routers/instrumentation");

const app = express();
const API_PORT = 4000;

app.use(
  cors({
    origin: "*",
  })
);

app.use("/static", express.static(path.join(__dirname, "../static")));

app.use(bodyParser.urlencoded({ extended: false, limit: "50mb" }));
app.use(bodyParser.json({ limit: "500mb" }));

// routers
app.use("/admin", administrationController);
app.use("/analysis", analysisController);
app.use("/instrumentation", instrumentationController);

app.get("/", (req, res) => {
  res.send("Instrumentation server running...");
});

const server = app.listen(API_PORT, () => {
  logger.info(`Instrumentation server started on port ${API_PORT}`);
});

process.on("SIGTERM", shutDown);
process.on("SIGINT", shutDown);

let connections = [];

server.on("connection", (connection) => {
  connections.push(connection);
  connection.on(
    "close",
    () => (connections = connections.filter((curr) => curr !== connection))
  );
});

function shutDown() {
  logger.info("Received kill signal, shutting down gracefully");
  server.close(() => {
    logger.info("Closed out remaining connections");
    process.exit(0);
  });

  setTimeout(() => {
    logger.error(
      "Could not close connections in time, forcefully shutting down"
    );
    process.exit(1);
  }, 10000);

  connections.forEach((curr) => curr.end());
  setTimeout(() => connections.forEach((curr) => curr.destroy()), 5000);
}
