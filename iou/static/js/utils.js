function domCreate(config, exported) {
    let el = document.createElement(config.el || "div");
    for (let key in config) {
        let val = config[key];
        switch (key) {
            case "el":
                break;
            case "text":
                el.textContent = val;
                break;
            case "html":
                el.innerHTML = val;
                break;
            case "_exported":
                exported[val] = el;
                break;
            case "child":
            case "children":
                if (!Array.isArray(val)) {
                    val = [val];
                }
                for (let ch of val) {
                    if (typeof ch == "string") {
                        el.appendChild(document.createTextNode(ch));
                    } else if (ch instanceof HTMLElement){
                        el.appendChild(ch);
                    } else {
                        el.appendChild(domCreate(ch, exported));
                    }
                }
                break;
            default:
                if (key.substr(0, 2) == "on" && typeof val === "function") {
                    el.addEventListener(key.substr(2), val);
                } else if (val != null) {
                    el.setAttribute(key, val);
                }
        }
    }
    return el;
}

function formData(form) {
    let ret = {};
    for (let e of form.elements) {
        if (e.hasAttribute("name")) {
            ret[e.name] = e.value;
        }
    }
    return ret;
}
