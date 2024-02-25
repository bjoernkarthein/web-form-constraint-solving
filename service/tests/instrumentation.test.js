const router = require("../src/routers/instrumentation");
const bodyParser = require("body-parser");
const express = require("express");
const fs = require("fs");
const path = require("path");
const request = require("supertest");

const app = express();
app.use(bodyParser.json({ limit: "50mb" }));
app.use("/", router);

describe("Instrument files correctly", () => {
    test("instrument simple file", async() => {
        const name = "decl.js";
        const testFile = fs.readFileSync(path.join(__dirname, "test_data", "instrumentation", name), "utf-8");
        const data = {name: name, source: testFile};
        await request(app)
                .post("/instrument")
                .send(data)
                .set('Accept', 'application/json');
        
        const filePath = path.join(__dirname, "..", "instrumented", name);
        const fileContent = fs.readFileSync(filePath, "utf-8");

        expect(fileContent).toContain("sendLog('VARIABLE_DECLARATION'");
        expect(fileContent).toContain("sendLog('VARIABLE_ASSIGNMENT'");
    });

    test("instrument simple file", async() => {
        const name = "for.js";
        const testFile = fs.readFileSync(path.join(__dirname, "test_data", "instrumentation", name), "utf-8");
        const data = {name: name, source: testFile};
        await request(app)
                .post("/instrument")
                .send(data)
                .set('Accept', 'application/json');
        
        const filePath = path.join(__dirname, "..", "instrumented", name);
        const fileContent = fs.readFileSync(filePath, "utf-8");

        expect(fileContent).toContain("sendLog('VARIABLE_DECLARATION'");
    });
});