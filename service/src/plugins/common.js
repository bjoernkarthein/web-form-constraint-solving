const op_path = require("path");

function getLocation(path, filePath) {
  const location = path.node.loc;

  if (!location) {
    return {};
  }

  const start = {
    line: location.start.line,
    column: location.start.column,
    index: location.start.index,
  };

  const end = {
    line: location.end.line,
    column: location.end.column,
    index: location.end.index,
  };

  const pathElements = filePath.split("/");
  const fileName = pathElements[pathElements.length - 1];

  return {
    file: fileName,
    start: start,
    end: end,
  };
}

function buildTraceFunctionCall(path, state, action, args) {
  const file = toFilePath(state.filename);
  const location = JSON.stringify(getLocation(path, file));
  return `b0aed879_987c_461b_af34_c9c06fe3ed46(${action}, ${args}, ${location});`;
}

const toFilePath = (filePath) =>
  filePath.split(op_path.sep).join(op_path.posix.sep);

const toExpressionString = (expression) =>
  expression &&
  expression.length > 0 &&
  ((expression[0] == "'" && expression[expression.length - 1] == "'") ||
    (expression[0] == '"' && expression[expression.length - 1] == '"'))
    ? expression
    : JSON.stringify(expression);

module.exports = {
  buildTraceFunctionCall,
  getLocation,
  toExpressionString,
  toFilePath,
};
