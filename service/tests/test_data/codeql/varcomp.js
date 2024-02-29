const input = document.getElementById("amount");
const value = input.value;
const otherValue = document.getElementById("other-amount").value;

if (otherValue <= value) {
  input.setCustomValidity("amount must be less than other amount");
} else if (value <= 0) {
  input.setCustomValidity("amount must be greater than 0");
}
