"use strict";

class CustomDate {
    constructor(date = null) {
        this.date = date === null ? new Date() : new Date(date) ;
    } 

    static months = {
        0: 'January',
        1: 'February',
        2: 'March',
        3: 'April',
        4: 'May',
        5: 'June',
        6: 'July',
        7: 'August',
        8: 'September',
        9: 'October',
        10: 'November',
        11: 'December'
    };

    static days = {
        "0": 'Sunday',
        "1": 'Monday',
        "2": 'Tuesday',
        "3": 'Wednesday',
        "4": 'Thurstday',
        "5": 'Friday',
        "6": 'Saturday'
    };

    // return the timestamp:
    get timestamp() {
        return this.date.getTime();
    }

    get year() {
        return this.date.getFullYear();
    }

    get month() {
        return this.date.getMonth();
    }

    // return month name in long format
    get Month() {
        return CustomDate.months[this.month];
    }
    
    // return the day of the month
    get day() {
        return this.date.getDate();
    }
    
    get weekday() {
        return this.date.getDay();
    }
    
    // return name of the day in long format
    get Day() {
        return CustomDate.days[this.weekday];
    }

    get custom_date() {
        return `${this.Day}, ${this.day}. ${this.Month} ${this.year}.`
    }

    add_day(day) {
        this.date = new Date(this.date.setDate(this.date.getDate() + day));
    }

    // log the element to the console:
    log() {
        console.log(this);
    }

    date_before(format = "short") {
        if (format === "l") format = "long";
        const timestamp = this.timestamp / 1000;
        const now = Math.round(Date.now() / 1000);
        const min = 60;
        const hour = min * 60;
        const day = hour * 24;
        const week = day * 7;
        const month = day * 30;
        const year = month * 12;

        const result = {
            short: {
                Y: "Y",
                M: "M",
                W: "W",
                D: "D",
                h: "h",
                m: "m"
            },
            long: {
                Y: " year",
                M: " month",
                W: " week",
                D: " day",
                h: " hour",
                m: " minute"
            }
        };

        const get_post = (date, synbol) => {
            let post = result[format][synbol];
            if (format === "long") {
                post += date > 1 ? "s" : "";
            }
            return post;
        };

        if (now - timestamp - year > 0) {
            const years = Math.round((now - timestamp - year) / year) || 1;
            return `${years}${get_post(years, "Y")}`;
        }

        if (now - timestamp - month > 0) {
            const months = Math.round((now - timestamp - month) / month) || 1;
            return `${months}${get_post(months, "M")}`;
        }
        if (now - timestamp - week > 0) {
            const weeks = Math.round((now - timestamp - week) / week) || 1;
            return `${weeks}${get_post(weeks, "W")}`;
        }
        if (now - timestamp - day > 0) {
            const days = Math.round((now - timestamp - day) / day) || 1;
            return `${days}${get_post(days, "D")}`;
        }
        if (now - timestamp - hour > 0) {
            const hours = Math.round((now - timestamp - hour) / hour) || 1;
            return `${hours}${get_post(hours, "h")}`;
        }
        if (now - timestamp - min > 0) {
            const mins = Math.round((now - timestamp - min) / min) || 1;
            return `${mins}${get_post(mins, "m")}`;
        }
        return "now";
    }

    date_more(format = "short") {
        const later = this.timestamp;
        const now = Math.round(Date.now());
        const substract = new CustomDate(now - (later - now));
        
        return substract.date_before(format);
    }
}