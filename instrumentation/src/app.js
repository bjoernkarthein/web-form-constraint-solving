const express = require("express");
const cors = require("cors");
const bodyParser = require("body-parser");
const fs = require("fs");
const exec = require("child_process");
const path = require("path");

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

app.get("/", (req, res) => {
  res.send(
    "Instrumentation server. Send request to '/instrument' to instrument a .js file"
  );
});

app.listen(PORT, () => {
  console.log(`Instrumentation server started on port ${PORT}...`);
});

function runCommand(cmd) {
  return new Promise((resolve, reject) => {
    exec(cmd, (error) => {
      if (error) {
        reject();
        return;
      }
      resolve();
    });
  });
}
