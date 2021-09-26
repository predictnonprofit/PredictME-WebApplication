"use strict";

const addOrRemoveCssClassForNodeList = (nodeList, cssClassList, addOrRemove = "add") => {
    nodeList.forEach(item => {
        // check if add or remove class
        if (addOrRemove === 'add') {
            item.classList.add(...cssClassList);
            // item.setAttribute('disabled', "disabled");
            item.disabled = true;
        } else {
            item.classList.remove(...cssClassList);
            item.disabled = false;
        }
    });
};


const emptyValuesNodelist = nodeList => {
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
        z_index: 1031,
        timer: 1500,
    });
};


// convert string to title case
const toTitleCase = (str) => {
  return str.replace(
    /\w\S*/g,
    function(txt) {
      return txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase();
    }
  );
}
