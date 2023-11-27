function getLocation(path) {
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

  return JSON.stringify({
    start: start,
    end: end,
  });
}

module.exports = { getLocation };
