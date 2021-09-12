"use strict";
// global variables
const upgradeMembershipSettingsBtn = document.querySelectorAll(".upgradeMembershipSettingsBtn");
// download invoices btn
const downloadInvoicesBtn = document.querySelector("#downloadInvoicesBtn");
downloadInvoicesBtn.addEventListener("click", event => {
    fetchMemberInvoices();
});

// download user transactions btn
const downloadTransactionsBtn = document.querySelector("#downloadTransactionsBtn");
downloadTransactionsBtn.addEventListener('click', event => {
    fetchMemberTransactions();
});


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
        newMembershipName = `${membershipName}_${value}`;

        const upgradeBtn = document.querySelector(`#${btnDataId}`);
        upgradeBtn.removeAttribute("disabled");
        upgradeBtn.classList.remove('not-allowed-cursor', "disabled");
    });
});

// add event listner to upgrade btns in account settings page
upgradeMembershipSettingsBtn.forEach(item => {
    item.addEventListener("click", event => {
        const clickedBtn = event.target;
        const newMembershipLbl = newMembershipName.replace("_", ' ').trim();
        // console.log(newMembershipLbl);
        Swal.fire({
            title: 'Are you sure?',
            html: `Your membership will upgrade to <b>${newMembershipLbl}</b>, You won't be able to revert this!`,
            icon: 'question',
            // showDenyButton: true,
            showCancelButton: true,
            confirmButtonColor: '#3085d6',
            cancelButtonColor: '#d33',
            confirmButtonText: 'Yes, upgrade',
            allowOutsideClick: false,
            allowEscapeKey: false,
            allowEnterKey: false,
        }).then(async (result) => {
            if (result.isConfirmed) {
                const upgradeResponse = await requestUpgradeToNewMembership(newMembershipName);
                if(upgradeResponse['is_done']){
                    Swal.fire('Upgraded!', 'Your membership upgraded successfully (testing)', 'success');
                }
            }
        });
    });
});