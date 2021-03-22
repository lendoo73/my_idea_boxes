"use strict";

const title = new Dom("name");
const description = new Dom("description");
const close_at = new Dom("close_at");
const header = new Dom("header_container");
const content = new Dom("content_container");
const close_at_container = new Dom("close_at_container");

// add min attribute to the close at input:
const today = new CustomDate();
today.add_day(1);
close_at.min = today.date.toISOString().split("T")[0];

const long_format = () => {
    const close = new CustomDate(close_at.val);
    return close.custom_date;
};

// display markdown in monitor when the page is loaded: (it is need in edit mode)
header.markdown(title.val, "# ");
content.markdown(description.val);
console.log(close_at.val);
if (close_at.val) {
    // only display if the user already choosed any date:
    close_at_container.markdown(close_at.val, "#### Closing time at: <br />", long_format);
}

// add type event to display real-time any change:
header.markdown_event(title, "# ");
content.markdown_event(description);
close_at_container.markdown_event(close_at, "#### Closing time at: <br />", "change", long_format);

/*

<div style="text-align: center;"><u>PBYL Grid Review</u></div>

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;As part of ongoing continuous improvement within XDC, we will be conducting colleague led listening groups about the PBYL grid.

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;All ideas considered, no matter how big/small, and feedback given.

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;All PBYL colleagues will be asked for their views during the review.

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;If you are interested in taking a more leading role in the review please make your DM or SM aware.

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;1<sup>st</sup> groups to be held W/C 31/01/21
*/
