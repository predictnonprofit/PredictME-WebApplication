"use strict";


const checkIfUndefined = value => {
    if ((typeof value === "undefined") || (typeof value === undefined)) {
        return true;
    } else {
        return false;
    }
}

const addOrRemoveCssClassForNodeList = (nodeList, cssClassList, addOrRemove = "add") => {
    nodeList.forEach(item => {
        // check if add or remove class
        if (addOrRemove === 'add') {
            item.classList.add(...cssClassList);
            item.disabled = true;
        } else {
            item.classList.remove(...cssClassList);
            item.disabled = false;
        }
    });
};


const enableOrDisableNodeList = (nodeList, enableOrDisable, additionCssClassesArray) => {
    try {
        nodeList.forEach(item => {

            // check if enable or disable
            if (enableOrDisable === "enable") {
                
                // check if any extra css classes provided
                if (Array.isArray(additionCssClassesArray) === true) {
                    item.classList.remove(...additionCssClassesArray);
                }
                // enable the input
                item.disabled = false;

            } else {
                // check if any extra css classes provided
                if (Array.isArray(additionCssClassesArray) === true) {
                    item.classList.add(...additionCssClassesArray);
                }
                // disable the input
                item.disabled = true;
            }

        });

    } catch (error) {
        console.error(error);
    }

};

const emptyValuesNodeList = nodeList => {
    nodeList.forEach(item => {
        item.value = '';
    });
};


const displayTopNotification = (msgBody, msgType) => {
    let animateClasses, icon = '';
    if (msgType === 'danger') {
        animateClasses = {
            enter: 'animate__animated animate__tada',
            exit: 'animate__animated animate__bounceOutRight'
        };
        icon = "icon la la-warning";
    } else if (msgType === 'success') {
        animateClasses = {
            enter: 'animate__animated animate__ animate__faster animate__slideInRight',
            exit: 'animate__animated animate__ animate__faster animate__slideOutRight'
        };
        icon = "icon la la-check";
    }
    $.notify({
        // options
        message: msgBody,
        icon: icon,
    }, {
        // settings
        type: msgType,
        allow_dismiss: false,
        animate: animateClasses,
        z_index: 2000,
        timer: 1000,
        showProgressbar: true
    });
};


// convert string to title case
const toTitleCase = (str) => {
    return str.replace(
        /\w\S*/g,
        function (txt) {
            return txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase();
        }
    );
}


// sessionStorage helpers

// create new sessionStorage
const createSessionStorage = (name, value, isDebugging = false) => {
    if (isDebugging === true)
        console.warn(`The item ${name} set with value ${value}`);

    window.sessionStorage.setItem(name, value);
};

// check if item exists in sessionStorage
const checkSessionStorage = (name, isDebugging = false) => {
    if (isDebugging === true)
        console.warn(`Check item ${name} if exists`);

    const item = window.sessionStorage.getItem(name);
    if (item !== null) {
        return true;
    } else {
        return false;
    }

};

// delete sessionStorage
const deleteSessionStorage = (name, isAll = false, isDebugging = false) => {
    if (isDebugging === true)
        console.warn(`Deleting ${name} from sessionStorage...`);

    if (isDebugging && isAll)
        console.warn(`Deleting all sessionStorage...`);

    if (checkSessionStorage(name) === true) {
        window.sessionStorage.removeItem(name);
    }

    // delete all items
    if (isAll) {
        window.sessionStorage.clear();
    }

};


// get sessionStorage value
const getSessionStorage = (name, isDebugging = false) => {
    if (isDebugging === true)
        console.warn(`Get ${name} from sessionStorage`);

    if (checkSessionStorage(name) === true) {
        return window.sessionStorage.getItem(name).trim();
    } else {
        return null;
    }
};