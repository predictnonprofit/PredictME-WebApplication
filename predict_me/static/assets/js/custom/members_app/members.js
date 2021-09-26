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

// add event listner to upgrade btns in account settings page
upgradeMembershipSettingsBtn.forEach(item => {
    const url = upgradeMembershipForm.action;
    item.addEventListener("click", event => {
        const clickedBtn = event.target;
        // console.log(newMembershipName);
        const newMembershipLbl = newMembershipName.replace("_", ' ').trim();
        // console.log(newMembershipLbl);
        Swal.fire({
            title: 'Are you sure',
            html: `Your membership will upgrade to <b>${toTitleCase(newMembershipLbl)}</b><br />, You won't be able to revert this!`,
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
                // disable the upgrade buttons
                upgradeMembershipSettingsBtn.forEach(btn => {
                    btn.disabled = true;
                    btn.classList.add("disabled", "progress-cursor");
                });
                // disable the membership radio buttons
                allUpgradeMembershipRadioBtns.forEach(btn => {
                    btn.disabled = true;
                    btn.classList.add("disabled", "progress-cursor");
                });
                const upgradeResponse = await requestUpgradeToNewMembership(newMembershipName, url);
                console.log(upgradeResponse);
                if (upgradeResponse['is_error'] === false) {
                    // Swal.fire('Upgraded!', 'Your membership upgraded successfully (testing)', 'success');
                    /* Swal.fire({
                        title: 'Congrats!',
                        text: upgradeResponse['msg'],
                        icon: 'success',
                        confirmButtonText: 'OK'
                    }).then((result) => {
                        if (result.isConfirmed) {
                            window.location.reload();
                        }
                    }) */
                    let timerInterval
                    Swal.fire({
                        title: 'Congrats!',
                        icon: "success",
                        // html: 'I will close in <b></b> milliseconds.',
                        text: upgradeResponse['msg'],
                        timer: 2000,
                        timerProgressBar: true,
                        allowOutsideClick: false,
                        allowEscapeKey: false,
                        allowEnterKey: false,
                        didOpen: () => {
                            Swal.showLoading()
                            // const b = Swal.getHtmlContainer().querySelector('b');
                            timerInterval = setInterval(() => {
                                // b.textContent = Swal.getTimerLeft();
                            }, 100);
                        },
                        willClose: () => {
                            clearInterval(timerInterval);
                        }
                    }).then((result) => {
                        /* Read more about handling dismissals below */
                        if (result.dismiss === Swal.DismissReason.timer) {
                            console.log('I was closed by the timer');
                            window.location.reload();
                        }
                    })
                } else {
                    Swal.fire('Error', 'There is an error in upgrade process!', 'error');
                }
            }
        });
    });
});