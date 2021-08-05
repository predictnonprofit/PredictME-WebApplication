"use strict";
let isWizardEnabled = false;

const sessionID = extractLastSessionID();

let runModelBtnWizard = $("#runModelBtnWizard");

let dataHandlerWizardBtn = $("#dataHandlerWizardBtn");

let dhWizardBtnWrapper = $("#dhWizardBtnWrapper");

// wizard headers
const dhWizardStepHeader2 = $("#dhWizardStepHeader2");
const dhWizardStepHeader3 = $("#dhWizardStepHeader3");

let wizardStepsNames = {
  "1": 'upload-instructions',
  "2": "pick-columns",
  "3": "review-data"
};

let currentStepName = 'upload-instructions'; // this will change dynamicly based on process name

let setDHBtnLabel = (stepName) => {
  const btn = $("#dataHandlerWizardBtn");
  if (stepName === 'upload-instructions') {
    btn.html("Next: Select Data Columns");
  } else if (stepName === 'pick-columns') {
    dhWizardBtnWrapper.attr("data-toggle", "tooltip");
    dhWizardBtnWrapper.attr("title", "please validate columns");
    btn.html("Next: Review Data");
  }
};

// Class definition
// Wizard DOM element
let wizardEl = document.querySelector('#datahandler_wizard');

// Initialize wizard object
var wizardObj = new KTWizard(wizardEl, {
  startStep: 1, // initial active step number
  clickableSteps: true, // allow step clicking
  navigation: false // disable default navigation handlers,
});

wizardObj.on('changed', function (wizard) {
  KTUtil.scrollTop();
});

// Wizard's navigation buttons
let prevButton = wizardEl.querySelector('[data-wizard-type="action-prev"]');
let nextButton = wizardEl.querySelector('[data-wizard-type="action-next"]');

// Custom navigation handlers
prevButton.addEventListener('click', function () {
  // Go back to the previouse step
  wizardObj.goPrev();
  const step = wizardObj.getStep().toString();
  const stepName = wizardStepsNames[step];
  setDHBtnLabel(stepName);
  // console.log(dataHandlerWizardBtn.prop('disabled'));
  dataHandlerWizardBtn.removeAttr('disabled').removeClass('not-allowed-cursor disabled');
  // check if it is the first step
  // if (wizardObj.isFirstStep() === true) {
  runModelBtnWizard.hide();
  // console.log("Previous Wizard Step -> ", wizardObj.getStep());  // just for development purposes
  // }
})

nextButton.addEventListener('click', function () {
  wizardObj.goNext(); // navigate to next step
  const step = wizardObj.getStep().toString();
  const stepName = wizardStepsNames[step];
  // do some validation here
  enableDisableDhBtn("disable");
  setDHBtnLabel(stepName);

  // check if it is the last step
  if (wizardObj.isLastStep() === true) {
    runModelBtnWizard.show();
  }

  // check if it is not the first step
  if (wizardObj.isFirstStep() === false) {
    $("#dhWizardDeleteBtn").show();
  } else {
    $("#dhWizardDeleteBtn").hide();
  }

  // console.log("Next Wizard Step -> ", wizardObj.getStep());  // just for development purposes

  // check the step number then enable the wizard header
  if (wizardObj.getStep() === 2) {
    // if the user in step 2, enable step 2 header
    dhWizardStepHeader2.removeClass("bg-gray-300 not-allowed-cursor");
  } else if (wizardObj.getStep() === 3) {
    dhWizardStepHeader3.removeClass("bg-gray-300 not-allowed-cursor");
  }
});