"use strict";

// change Closing:
const dates = new Dom(".box_container .close", "ss"); // select all Closing cells
const change_closing = element => {
    const close_at = new CustomDate(element.get_data.close_at);
    // add + 1 day for closing time to calculate with the last day
    element.title = `Closing time at: ${close_at.custom_date}`;
    close_at.add_day(1);
    const date_more = close_at.date_more();
    const now = new CustomDate();
    if (close_at.date < now.date) {
        // This Idea Box already closed:
        element.html = "&times;";
        element.style.color = "red";
        element.style.fontWeight = 900;
        element.style.fontSize = "35px";
        element.title = `Closed at: ${close_at.custom_date}`;
    } else element.txt = date_more;
};

dates.all(change_closing);

// change Activity:
const activities = new Dom(".box_container .activity", "ss"); // select all Activity cells
const change_activity = element => {
    const last_activity = element.get_data.activity;
    if (last_activity !== "None") {
        const activity = new CustomDate(last_activity);
        const date_before = activity.date_before();
        element.txt = date_before;
        const past = date_before !== "now" ? " ago" : "";
        element.title = `Last activity ${activity.date_before("l")} ${past}.`;
    } else element.title = `Nobody has a unique Idea?`;
};

activities.all(change_activity);
