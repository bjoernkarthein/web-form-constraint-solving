/** @type {import('jest').Config} */
const config = {
  transform: {},
};

module.exports = config;

process.env = Object.assign(process.env, {
  CODEQL_PATH: "codeql"
});