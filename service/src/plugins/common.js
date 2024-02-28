const op_path = require("path");

function getLocation(path, filePath) {
  const location = path.node.loc;

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

  return JSON.stringify({
    file: fileName,
    start: start,
    end: end,
  });
}

const toFilePath = (filePath) =>
  filePath.split(op_path.sep).join(op_path.posix.sep);

const toExpressionString = (expression) =>
  expression.length > 0 &&
  ((expression[0] == "'" && expression[expression.length - 1] == "'") ||
    (expression[0] == '"' && expression[expression.length - 1] == '"'))
    ? expression
    : JSON.stringify(expression);

module.exports = { getLocation, toExpressionString, toFilePath };
