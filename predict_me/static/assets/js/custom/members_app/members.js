$(function() {
	

    // download invoices btn
    const downloadInvoicesBtn = $("#downloadInvoicesBtn");
    downloadInvoicesBtn.on("click", (event) => {
        fetchMemberInvoices();
    });

    // download user transactions btn
    const downloadTransactionsBtn = $("#downloadTransactionsBtn");
    downloadTransactionsBtn.on("click", (event) => {
        fetchMemberTransactions();
    });


    // upgrade membership btn
    const upgradeMembershipBtn = $("#upgradeMembershipBtn");
    upgradeMembershipBtn.on("click", (event) => {
        upgradeMembershipBtn();
    });


    // send message btn
    const inboxSendMessageBtn = $(".inboxSendMessageBtn");
    inboxSendMessageBtn.on("click", (event) => {
        sendMessage();
    });

});