const getElement = id => document.getElementById(id);
const clickButton = id => getElement(id).click();

function addUser() {
    clickButton("deleteUserReset");
    getElement("deleteUserField").value = "";
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
        getElement("viewUserUserType").innerText = accountType;
    }
    getElement("viewUserUsername").innerText = username;
    getElement("viewUserName").innerText = name;
    getElement("viewUserEmail").innerText = email;
    getElement("viewUserGender").innerText = {"M":"Male", "F":"Female", "O":"Others", "-":"-"}[gender];
    getElement("viewUserProfilePic").src = profilePic;
    clickButton("viewUserButton");
}

function deleteUser() {
    clickButton("addUserReset");
    clickButton("deleteUserReset");
    getElement("deleteUserField").value = selectedUserID;
    clickButton("deleteUserSubmit");
}
