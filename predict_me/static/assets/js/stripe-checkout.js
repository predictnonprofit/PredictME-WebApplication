$(function () {
    // Create a Stripe client.
    var stripe = Stripe('pk_test_g5z1xvZJJ04QG9uzwR9u0Df600SMC4ANGr', {
        locale: 'en'
    });

    // Create an instance of Elements.
    var elements = stripe.elements();

    // Custom styling can be passed to options when creating an Element.
    // (Note that this demo uses a wider set of styles than the guide below.)
    var style = {
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

    // Create an instance of the card Element.
    var card = elements.create('card', {style: style});

    // Add an instance of the card Element into the `card-element` <div>.
    card.mount('#card-element');

    // Handle real-time validation errors from the card Element.
    card.addEventListener('change', function (event) {
        var displayError = document.getElementById('card-errors');
        if (event.error) {
            displayError.textContent = event.error.message;
        } else {
            displayError.textContent = '';
        }
    });

    // Handle form submission.
    var form = document.getElementById('payment-form');
    form.addEventListener('submit', function (event) {
        event.preventDefault();

        stripe.createToken(card).then(function (result) {
            if (result.error) {
                // Inform the user if there was an error.
                var errorElement = document.getElementById('card-errors');
                errorElement.textContent = result.error.message;
            } else {
                // Send the token to your server.
                stripeTokenHandler(result.token);
            }
        });
    });

    // Submit the form with the token ID.
    function stripeTokenHandler(token) {
        // Insert the token ID into the form so it gets submitted to the server
        var form = document.getElementById('payment-form');
        var hiddenInput = document.createElement('input');
        hiddenInput.setAttribute('type', 'hidden');
        hiddenInput.setAttribute('name', 'stripeToken');
        hiddenInput.setAttribute('value', token.id);
        form.appendChild(hiddenInput);

        // Submit the form
        form.submit();
    }

});

$(document).ready(function () {
    // my custom js code, the above code not for stripe

    // this to enable the payment submit btn when user accept the payment and terms of use checkbox
    $("#agree_payment").change(function () {
        let paymentBtn = $('#paymentBtn');
        if (this.checked) {
            paymentBtn.removeAttr("disabled");
            paymentBtn.removeClass("disabled not-allowed-cursor");
        } else {
            paymentBtn.attr("disabled", "disabled");
            paymentBtn.addClass("disabled not-allowed-cursor");
        }
    });

    // this to disable payment terms link
    $('#paymentTermsLink').click(function (e) {
        e.preventDefault();
    });

    // this to display the selected subscription range (yearly, monthly)
    $('input[name="sub_range"]').click(function () {
        let sRange = $("#sRange");
        let sPrice = $("#sPrice");
        const ele = $(this);
        if ($(this).is(':checked')) {
            let rangeVal = $(this).closest('label').text().trim();
            // check if select monthly or yearly to print the correct "in Month", "in Year"
            if(rangeVal === "Monthly"){
                sRange.text("Month");
            }else{
                sRange.text("Year");
            }

            // check if select monthly or yearly to print the correct value in accept payment block
            if(rangeVal === "Monthly"){
                sPrice.text("Currently $" + ele.data('price') );  // the correct monthly value save it or parse it from context variable in django view
            }else{
                sPrice.text("Currently $" + ele.data('price'));
            }
        }
    });


    // disable the button after click
    const paymentBtn = $('#paymentBtn');
    paymentBtn.on("click", function(event){
      this.attr("disabled", "disabled");
      this.addClass("disabled not-allowed-cursor");
    });
})
