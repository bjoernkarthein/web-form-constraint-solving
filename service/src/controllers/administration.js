const { WebSocketServer } = require("ws");

const instrumentationService = require("../instrument");
const tracerService = require("../trace");
const { logger } = require("../log");
const constraintService = require("../constraints");
const codeqlService = require("../codeql");

const WEBSOCKET_SERVER_PORT = 1337;
const wss = new WebSocketServer({ port: WEBSOCKET_SERVER_PORT });
const connections = [];

wss.on("connection", function connection(ws) {
  connections.push(ws);
  ws.send("Now listening for server messages...");
});

let clean = (req, res) => {
  constraintService.cleanUp();
  codeqlService.cleanUp();
  instrumentationService.cleanUp();
  tracerService.cleanUp();
  logger.info("Cleaned up all resources");
  res.send("Cleaned up all resources");
};

let log = (req, res) => {
  for (const connection of connections) {
    connection.send(req.body);
  }
};

module.exports = { clean, log };
