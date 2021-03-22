"use strict";
class Device {
    constructor() {
        this.width = (window.innerWidth > 0) ? window.innerWidth : screen.width;
    }
}