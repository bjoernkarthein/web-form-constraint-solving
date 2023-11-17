const express = require("express");
const cors = require("cors");
const bodyParser = require("body-parser");
const path = require("path");

const instrumentation = require("./instrument");
const tracer = require("./trace");

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

app.post("/instrument", (req, res) => {
  const name = req.body.name;
  const content = req.body.source;

  instrumentation.saveFile(name, content);
  instrumentation.runCommand(instrumentation.getBabelCommand(name)).then(() => {
    const fileName = `${instrumentation.instrumentedDir}${name}`;
    console.log(`instrumented file ${name}`);
    res.sendFile(fileName, { root: __dirname });
  });
});

app.post("/record", (req, res) => {
  tracer.addToTraceLog(req);
  res.sendFile(tracer.traceLogFile, { root: __dirname });
  // handleEvent(action, args, time, file, location, pageFile);
});

app.listen(PORT, () => {
  console.log(`Instrumentation server started on port ${PORT}...`);
});
