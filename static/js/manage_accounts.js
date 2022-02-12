[].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]')).map(trigger => new bootstrap.Tooltip(trigger));

const clickButton = id => document.getElementById(id).click();

const displayUsername = document.getElementsByClassName("display-username");
const formResetInputs = document.getElementsByClassName("reset-form");

let selectedUserID = null;

function selectAccount(userID, username, buttonId) {
  selectedUserID = userID;
  for (let i in displayUsername) {
    displayUsername[i].innerText = username;
  }
  clickButton(buttonId);
}

function deleteUser() {
  for (let i in formResetInputs) {
    formResetInputs[i].click();
  }
  document.getElementById("deleteUserField").value = selectedUserID;
  clickButton("deleteUserSubmit");
}
