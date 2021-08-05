"use strict";

// this function will update the status of the crash report
function fetchChangeCrashReportStatus(status, crashObjId) {
    const url = `${webSiteUrl}/dashboard/crashes/api/change-report-status`;

    try {
        return fetch(url, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json;charset=utf-8",
                    "X-CSRFToken": getCookie('csrftoken')
                },
                body: JSON.stringify({
                    crashStatus: status,
                    crashID: parseInt(crashObjId),
                })
            })
            .then(response => {
                // check the response status
                if ((response.statusText === 'OK') && (response.status === 200)) {
                    return response.json();
                } else {
                    // retry when connection field
                    fetchChangeCrashReportStatus(status, crashObjId);
                }
            })
            .catch(error => {
                if (error instanceof TypeError) {
                    console.info('Error in connection!!, please wait...');
                } else {
                    console.error(error);
                }
            });
    } catch (error) {
        if (error instanceof TypeError) {
            console.info('Error in connection!!, please wait...');
        } else {
            console.error(error);
        }
    }

}