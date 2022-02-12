[].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]')).map(trigger => new bootstrap.Tooltip(trigger));

const clickButton = id => document.getElementById(id).click();

function addUser() {
    clickButton("deleteUserReset");
    document.getElementById("deleteUserField").value = "";
    clickButton("addUserSubmit");
}

const displayUsername = [].slice.call(document.querySelectorAll('.display-username'));
let selectedUserID = null;
function selectAccount(userID, username, buttonID) {
    selectedUserID = userID;
    for (let i in displayUsername) {
        displayUsername[i].innerText = username;
    }
    clickButton(buttonID);
}

function viewUser(accountType, username, name, email, gender, profilePic) {
    if (accountType != "") {

    }
    console.log("hi");
    clickButton("viewUser");
}

function deleteUser() {
    clickButton("addUserReset");
    clickButton("deleteUserReset");
    document.getElementById("deleteUserField").value = selectedUserID;
    clickButton("deleteUserSubmit");
}
