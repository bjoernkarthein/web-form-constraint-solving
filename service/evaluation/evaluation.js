const fs = require("fs");

const defaultStats = {
  time_instrumenting_ms: 0,
  time_analyzing_ms: 0,
  constraint_candidates: [],
  js_files_analyzed: [],
};
var stats = defaultStats;

function saveStat(name, value) {
  stats[name] = value;
}

function getStat(name) {
  return stats[name];
}

function getCurrentStats() {
  // fs.writeFileSync("../evaluation/service_stats.json", JSON.stringify(stats));
  const current = { ...stats };
  stats = defaultStats;
  return current;
}

module.exports = {
  getStat,
  saveStat,
  getCurrentStats,
};
