"use strict";
const oldStripeCardCheckbox = $("#oldStripeCardCheckbox")
// Create a Stripe client.
let stripe = Stripe("pk_test_g5z1xvZJJ04QG9uzwR9u0Df600SMC4ANGr");

// hold var is for stripe input
let stripeCardElementHolder = null;
let stripeCardElementHolderClone = null;


const extraRowsPurchased = $("#extraRowsPurchased");
const totalAmountDue = $("#totalAmountDue");

const dataHandlerSpinner = $("#data-handler-stripe-spinner");

const dataHandlerStripeFormInputs = $("#data-handler-payment-form .data-handler-stripe-charge-form")
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

// Create an instance of the card Element.
let card = elements.create("card", {
  style: style,
});

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
let form = document.getElementById("data-handler-payment-form");
form.addEventListener("submit", function (event) {
  event.preventDefault();
  // first validate the extra records count
  if ((extraRowsPurchased.val() === "") || (parseInt(extraRowsPurchased.val()) < 0)) {
    extraRowsPurchased.addClass("border-danger");
  } else {
    // here if the extra records not empty
    extraRowsPurchased.removeClass("border-danger");

    if (oldStripeCardCheckbox.is(":checked") === true) {
      // checked
      showOrHideSpinner("SHOW");
      stripeTokenHandler();
    } else {
      // not checked
      stripe.createToken(card).then(function (result) {
        if (result.error) {
          // Inform the user if there was an error.
          let errorElement = document.getElementById("card-errors");
          errorElement.textContent = result.error.message;
        } else {
          showOrHideSpinner("SHOW");
          // Send the token to your server.
          stripeTokenHandler(result.token);
        }

      });

    }
  }


});

// Submit the form with the token ID.
async function stripeTokenHandler(token) {
  // Insert the token ID into the form so it gets submitted to the server
  let stripeToken;
  // check if the token exists
  if (typeof token === "undefined") {
    stripeToken = null;
  } else {
    stripeToken = token.id;
  }
  let form = document.getElementById("data-handler-payment-form");
  let formData = {
    "stripeToken": stripeToken,
  };
  const chargeRequest = await chargeExtraRecords(formData);
  if (chargeRequest['is_done'] == true) {
    Swal.fire(
      'Success',
      chargeRequest['msg'],
      'success'
    );
    showOrHideSpinner("HIDE");
    callDataHandlerTableFunc(); // update data handler overview
  } else {
    Swal.fire({
      title: 'Attention!',
      text: chargeRequest['msg'],
      icon: 'error',
      showCancelButton: false,
      confirmButtonColor: '#3085d6',
      confirmButtonText: 'Check',
      allowEscapeKey: false,
      allowEnterKey: false,
      allowOutsideClick: false,
    }).then((result) => {
      if (result.isConfirmed) {
        showOrHideSpinner("HIDE");
        // stripeCardElementHolder = null;
      }
    })

  }

}


function enableDisableCheckBtn(isInReady, justAttach) {

  const cEle = $("#card-element, #last4Span");
  if (isInReady === true) {
    oldStripeCardCheckbox.change(function () {
      // console.log(stripeCardElementHolder);
      if (this.checked) {
        // if the checkbox is checked
        stripeCardElementHolder = cEle.detach();
        stripeCardElementHolderClone = $(stripeCardElementHolder).clone();
      } else {
        // if the checkbox not checked
        // console.log(stripeCardElementHolder);

        // console.log(stripeCardElementHolderClone.get(0) == stripeCardElementHolder.get(0));
        if (stripeCardElementHolder !== null) {
          $("#card-element-wrapper").append(stripeCardElementHolder);
        }
      }
    });
  } else {
    // if isInReady is false
    if (justAttach === true) {
      // if (typeof stripeCardElementHolder[0] === "undefined"){
      //   stripeCardElementHolder = stripeCardElementHolderClone;
      // }
      // console.log(stripeCardElementHolderClone[0]);
      if (stripeCardElementHolder !== null) {
        $("#card-element-wrapper").append(stripeCardElementHolder);
      }
    } else {
      stripeCardElementHolder = cEle.detach();
    }



  }


}


function showOrHideSpinner(showOrHide) {
  if (showOrHide === "HIDE") {
    // if set enable the
    dataHandlerSpinner.hide();
    dataHandlerStripeFormInputs.prop('disabled', false).removeClass('progress-cur');
    enableDisableCheckBtn(false, true);
  } else {
    dataHandlerSpinner.show();
    dataHandlerStripeFormInputs.prop("disabled", true).addClass('progress-cur');
    enableDisableCheckBtn(false, false);
  }
}

// this when the user enter the amount of rows which will purchased
function calculateExtraRows() {

  // check if the number of rows bigger than 0
  if (parseFloat(extraRowsPurchased.val()) < 0) {
    totalAmountDue.val(0);
  } else {
    totalAmountDue.val(parseFloat(extraRowsPurchased.val() * 0.5));
  }

}



$(function () {
  // code
  enableDisableCheckBtn(true);
  // console.log($("#dhAbovePlanLimitRecord").text())

  
});