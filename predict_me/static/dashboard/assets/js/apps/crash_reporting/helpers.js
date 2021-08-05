"use strict";


// this function will run when admin change the status of crash
async function changeReportStatus() {
    try {
        const crashStatusSelect = $('#crashStatusSelect');
        const crashReportID = $('#crashReportID');
        const crashStatusRequest = await fetchChangeCrashReportStatus(crashStatusSelect.val(), crashReportID.val());
        // check the status code, or the connection is successfully
        if (crashStatusRequest.status === 200) {
            await Swal.fire(
                'Success',
                'The status changed successfully!',
                'success'
            );
            location.href = location.href;

        } else {
            // this else if there error in the connection
            console.error('Error when change report crash status!!');
            console.error(crashStatusRequest.status);
        }
    } catch (error) {
        if (error instanceof TypeError) {
            console.error('Error in connection!!, please wait...');
        } else {
            console.error(error);
        }
    }



}