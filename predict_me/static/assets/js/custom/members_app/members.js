"use strict";
// global variables
const upgradeMembershipSettingsBtn = document.querySelectorAll(".upgradeMembershipSettingsBtn");
const upgradeMembershipForm = document.querySelector("#upgrade-membership-form");
if (upgradeMembershipForm !== null)
    upgradeMembershipForm.addEventListener("submit", e => e.preventDefault());


// download invoices btn
const downloadInvoicesBtn = document.querySelector("#downloadInvoicesBtn");
if (downloadInvoicesBtn !== null) {
    downloadInvoicesBtn.addEventListener("click", event => {
        fetchMemberInvoices();
    });
}

// download user transactions btn
const downloadTransactionsBtn = document.querySelector("#downloadTransactionsBtn");
if (downloadTransactionsBtn !== null) {
    downloadTransactionsBtn.addEventListener('click', event => {
        fetchMemberTransactions();
    });
}


// upgrade membership btn
const upgradeMembershipButton = document.querySelector("#upgradeMembershipBtn");
if (upgradeMembershipButton != null) {
    upgradeMembershipButton.addEventListener('click', event => {
        upgradeMembershipBtn();
    });
}



// send message btn
const inboxSendMessageBtn = $(".inboxSendMessageBtn");
inboxSendMessageBtn.on("click", (event) => {
    sendMessage();
});

// this var to save the changed new membership with cycle
let newMembershipName = '';
// enable upgrade buttons in account settings table
const allUpgradeMembershipRadioBtns = document.querySelectorAll("input[name='upgrade_membership_radio_btn']");
allUpgradeMembershipRadioBtns.forEach(element => {
    element.addEventListener("change", event => {
        // forEach to disable the input to make it like toggle
        upgradeMembershipSettingsBtn.forEach(item => {
            const disabledClasses = ["not-allowed-cursor", "disabled"];
            item.classList.add(...disabledClasses);
        });
        const input = event.target;
        const btnDataId = input.dataset['btnId'];
        const membershipName = input.dataset['membershipName'];
        const value = input.value;
        // newMembershipName = `${membershipName}_${value}`;
        newMembershipName = value;

        const upgradeBtn = document.querySelector(`#${btnDataId}`);
        upgradeBtn.removeAttribute("disabled");
        upgradeBtn.classList.remove('not-allowed-cursor', "disabled");
    });
});

// add event listener to upgrade btns in account settings page
upgradeMembershipSettingsBtn.forEach(item => {
    const url = upgradeMembershipForm.action;
    item.addEventListener("click", event => {
        const clickedBtn = event.target;
        // console.log(newMembershipName);
        const newMembershipLbl = newMembershipName.replace("_", ' ').trim();
        // console.log(newMembershipLbl);
        createSessionStorage("newSubMembership", newMembershipLbl, true);
        $("#newCreditCardFormModal").modal("show");
        $("#newCreditCardFormModal").modal("handleUpdate");

    });
});

/* setTimeout(() => {
    $("#newCreditCardFormModal").modal("show");
    $("#newCreditCardFormModal").modal("handleUpdate");
}, 2000); */