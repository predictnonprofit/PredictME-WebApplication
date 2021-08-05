"use strict";
$(function () {
    const changeReportStatusBtn = $('#changeReportStatusBtn');
    changeReportStatusBtn.on('click', (event) => {
        changeReportStatus();
    });
});