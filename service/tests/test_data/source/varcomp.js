const input = document.getElementById("amount");
const value = input.value;
const otherValue = document.getElementById("other-amount").value;

if (value >= otherValue) {
  input.setCustomValidity("amount must be less than other amount");
}
