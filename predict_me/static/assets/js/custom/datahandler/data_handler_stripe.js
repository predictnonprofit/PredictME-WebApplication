"use strict";
const dhUpgradeMembershipTableForm = document.querySelector("#dh-upgrade-membership-table-form");
const dhBillingCycleInputs = document.querySelectorAll("[name='dh_upgrade_to_new_membership']");
const oldStripeCardCheckbox = document.querySelector("#oldStripeCardCheckbox");
const runStripeChargeBtn = document.querySelector("#runStripeChargeBtn");
const dhExtraRecordsAllInputs = document.querySelectorAll(".data-handler-extra-records-form-input");

dhBillingCycleInputs.forEach(item => {
  item.addEventListener("blur", event => {
    const currentElement = event.currentTarget;
    const priceElement = currentElement.dataset['priceId'];
    const priceElementNode = document.querySelector(`#${priceElement}`);
    const placeholder = priceElementNode.querySelector("b.price-placeholder");
    const monthly = priceElementNode.querySelector("b.price-monthly");
    const yearly = priceElementNode.querySelector("b.price-yearly");
    placeholder.classList.remove('d-none');
    yearly.classList.add('d-none');
    monthly.classList.add('d-none');
    currentElement.checked = false;
  });
  item.addEventListener("change", event => {
    const currentElement = event.currentTarget;
    const priceElement = currentElement.dataset['priceId'];
    const billingCycle = currentElement.dataset['cycle'];
    const membershipName = currentElement.dataset['name'];
    const newMembershipLbl = membershipName.replace("_", ' ').trim();
    const priceElementNode = document.querySelector(`#${priceElement}`);
    const placeholder = priceElementNode.querySelector("b.price-placeholder");
    const monthly = priceElementNode.querySelector("b.price-monthly");
    const yearly = priceElementNode.querySelector("b.price-yearly");

    // console.log(newMembershipLbl);
    createSessionStorage("newSubMembership", newMembershipLbl, true);

    placeholder.classList.add('d-none'); // by default hide the placeholder price

    // check if the user select monthly or yearly
    if (billingCycle == "monthly") {
      yearly.classList.add('d-none');
      monthly.classList.remove('d-none');
    } else if (billingCycle == "yearly") {
      monthly.classList.add('d-none');
      yearly.classList.remove('d-none');
    }

  });
});

// check if the button exists
if (dhUpgradeMembershipTableForm !== null) {
  dhUpgradeMembershipTableForm.addEventListener("submit", event => {
    event.preventDefault();
    $("#newCreditCardFormModal").modal("show");
    $("#newCreditCardFormModal").modal("handleUpdate");
  });
}


// Create a Stripe client.
const stripe = Stripe('pk_test_g5z1xvZJJ04QG9uzwR9u0Df600SMC4ANGr', {
  locale: 'en'
});

// Create an instance of Elements.
let elements = stripe.elements();

// Custom styling can be passed to options when creating an Element.
// (Note that this demo uses a wider set of styles than the guide below.)
let style = {
  base: {
    color: "#32325d",
    fontFamily: '"Helvetica Neue", Helvetica, sans-serif',
    fontSmoothing: "antialiased",
    fontSize: "16px",
    "::placeholder": {
      color: "#aab7c4",
    },
  },
  invalid: {
    color: "#fa755a",
    iconColor: "#fa755a",
  },
};

// stripe card options
const cardOptions = {
  style: style,
  hidePostalCode: true
};

// Create an instance of the card Element.
let card = elements.create("card", cardOptions);

// Add an instance of the card Element into the `card-element` <div>.
card.mount("#card-element");

// Handle real-time validation errors from the card Element.
card.on("change", function (event) {
  let displayError = document.getElementById("card-errors");
  if (event.error) {
    displayError.textContent = event.error.message;
  } else {
    displayError.textContent = "";
  }
});

// Handle form submission.
let form = document.querySelector("#data-handler-payment-form");
form.addEventListener("submit", function (event) {
  try {
    event.preventDefault();
    const cardElement = elements.getElement("card");
    if (cardElement !== null) {
      stripe.createToken(card).then(function (result) {
        if (result.error) {
          // Inform the user if there was an error.
          let errorElement = document.querySelector("#card-errors");
          errorElement.textContent = result.error.message;
        } else {

          // disable the submit button
          enableOrDisableNodeList(dhExtraRecordsAllInputs, "disable", disableAndWaitCursorCssClasses);
          (cardElement !== null) && cardElement.update({
            disabled: true
          });

          // Send the data to server.
          stripeTokenHandler(result.token);


        }

      });
    } else {

      // disable the submit button
      enableOrDisableNodeList(dhExtraRecordsAllInputs, "disable", disableAndWaitCursorCssClasses);
      (cardElement !== null) && cardElement.update({
        disabled: true
      });

      // Send the data to server.
      stripeTokenHandler();

    }
  } catch (error) {
    console.error(error);
  }



});

// Submit the form with the token ID.
const stripeTokenHandler = async (token) => {
  try {
    // Insert the token ID into the form so it gets submitted to the server
    let stripeToken;
    let formData = {};
    // check if the token exists
    if (typeof token === "undefined") {
      stripeToken = null;
      formData['is_new_card'] = false;
    } else {
      stripeToken = token.id;
      formData['is_new_card'] = true;
    }
    formData['stripeToken'] = stripeToken;

    // check if the member provide new credit card
    if (formData['is_new_card'] === true) {
      confirmRequestPromise().then(isConfirmed => {
        // check if the user click on save or not
        if (isConfirmed === true) {
          formData['save_as_default'] = true;
        } else {
          formData['save_as_default'] = false;
        }
        return formData;

      }).then(formData => {
        const chargeRequest = chargeExtraRecords(formData);
        chargeRequest.then(data => {
          // check if there is an error in the request, the request for charge
          if (data['is_error'] === false) {
            // no errors in this case
            displayTopNotification(data['msg'], "success");
            setTimeout(() => {
              location.reload();
            }, 2000);

          } else {
            displayTopNotification(data['msg'], "danger");
            throw new Error(data['msg']);
          }
        });
      }).catch(error => {
        displayTopNotification(error, "danger");
      }).finally(() => {
        setDataHandlerTableOverview();
      });
    } else {
      // in case the member will charge using old credit card
      const chargeRequest = chargeExtraRecords(formData);
      chargeRequest.then(data => {
        // check if there is an error in the request
        if (data['is_error'] === false) {
          // no errors in this case
          displayTopNotification(data['msg'], "success");
          const cardElement = elements.getElement("card");
          enableOrDisableNodeList(dhExtraRecordsAllInputs, "enable", disableAndWaitCursorCssClasses);
          (cardElement !== null) && cardElement.update({
            disabled: true
          });
          setDataHandlerTableOverview();
          setTimeout(() => {
            location.reload();
          }, 2000);


        } else {
          throw new Error(data['msg']);
        }
      }).catch(error => {
        displayTopNotification(error, "danger");
      }).finally(() => {
        setDataHandlerTableOverview();
      });
    }


  } catch (error) {
    console.error(error);
  }
};

oldStripeCardCheckbox.addEventListener("change", event => {
  const element = event.currentTarget;
  if (element.checked) {
    card.destroy();
    document.querySelector("#dh-card-element-wrapper").classList.add("d-none");
  } else {
    document.querySelector("#dh-card-element-wrapper").classList.remove("d-none");
    card = elements.create('card', cardOptions);
    card.mount('#card-element');
    // enable the submit button
    runStripeChargeBtn.classList.remove("disabled", "wait-cursor");
    runStripeChargeBtn.disabled = false;
  }
});

const confirmRequestPromise = () => {
  return new Promise((resolve, reject) => {
    Swal.fire({
      title: 'Attention',
      html: "Do you want to save the new credit card as the default on <b>PredictME</b> project?",
      icon: 'info',
      showCancelButton: true,
      confirmButtonColor: '#3085d6',
      cancelButtonColor: '#d33',
      confirmButtonText: 'Yes, save it!',
      cancelButtonText: "No, just use it for this charge",
      allowOutsideClick: false,
      allowEscapeKey: false,
      allowEnterKey: false,
    }).then((result) => {
      resolve(result.isConfirmed);
    });
  });
}