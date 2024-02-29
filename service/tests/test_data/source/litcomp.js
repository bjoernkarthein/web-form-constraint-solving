const input = document.getElementById("amount");
const value = input.value;

if (value <= 0) {
  input.setCustomValidity("amount must be greater than 0");
}
