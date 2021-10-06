"use strict";
$(function () {

    const newCreditCardElementParentWrapper = document.querySelector("#new-credit-card-element-parent-wrpper");


    // check if the card element exists on the page
    if (newCreditCardElementParentWrapper !== null) {
        const newCreditCardElementWrapper = document.querySelector("#new-credit-card-element-wrapper");
        const newCreditCardFormErrors = document.querySelector("#new-credit-card-form-errors");
        const creditCardElement = document.querySelector("#new-credit-card-element");
        const useLastCreditCardInput = document.querySelector("input[name='use_last_credit_card_input']");
        const submitBtn = document.querySelector("#new-credit-card-submit-btn");
        // Custom styling can be passed to options when creating an Element.
        // (Note that this demo uses a wider set of styles than the guide below.)
        const style = {
            base: {
                color: '#32325d',
                fontFamily: '"Helvetica Neue", Helvetica, sans-serif',
                fontSmoothing: 'antialiased',
                fontSize: '16px',
                '::placeholder': {
                    color: '#aab7c4'
                }
            },
            invalid: {
                color: '#fa755a',
                iconColor: '#fa755a'
            }
        };
        const cardOptions = {
            style: style,
            hidePostalCode: true,
            // disabled: true
        };


        // Create a Stripe client.
        const stripe = Stripe('pk_test_g5z1xvZJJ04QG9uzwR9u0Df600SMC4ANGr', {
            locale: 'en'
        });

        // Create an instance of Elements.
        const elements = stripe.elements();



        // Create an instance of the card Element.
        let card = elements.create('card', cardOptions);

        // Add an instance of the card Element into the `card-element` <div>.
        card.mount('#new-credit-card-element');

        // Handle real-time validation errors from the card Element.
        card.addEventListener('change', function (event) {
            const displayError = document.querySelector('#new-credit-card-form-errors');
            if (event.error) {
                displayError.textContent = event.error.message;
            } else {
                displayError.textContent = '';
            }
        });


        // Submit the form with the token ID.
        const stripeTokenHandler = async (token) => {
            const newMembershipSlug = getSessionStorage("newSubMembership").replace(" ", "_");
            const form = document.querySelector('#new-credit-card-form');

            // check if there is token passed
            if (typeof token !== "undefined") {
                const hiddenInput = document.createElement('input');
                hiddenInput.setAttribute('type', 'hidden');
                hiddenInput.setAttribute('name', 'stripeToken');
                hiddenInput.setAttribute('value', token.id);
                form.appendChild(hiddenInput);
            }

            const slugHiddenInput = document.createElement("input");
            slugHiddenInput.setAttribute("type", 'hidden');
            slugHiddenInput.setAttribute("name", "membership_slug");
            slugHiddenInput.setAttribute("value", newMembershipSlug);
            form.appendChild(slugHiddenInput);

            // send the request to backend
            const upgradeResponse = await requestUpgradeToNewMembership({
                "token": token,
                "membership_slug": newMembershipSlug,
                // "membership_slug": 'expert_monthlyy',
                "use_last_credit_card_input": document.querySelector("input[name='use_last_credit_card_input']").value
            }, form.action);
            // check if there an errors
            if (upgradeResponse['is_error'] === false) {
                let timerInterval
                Swal.fire({
                    title: 'Congrats!',
                    icon: "success",
                    // html: 'I will close in <b></b> milliseconds.',
                    text: upgradeResponse['msg'],
                    timer: 3000,
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
                Swal.fire('Error', upgradeResponse['msg'], 'error');
            }

            // Submit the form
            // form.submit();
        };


        const form = document.querySelector('#new-credit-card-form');
        form.addEventListener('submit', function (event) {
            event.preventDefault();
            const cardElement = elements.getElement("card");


            // check cardElement is null mean the stripe form hidden or destroyed
            if (cardElement !== null) {
                stripe.createToken(card).then((result) => {
                    if (result.error) {
                        // Inform the user if there was an error.
                        const errorElement = document.querySelector('#new-credit-card-form-errors');
                        errorElement.textContent = result.error.message;
                    } else {
                        // disable the submit button
                        submitBtn.classList.add("disabled", "wait-cursor");
                        submitBtn.disabled = true;
                        // Send the token to your server.
                        stripeTokenHandler(result.token);


                    }
                });
            } else {
                // disable the submit button
                submitBtn.classList.add("disabled", "wait-cursor");
                submitBtn.disabled = true;
                stripeTokenHandler();
            }

        });


        // add event listener to checkbox
        useLastCreditCardInput.addEventListener("change", event => {
            const isChecked = event.currentTarget.checked;
            let detachedElement = newCreditCardElementParentWrapper;

            if (isChecked === true) {
                event.currentTarget.value = 1;
                // console.log('Detach');
                newCreditCardElementWrapper.classList.add("d-none");
                card.destroy();
            } else {
                event.currentTarget.value = '';
                // console.log('Attach');
                newCreditCardElementWrapper.classList.remove("d-none");
                newCreditCardFormErrors.textContent = "";
                card = elements.create('card', cardOptions);
                card.mount('#new-credit-card-element');

            }
        });


        // modal events
        $('#newCreditCardFormModal').on('show.bs.modal', event => {
            // first check if new membership is saved in sessionStorage
            if(checkSessionStorage('newSubMembership')){
                const getNewMembership = getSessionStorage("newSubMembership").split(" ");
                const newMembershipTextHolder = document.querySelector("#new-membership-text-holder");
                const newMembershipCycleHolder = document.querySelector("#new-membership-cycle-holder");
                newMembershipTextHolder.textContent = toTitleCase(getNewMembership[0]);
                newMembershipCycleHolder.textContent = toTitleCase(getNewMembership[1]);
            }else{
                displayTopNotification("You should select new membership first!", "danger");
                event.preventDefault();
            }
            
        });

        $('#newCreditCardFormModal').on('hide.bs.modal', event => {
            document.querySelector("#new-membership-text-holder").textContent = "";
            document.querySelector("#new-membership-cycle-holder").textContent = "";
            deleteSessionStorage("newSubMembership");
        });

    }

});