"use strict";

const speech_container = new Dom("speech_container", ".");
const avatar_img = new Dom(".avatar_card img", "s");          // to change avatar-image when the user choose 'incognito'
const default_path = avatar_img.element.attributes.src.value; // save the current user's avatar for later useing
const sign_container = new Dom("sign_container");             // to change name on the avatar card
const idea = new Dom("idea");                                 // select the textarea-field
const inputs = new Dom("[id^='sign-']", "selectors");         // select all radio inputs of signing
const button = new Dom(".edit_button button", "s");

const signing = () => {
    // change the sign to the choosen name:
    sign_container.txt = event.target.nextElementSibling.innerText;
    // toggle avatar when user select/unselect 'incognito'
    if (event.target.value === "incognito") {
        avatar_img.element.attributes.src.value = "/static/avatars/incognito-cut.svg";
    } else if (avatar_img.element.attributes.src.value !== default_path) {
        avatar_img.element.attributes.src.value = default_path;
    }
};


// display markdown in monitor when the page is loaded: (it is need in edit mode)
speech_container.markdown(idea.val);


// add type event to the textarea field to display real-time any change:
speech_container.markdown_event(idea);

// select first name radiofield by default:
//inputs.elements[2].checked = true;
// add change event to all sign-iputs:
inputs.all_add_change(signing);

// disable Edit button on the avatar card:
button.disabled = true;
button.cursor = "not-allowed";