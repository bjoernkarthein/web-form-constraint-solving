const value = document.getElementById("email-field").value;

const expr = new RegExp(/^.+@.+$/g);
expr.test(value);