"use strict";

const fill_login_form = (username) => {
    // store login details in session storage:
    sessionStorage.setItem("username", username);
    // redirect user to the login page:
    window.location.href = "/login";
};