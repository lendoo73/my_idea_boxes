"use strict";

// if the use clicked on a sample login details fill the login form:
if (document.referrer.indexOf("sample") > -1) {
    const user = new Dom("email_or_user_name");
    const password = new Dom("password");
    user.val = sessionStorage.getItem("username");
    password.val = "aaa";
    // simulate user click on 'Sign In' button:
    const submit = new Dom("submit");
    submit.click();
}