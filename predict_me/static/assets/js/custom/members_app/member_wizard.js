"use strict";

// Wizard DOM element
const wizardEl = document.querySelector('#account_settings_wizard');

// Initialize wizard object
const wizardObj = new KTWizard(wizardEl, {
  startStep: 1, // initial active step number
  clickableSteps: true, // allow step clicking
  navigation: false // disable default navigation handlers,
});

const accountSettingsSearchURL = new URL(location.href);
// check if the page has get value to active the required tab in the wizard
if (accountSettingsSearchURL.search !== "") {
  // in this case the search has value
  const searchParams = accountSettingsSearchURL.search;
  const paramName = searchParams.split("=")[0].replace("?", "");
  const paramValue = Boolean(searchParams.split('=')[1]);
  // check if the payment exists
  if ((paramName === 'payment') && (paramValue === true)) {
    wizardObj.goTo(3);
  }
}
