function swAlert(alertTitle, alertMsg, alertType) {
    swal.fire(`${alertTitle}`, `${alertMsg}`, `${alertType}`);
}

// function to grab member invoices
function fetchMemberInvoices() {
    const invoicesTable = $("#invoices-list-table");
    const startDate = $("#invoice-start-date");
    const endDate = $("#invoice-end-date");
    const invoicesListTableWrapper = $("#invoicesListTableWrapper");
    // check if the values are empty
    if ((startDate.val() === "") && (endDate.val() === "")) {
        // all invoices
        startDate.addClass("bg-danger-o-50");
        endDate.addClass("bg-danger-o-50");
    } else {
        // here validate start date and end date
        if (startDate.val() === '') {
            startDate.addClass("bg-danger-o-50");
        } else {
            startDate.removeClass("bg-danger-o-50");
        }
        if (endDate.val() === "") {
            endDate.addClass("bg-danger-o-50");
        } else {
            endDate.removeClass("bg-danger-o-50");
        }

        // if start date and end date are not empty
        if ((startDate.val() !== "") && (endDate.val() !== "")) {
            const fetchInvoicesRequest = fetchMemberInvoicesRequest(startDate.val(), endDate.val(), "invoices");
            $.when(fetchInvoicesRequest).done(function (data, textStatus, jqXHR) {
                if ((textStatus === "success") && (jqXHR.status === 200)) {
                    invoicesListTableWrapper.show();
                    $("#invoices-list-table > tbody").html("<tr></tr>");
                    const invoices = data['invoices'];
                    const invoicesCount = parseInt(data['invoices_count']);
                    for (const inv of invoices) {
                        $('#invoices-list-table tr:last').after(`
                            <tr>
                                <td> ${inv['customer']} </td>
                                <td> <b>$${parseFloat(inv['amount_due'])}</b> </td>
                                <td> <b>$${parseFloat(inv['amount_paid'])}</b> </td>
                                <td> <b>$${parseFloat(inv['amount_remaining'])}</b> </td>
                                <td>${inv['status']}</td>
                                <td> 
                                <a href="${inv['invoice_pdf']}" target="_blank"> Invoice PDF File </a>
                                </td>
                            </tr>
                        `);
                    }

                } else {
                    swAlert("Error", data, 'error');
                }
            });
        }
    }

}
// function to grab member transactions
function fetchMemberTransactions() {
    const invoicesTable = $("#invoices-list-table");
    const startDate = $("#trans-start-date");
    const endDate = $("#trans-end-date");
    const transactionsListTableWrapper = $("#transactionsListTableWrapper");
    // check if the values are empty
    if ((startDate.val() === "") && (endDate.val() === "")) {
        // all trans
        startDate.addClass("bg-danger-o-50");
        endDate.addClass("bg-danger-o-50");
    } else {
        // here validate start date and end date
        if (startDate.val() === '') {
            startDate.addClass("bg-danger-o-50");
        } else {
            startDate.removeClass("bg-danger-o-50");
        }
        if (endDate.val() === "") {
            endDate.addClass("bg-danger-o-50");
        } else {
            endDate.removeClass("bg-danger-o-50");
        }

        // if start date and end date are not empty
        if ((startDate.val() !== "") && (endDate.val() !== "")) {
            const fetchInvoicesRequest = fetchMemberInvoicesRequest(startDate.val(), endDate.val(), "trans");
            $.when(fetchInvoicesRequest).done(function (data, textStatus, jqXHR) {
                if ((textStatus === "success") && (jqXHR.status === 200)) {
                    transactionsListTableWrapper.show();
                    $("#transactions-list-table > tbody").html("<tr></tr>");
                    const trans = data['trans'];
                    const transCount = parseInt(data['trans_count']);

                    for (const tran of trans) {
                        $('#transactions-list-table tr:last').after(`
                            <tr>
                                <td> ${tran['created']} </td>
                                <td> ${tran['customer']} </td>
                                <td> <b>$${tran['amount']}</b> </td>
                                <td> ${tran['card']} </td>
                                <td> 
                                <a href="${tran['receipt_url']}" target="_blank"> Receipt URL </a>
                                </td>
                                <td> 
                                ${tran['paid'] == true ? "Yes" : "No"}
                                </td>
                            </tr>
                        `);
                    }

                } else {
                    swAlert("Error", data, 'error');
                }
            });
        }
    }

}


// upgrade membership function
function upgradeMembershipBtn() {
    alert('upgrade membership');
}


// send message funtion
function sendMessage() {
    const receiverEmails = $("#receiverEmails");
    const composeSubject = $("#composeSubject");
    const messageContent = $(".ql-editor");
    /* console.log(receiverEmails.val());
    console.log(composeSubject.val());
    console.log(messageContent.html());
    alert("Send the message"); */
}