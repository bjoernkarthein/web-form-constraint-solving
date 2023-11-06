const express = require("express");
const path = require("path");

const app = express();

const PORT = 3000;

app.use("/static", express.static(path.join(__dirname, "../static")));

app.get("/", (req, res) => {
  res.send("This server statically serves the UI. Go to /static/ui.html");
});

app.listen(PORT, () => {
  console.log(`UI started on port ${PORT}...`);
});
