const expr = new RegExp(/^.*@.*$/g);
const email = document.getElementById("mail").value;

if (expr.test(email)) {
  console.log("valid mail");
}
