$(function () {
    // delete session from sessions page
    const deleteSessionHistoryForm = $(".deleteSessionHistoryForm");
    deleteSessionHistoryForm.on("submit", (event) => {
        event.preventDefault();
        let msg;
        const form = $(event.currentTarget);
        const isAll = form.data('isAllForm');
        if (isAll === 1) {
            msg = "Do you want to delete all sessions?, You won't be able to revert this!";
        } else {
            msg = "You won't be able to revert this!";
        }
        Swal.fire({
            title: 'Are you sure?',
            text: msg,
            icon: 'warning',
            showCancelButton: true,
            confirmButtonColor: '#3085d6',
            cancelButtonColor: '#d33',
            confirmButtonText: 'Yes',
            allowOutsideClick: false,
            allowEscapeKey: false,
            allowEnterKey: false,
        }).then((result) => {
            if (result.isConfirmed) {
                event.currentTarget.submit();
            }
        });
    });

});