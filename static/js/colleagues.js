"use strict";

// ------------ filter table ------------ :
const cells = {
    "first_name": {
        input: document.getElementById("first_name"),
        filter: "",
        column: 0
    },
    "last_name": {
        input: document.getElementById("last_name"),
        filter: "",
        column: 1
    },
    "username": {
        input: document.getElementById("username"),
        filter: "",
        column: 2
    },
    "email": {
        input: document.getElementById("email"),
        filter: "",
        column: 3
    },
    "position": {
        input: document.getElementById("position"),
        filter: "",
        column: 4
    },
    
};

const table = document.getElementById("filterable_table");
const tr = table.getElementsByTagName("tr");

const filter_by = (id) => {
    // Declare variables
    cells[id].filter = cells[id].input.value.toUpperCase();
    console.log("event");
    
    for (let i = 0; i < tr.length; i++) {
        tr[i].style.display = "";
    }
    
    for (const value of Object.values(cells)) {
        if (value.filter) {
            // Loop through all table rows, and hide those who don't match the search query
            for (let i = 0; i < tr.length; i++) {
                const td = tr[i].getElementsByTagName("td")[value.column];
                if (td) {
                    const txtValue = td.textContent || td.innerText;
                    if (txtValue.toUpperCase().indexOf(value.filter) > -1) {
                        // tr[i].style.display = "";
                    } else {
                        tr[i].style.display = "none";
                    }
                }
            }
        }
    }
};
