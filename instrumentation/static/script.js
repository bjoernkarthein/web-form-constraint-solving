function sendLog(action, args, time, file, location, pageFile) {
  var xhr = new XMLHttpRequest();
  xhr.open("POST", "http://localhost:4000/record", true);
  xhr.setRequestHeader("Content-Type", "application/json");
  xhr.send(
    JSON.stringify({
      action,
      args,
      time,
      file,
      location,
      pageFile,
    })
  );
}
