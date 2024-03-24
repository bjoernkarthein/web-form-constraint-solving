const { WebSocketServer } = require("ws");

const instrumentationService = require("../instrument");
const tracerService = require("../trace");
const { logger } = require("../log");
const constraintService = require("../constraints");
const codeqlService = require("../codeql");
const {
  writeStatsToFile,
  getCurrentStats,
} = require("../../evaluation/evaluation");

const WEBSOCKET_SERVER_PORT = 1337;
const wss = new WebSocketServer({ port: WEBSOCKET_SERVER_PORT });
const connections = [];

wss.on("connection", function connection(ws) {
  connections.push(ws);
  ws.send("Successfully subscribed to service notifications");
});

let clean = (req, res) => {
  constraintService.cleanUp();
  codeqlService.cleanUp();
  instrumentationService.cleanUp();
  tracerService.cleanUp();
  logger.info("Cleaned up all resources");
  res.send("Cleaned up all resources");
};

let getStats = (req, res) => {
  const stats = getCurrentStats();
  res.json(stats);
};

let log = (req, res) => {
  for (const connection of connections) {
    connection.send(JSON.stringify(req.body));
  }
  res.send("Notified subscribers");
};

module.exports = { clean, log, getStats };
