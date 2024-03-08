let c989a310_3606_4512_bee4_2bc00a61e8ac = false;

function b0aed879_987c_461b_af34_c9c06fe3ed46(
  action,
  args,
  file,
  location,
  pageFile
) {
  if (!c989a310_3606_4512_bee4_2bc00a61e8ac) {
    return;
  }
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
