"use strict";

const header = new Dom("header_container");
const content = new Dom("content_container");
const close_at = new Dom("close_at_container");

// convert database-stored idea box to markdown formatted content:
header.markdown(header.txt, "# ");
// required to send content to the data attribute, otherwise any linebreak will be omitted
content.markdown(content.get_data.description);

close_at.markdown(new CustomDate(close_at.txt).custom_date, "#### Closing time at: <br />");