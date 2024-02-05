function sendLog(action, args, file, location, pageFile) {
  var xhr = new XMLHttpRequest();
  xhr.open("POST", "http://localhost:4000/analysis/record", false); // Make this synchronous so that we ensure that the server is finished processing
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
