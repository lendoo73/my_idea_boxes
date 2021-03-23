"use strict"
// create hover effect on CodeCademy logo:
const logo = new Dom("codecademy_logo");

const changeImg = event => {
    const src = event.target.src
    const pos = src.search("white");
    if (pos  === -1) {
        event.target.src = src.replace("beige", "white")
    } else {
        event.target.src = src.replace("white", "beige")
    }
};

// add onmouse-over/out event to the CodeCademy logo
logo.add_over(changeImg);
logo.add_out(changeImg);

const device = new Device();
if (device.width <= 576) {
    // Change menu to icon bars;
    const menus = new Dom("nav a", "ss");
    const company_logo = new Dom(".header_left a img", "s");
    
    // build relative path by counting sub directories:
    let subdir = window.location.pathname.split("/").length - 2;
    let path = "";
    while (subdir) {
        path += "../";
        subdir --;
    }
    
    // store logo src in session storage
    if (!(sessionStorage.getItem("logo_src"))) {
        sessionStorage.setItem("logo_src", company_logo.element ? company_logo.relative_path : "");
    }
    sessionStorage.setItem("logo_src", company_logo.element ? company_logo.relative_path : "");
    const icon_src = {
        "Home": "static/icons/home.png",
        "Sample": "static/icons/sample.png",
        "Companies": "static/icons/companies.png",
        "Colleague": "static/icons/colleague.png",
        "Login": "static/icons/login.png",
        "Main": "static/icons/main.png",
        "Company": sessionStorage.getItem("logo_src"),
        "Colleagues": "static/icons/update_colleague.png",
        "Privilegs": "static/icons/update_privilegs.svg",
        "Logout": "static/icons/logout.png"
    };
    const change_menu = menu => {
        if (menu.txt) menu.html = `<img 
            src="${path}${icon_src[menu.txt]}" 
            title="${menu.txt}"
        />`;
    };
    menus.all(change_menu);
}