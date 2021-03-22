"use strict";

// convert all .speech dataset to formatted text:
const speeches = new Dom("speech", "..");
speeches.elements.forEach(speech => {
    speech.markdown(speech.get_data.idea);
});

// convert date to human readable format:
const date_to = date => {
    const created = new CustomDate(date.txt);
    const date_before = created.date_before("long");
    const past = date_before !== "now" ? " ago" : "";
    date.txt = date_before + past;
};

const dates = new Dom("date", "..");
dates.all(date_to);