"use strict";
class Dom {
    constructor(name, type = "id") {
        
        // select by ID
        if (type === "id" || type === "#") {
            this.element = this.get_id(name);
        }
        
        // select by tagname
        if (type === "tag" || type === "t"  || type === "<>") {
            const tags = document.getElementsByTagName(name);
            this.construct_all(tags);
        }
        
        // select the first found in the document by CSS-selector:
        if (type === "selector" || type === "s") {
            this.element = document.querySelector(name);
        }
        
        // select all elements in the document by CSS-selector:
        if (type === "selectors" || type === "ss") {
            const tags = document.querySelectorAll(name);
            this.construct_all(tags);
        }
        
        // select the first element by classname:
        if (type === "class" || type === ".") {
            this.element = document.getElementsByClassName(name)[0];
        }
        
        // select all elements by classname:
        if (type === "classes" || type === "..") {
            const tags = document.getElementsByClassName(name);
            this.construct_all(tags);
        }

        // using in construct all method:
        if (type === "element") {
            this.element = name;
        }
    }

    static listeners = {
        "keyup": "add_keyup",
        "select": "add_select",
        "change": "add_change",
        "load": "add_load"
    };

    get_id(id) {
        return document.getElementById(id);
    }

    // return the element of instance:
    get get() {
        return this.element;
    }

    construct_all(tags) {
        this.elements = [];
        Array.from(tags).forEach(tag => {
            this.elements.push(new Dom(tag, "element"));
        });
    }

    // --------------------------- Events ---------------------------
    add_event(event, func) {
        this.element.addEventListener(event, func);
    }

    remove_event(event, func) {
        this.element.removeEventListener(event, func);
    }

    add_load(func) {
        this.add_event("load", func);
    }

    // add/remove click event to the element
    add_click(func) {
        this.add_event("click", func);
    }

    remove_click(func) {
        this.remove_event("click", func);
    }

    // add/remove keyup event to the element
    add_keyup(func) {
        this.add_event("keyup", func);
    }

    remove_keyup(func) {
        this.remove_event("keyup", func);
    }

    // add/remove select event to the element
    add_select(func) {
        this.add_event("select", func);
    }

    remove_select(func) {
        this.remove_event("select", func);
    }

    // add/remove change event to the element
    add_change(func) {
        this.add_event("change", func);
    }

    remove_change(func) {
        this.remove_event("change", func);
    }
    
    // add/remove mouseover event to the element
    add_over(func) {
        this.add_event("mouseover", func);
    }
    
    remove_over(func) {
        this.remove_event("mouseover", func);
    }

    // add/remove mouseout event to the element
    add_out(func) {
        this.add_event("mouseout", func);
    }
    
    remove_out(func) {
        this.remove_event("mouseout", func);
    }

    // add focus to the input tag
    add_focus() {
        this.element.focus();
    }
    
    remove_focus() {
        this.element.blur();
    }

    // --------------------------- add events for a collection of elements --------------------------- :
    all_add_change(func) {
        this.elements.forEach(element => {
            element.add_change(func);
        });
    }
    
    // --------------------------- MARKDOWN --------------------------- :
    // required to link: <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
    markdown(text, pre = "", callback = null) {
        if (callback) {
            text = callback();
        }
        this.element.innerHTML = marked(`${pre}${text}`);
    }
    
    // required to link: <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
    // from: Dom instance input element: this markdown value of input will be changed to HTML content
    // pre: insert before the content
    // type: the type of event what will fire the changing (default: keyup-event)
    // callback: functon will call to redeclare the content before changing (eg. to format date)
    markdown_event(from, pre = "", type = "keyup", callback = null) {
        const type_effect = () => {
            this.markdown(from.val, pre, callback);
        };
        // add event listener:
        from[Dom.listeners[type]](type_effect);
    }
    
    click() {
        this.element.click();
    }
    // --------------------------- Helper functions --------------------------- :
    // log the element to the console:
    log() {
        console.log(this.element);
    }

    logs() {
        console.log(this.elements);
    }

    serialize() {
        return Object.fromEntries(new FormData(this.element).entries());
    }

    // --------------------------- Attributes ---------------------------
    // get/set the attribute of the element:
    attr(name, value = null) {
        if (value !== null) {
            this.element[name] = value;
        }
        return this.element[name];
    }
    
    // --------------------------- HTML-attributes :
    get title() {
        return this.element.title;
    }

    set title(val) {
        this.element.title = val;
    }

    // --------------------------- input-attributes :
    // get element value:
    get val() {
        return this.element.value;
    }
    
    // set element value:
    set val(value) {
        this.element.value = value;
    }

    // get/set attribute min
    get min() {
        return this.element.min
    }

    set min(value) {
        this.element.min = value;
    }

    // get/set attribute max
    get max() {
        return this.element.max;
    }

    set max(value) {
        this.element.max = value;
    }

    // get/set attribute checked
    get checked() {
        return this.element.checked;
    }

    set checked(bool) {
        this.element.checked = bool;
    }

    // get/set disabled attribute
    get disabled() {
        return this.element.disabled;
    }

    set disabled(bool) {
        this.element.disabled = bool;
    }

    // --------------------------- img-attribute :
    // get/set attribute src
    get src() {
        return this.element.src;
    }
    
    set src(path) {
        this.element.src = path;
    }
    
    // get relative path:
    get relative_path() {
        return this.element.attributes.getNamedItem("src").nodeValue.replace("/", "");
    } 
    // --------------------------- data-attribute :
    get get_data() {
        return this.element.dataset;
    }
    
    set set_data(arr) {
        this.element.dataset[arr[0]] = arr[1];
    }
    
    //  --------------------------- HTML ---------------------------
    // get element's HTML
    get html() {
        return this.element.innerHTML;
    }
    
    // set element's HTML
    set html(html_txt) {
        this.element.innerHTML = html_txt;
    }
    
    get txt() {
        return this.element.innerText;
    }
    
    set txt(txt) {
        this.element.innerText = txt;
    }
    // --------------------------- collection methods :
    all(callback) {
        this.elements.forEach(elem => {
            callback(elem);
        });
    }
    
    //  --------------------------- Style ---------------------------
    get style() {
        return this.element.style;
    }
    
    // --------------------------- cursor property :
    get cursor() {
        return this.element.style.cursor;
    }

    set cursor(bool) {
        this.element.style.cursor = bool;
    }
}