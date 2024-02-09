function sendLog(action, args, file, location, pageFile) {
  var xhr = new XMLHttpRequest();
  xhr.open("POST", "http://localhost:4000/analysis/record", false); // make request synchronous to ensure that all traces arrive at the server before analysis starts
  xhr.setRequestHeader("Content-Type", "application/json");
  xhr.send(
    JSON.stringify({
      action,
      args,
      time: new Date().getTime(),
      file,
      location,
      pageFile,
    })
  );
}
