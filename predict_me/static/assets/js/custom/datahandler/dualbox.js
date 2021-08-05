const dataTypeArray = ["", "object", "int64", "float64", 'bool', 'datetime64', 'category', 'timedelta'];
const dataTypesOptions = ["", "Unique Identifier (ID)", "Text Field", "Numeric Field", "Donation Field", "GEO-Location Field"];
const geoLocationColumns = ["Country", "City", "State", "Zip Code"];
const leftClickedColumnClass = 'columnItem';
const rightClickedColumnClass = 'pickedItem';
let clickedLeftColumnItem = "";
let clickedRightColumnItem = "";
let checkMark = "&#10004;";
let timesMark = "&#10060;";
const timesIconHtml = '<i class="icon-lg la la-times-circle text-danger"></i>';
const checkIconHtml = '<i class="icon-lg la la-check-circle text-success"></i>';
const minusIconHtml = '<i class="icon-lg la la-minus-circle text-warning"></i>';
let selectedOptionsArray = [];
let selectedValidateColumns = {};
let optionsSelected = {};
let notValidateColumns = {}; // this will hold all columns with not valid data
let isUniqueIDSelected = false; // if true the member select the unique id column, false not selected


function setColumnsTotal() {
  // this function will set the total of items in the left and right columns title
  let avaTotal = $("#availableColumnsList li").length;
  let pickTotal = $("#pickedColumnsList li").length;
  $("#avaliableColumnsTotal h5 > b").text(avaTotal);
  $("#pickedColumnsTotal h5 > b").text(pickTotal);
}


function createNewItemRightColumn(colIdx, colName, colDataType, optionsList) {

  const liMarkup = `
            <li data-idx="${colIdx}"
                class='pickedItem list-group-item d-flex justify-content-between align-items-center cursor-pointer list-group-item-action'>
                ${colName}
                <span class="element-info-icon label position-absolute" style='background-color: unset; right: 185px; display: none;'>
                      <i class="icon-lg la la-info-circle text-warning font-weight-bolder"></i>
                </span>
                <select data-value='${colDataType}' class="form-control form-control-sm column-option-dtype w-150px mx-5">
                            ${optionsList}
                    </select>
                <span id="resetIDColumnBtn" class="label position-absolute" style='background-color: unset; right: 11px; display: none;' title="Reset ID column">
                      <i class="icon-lg la la-minus-circle text-danger font-weight-bolder"></i>
                </span>

            </li>
        `;

  $("#pickedColumnsList").append(liMarkup);



}

function enableLeftColumnItem(colIdx) {
  const leftItem = fetchColumnByDataIdx(true, colIdx);
  leftItem.removeClass("disabled bg-gray-200");
}

function fetchColumnByDataIdx(isLeftCol, colIdx) {
  if (isLeftCol === true) {
    const leftColItem = $(`.${leftClickedColumnClass}[data-idx="${colIdx}"]`);
    return leftColItem;
  } else {
    const rightColItem = $(`.${rightClickedColumnClass}[data-idx="${colIdx}"]`);
    return rightColItem;
  }
}

function extractLeftColData(colItem) {
  const selectedColumnName = colItem.clone().children().remove().end().text().trim();
  const selectedColumnNameWithoutIdxNumber = selectedColumnName.split(". ")[1]; // whitout number before the column name
  const selectedColumnDataType = colItem.children().text().trim().toLowerCase();
  const selectedColumnIdx = colItem.data('idx');
  return [selectedColumnIdx, selectedColumnNameWithoutIdxNumber, selectedColumnDataType];
}

function extractRightColData(colItem) {
  const colClone = colItem.clone();
  const tt = colClone.find("select").data('value');
  let name = colClone.children().remove().end().text().trim();
  let dType = colClone.find("select").data('value');
  let colIdx = colClone.data('idx');
  return [colIdx, name, tt];
}


function saveClickedColumn(isLeftCol, colIdx) {
  // isLeftCol means if the member click on right column
  if (isLeftCol === true) {
    return fetchColumnByDataIdx(true, colIdx);
  } else {
    return fetchColumnByDataIdx(false, colIdx);
  }
}

function selectAvaliableColumns() {
  // single click on the avaliable column
  $("ul#availableColumnsList").on("click", 'li', function(ev) {
    try {
      ev.preventDefault();
      $("#availableColumnsList li.active").removeClass("active");
      $(this).addClass('active');
      const selectedColumnIdx = $(this).data('idx');
      clickedLeftColumnItem = saveClickedColumn(true, selectedColumnIdx);
    } catch (err) {
      throw err;
      clickedLeftColumnItem = '';
    }

  });

  $("ul#availableColumnsList").on("dblclick", 'li', function(ev) {
    ev.preventDefault();
    try {

      const [idx, colName, colDataType] = extractLeftColData(clickedLeftColumnItem);
      const optionsMarkup = dataTypeOptions(colDataType);
      createNewItemRightColumn(idx, colName, colDataType, optionsMarkup);
      clickedLeftColumnItem.removeClass('active').addClass("disabled bg-gray-200");

    } catch (error) {
      //throw error;
      if (error instanceof TypeError) {
        console.warn("Please select column from left!");
        // swAlert("error", "Please select column from left!", 'error');
      }
    } finally {
      clickedLeftColumnItem = ""; // to avoid duplicate items

    }

  });
}

function selectPickedRightColumns() {

  let pickedColumnsSeList = $(".colPickedItem");
  $('ul#pickedColumnsList').on('click', 'li', function(ev) {
    ev.preventDefault();
    $("#pickedColumnsList li.active").removeClass("active");
    $(this).addClass('active');
    const selectedColumnIdx = $(this).data('idx');
    clickedRightColumnItem = saveClickedColumn(false, selectedColumnIdx);


  });

  $("ul#pickedColumnsList").on("dblclick", 'li', function(ev) {
    ev.preventDefault();
    const [idx, colName, colDataType] = extractRightColData(clickedRightColumnItem);
    enableLeftColumnItem(idx);
    clickedRightColumnItem.remove();
    clickedRightColumnItem = "";
  });


}

function addItemRightColumn() {
  // add item to from left column to right column
  if (clickedLeftColumnItem !== "") {
    try {

      const [idx, colName, colDataType] = extractLeftColData(clickedLeftColumnItem);
      const optionsMarkup = dataTypeOptions(colDataType);
      createNewItemRightColumn(idx, colName, colDataType, optionsMarkup);
      clickedLeftColumnItem.removeClass('active').addClass("disabled bg-gray-200");

    } catch (error) {
      //throw error;
      // if (error instanceof TypeError) {
      //   swAlert("error", "Please select column from left!", 'error');
      // }
    } finally {
      clickedLeftColumnItem = ""; // to avoid duplicat items
    }
  } else {
    console.warn("Please select column from left!");
    // swAlert("error", "Please select column from left!", 'error');
  }
}

function addItemLeftColumn() {
  // add item to from right column to left column
  if (clickedRightColumnItem !== "") {
    const [idx, colName, colDataType] = extractRightColData(clickedRightColumnItem);
    enableLeftColumnItem(idx);
    clickedRightColumnItem.remove();
    // to set the notes in the bottom of modal
    let tmpRemovedItem = $(clickedRightColumnItem.find('select'));

    clickedRightColumnItem = "";
  } else {
    swAlert("error", "Please select column from right!", 'error');
  }
}

function addAllRightColumnItems() {
  // this when member clicked on the left column to add new item to right column
  $("#pickedColumnsList").empty(); // to avoid duplicate items in the list
  let availableColumnsList = $("#availableColumnsList li");
  availableColumnsList.each(function(cIdx, column) {
    const columnIndex = cIdx;
    const columnItem = $(column);
    clickedLeftColumnItem = columnItem;
    const [idx, colName, colDataType] = extractLeftColData(clickedLeftColumnItem);
    const optionsMarkup = dataTypeOptions(colDataType);
    createNewItemRightColumn(idx, colName, colDataType, optionsMarkup);
    clickedLeftColumnItem.removeClass('active').addClass("disabled bg-gray-200");
    clickedLeftColumnItem = "";

  });
  // this to reset and fix the criteria when add all columns btn clicked
  $(".column-option-dtype").trigger('change', "reselect");
  resetAllCriteria();
}

function addAllLeftColumnItems() {
  // this when member clicked on the right column to get back old item to left column
  const pickedColumnsList = $("#pickedColumnsList li");
  pickedColumnsList.each(function(cIdx, column) {
    const columnIndex = parseInt(cIdx);
    const columnItem = $(column);
    clickedRightColumnItem = columnItem;
    const [idx, colName, colDataType] = extractRightColData(clickedRightColumnItem);
    enableLeftColumnItem(idx);

    clickedRightColumnItem.remove();
    clickedRightColumnItem = "";
    selectedOptionsArray = [];
    resetAllColumnsToDefault();


  });
}

function validatePickedColumns(evt) {
  evt.preventDefault();
  let isAllOK = true; // if this true means all columns data type have been selected
  selectedOptionsArray = []; // to avoid any duplicated, and run the validation right

  let validatePickedColumnsList = $("#pickedColumnsList").children('li');

  if (validatePickedColumnsList.length >= 3) {
    for (let tmpPic of validatePickedColumnsList) {

      const val = $(tmpPic).find("select option:selected").text().trim().toLowerCase();
      selectedOptionsArray.push(val);
    }
    for (let col of validatePickedColumnsList) {
      const selectedDtypeOption = $(col).find("select option:selected").text().trim().toLowerCase();
      const tmpCol = $(col);
      const [idx, colName, colDataType] = extractRightColData(tmpCol);
      if (selectedDtypeOption === "") {
        // if the member did not selecte the data type of columns
        $(col).children().find("select").addClass('is-invalid');
        isAllOK = false;
      } else {
        // $("#isValidateData").html(checkMark).removeClass('text-danger').addClass("text-success");
        $(col).children().find('select').removeClass('is-invalid');
        selectedValidateColumns[colName] = selectedDtypeOption;
      }

    }

  } else {
    swAlert("Error", "Please select at least 3 columns with the data type!", 'error');
  }

  // if all columns options selected validate the columns types
  if (isAllOK === true) {
    if ((selectedOptionsArray.includes("Donation Field".toLowerCase()) === false) && (selectedOptionsArray.includes("geo-location field") === false)) {
      Swal.fire({
        title: 'Are you sure?',
        text: "No Donation and/or Geo-Location fields selected. Do you want to add Geo-Location field(s) and/or Donation field(s)?",
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#3085d6',
        cancelButtonColor: '#d33',
        confirmButtonText: 'Yes, select',
        cancelButtonText: "No, process without them",
        allowOutsideClick: false,
        reverseButtons: false,
        allowEscapeKey: false,
        allowEnterKey: false,
      }).then((result) => {
        if (!result.value) { // means the member does not select donation field
          sendRequestValidate();
        } else {
          $("#validateColumnsBtn").html("Revalidate Columns");
          dhWizardBtnWrapper.attr("data-toggle", "tooltip");
          dhWizardBtnWrapper.attr("title", "please re-validate columns");
        }
      })
    } else if (selectedOptionsArray.includes("Donation Field".toLowerCase()) === false) {
      Swal.fire({
        title: 'Are you sure?',
        text: "No Donation field(s) selected. Do you want to add a Donation field(s)?",
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#3085d6',
        cancelButtonColor: '#d33',
        confirmButtonText: 'Yes, select it',
        cancelButtonText: "No, process without it",
        allowOutsideClick: false,
        reverseButtons: false,
        allowEscapeKey: false,
        allowEnterKey: false,
      }).then((result) => {
        if (!result.value) { // means the member does not select donation field
          sendRequestValidate();
        } else {
          $("#validateColumnsBtn").html("Revalidate Columns");
          dhWizardBtnWrapper.attr("data-toggle", "tooltip");
          dhWizardBtnWrapper.attr("title", "please re-validate columns");
        }
      })
    } else if (selectedOptionsArray.includes("geo-location field") === false) {
      Swal.fire({
        title: 'Are you sure?',
        text: "No Geo-Location field(s) selected. Do you want to add a Geo-Location field(s)?",
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#3085d6',
        cancelButtonColor: '#d33',
        confirmButtonText: 'Yes, select it',
        cancelButtonText: "No, process without it",
        allowOutsideClick: false,
        reverseButtons: false,
        allowEscapeKey: false,
        allowEnterKey: false,
      }).then((result) => {
        if (!result.value) { // means the member does not select donation field
          sendRequestValidate();
        } else {
          $("#validateColumnsBtn").html("Revalidate Columns");
          dhWizardBtnWrapper.attr("data-toggle", "tooltip");
          dhWizardBtnWrapper.attr("title", "please re-validate columns");
        }
      })
    } else {
      sendRequestValidate();
    }

  }

}


function resetAllColumnsToDefault() {
  $("#pickedColumnsList").empty();
  let availableColumnsList = $("#availableColumnsList li");
  availableColumnsList.each(function(cIdx, column) {
    const colIt = $(column);
    colIt.removeClass("disabled bg-gray-200");
    clickedLeftColumnItem = "";
    clickedRightColumnItem = "";
    selectedOptionsArray = [];
    optionsSelected = {};
    isUniqueIDSelected = false;
  });
  resetAllCriteria();
}

function sendRequestValidate() {
  let validateResponseObj = validateColumnsAjaxRequest(selectedValidateColumns);
  $.when(validateResponseObj).done(function(data, textStatus, jqXHR) {
    if ((textStatus === 'success') && (jqXHR.status === 200)) {
      const notValideRequest = notValidateColumnsRequest(notValidateColumns);
      $.when(notValideRequest).done(function(notVdata, notVTextStatus, notVjqXHR) {
        if ((notVTextStatus === 'success') && (notVjqXHR.status === 200)) {
          setSessionLastName("data_process");
          for (let key in selectedValidateColumns) {
            selectedPickedColumns.push(key);
          }
          const swalWithBootstrapButtons = Swal.mixin({
            customClass: {
              confirmButton: 'btn btn-success font-weight-bolder',
              cancelButton: 'btn btn-secondary font-weight-bolder'
            },
            buttonsStyling: false
          })

          swalWithBootstrapButtons.fire({
            title: 'Success',
            text: " Validation Successful!",
            icon: 'success',
            showCancelButton: true,
            confirmButtonText: 'Proceed to next step',
            cancelButtonText: 'Go back and revalidate',
            reverseButtons: false,
            allowOutsideClick: false,
            allowEscapeKey: false,

          }).then((result) => {
            if (result.value) {
              // $("#validateColumnsBtn").attr("disabled", 'disabled').toggleClass('disabled');
              sendSelectedColumns();
              dhWizardBtnWrapper.removeAttr("title").removeAttr("data-toggle");
              enableDisableDhBtn("enable");
              $("#validateColumnsBtn").html("Revalidate Columns").addClass("disabled").attr('disabled', 'disabled');
            } else if (
              /* Read more about handling dismissals below */
              result.dismiss === Swal.DismissReason.cancel
            ) {
              $("#validateColumnsBtn").html("Revalidate Columns");
              dhWizardBtnWrapper.attr("data-toggle", "tooltip");
              dhWizardBtnWrapper.attr("title", "please revalidate columns");
              Swal.close();
            }
          })
        }
      });

    }


  });
}


function columnOptionsChangeSaved(ele, option) {
  const element = $(ele);
  const parent = $(element.parent('li'));
  element.removeAttr('title');
  // get the span of tooltip
  const tmpSpan = $(parent.find("span.element-info-icon"));
  const tmpIDSpan = $(parent.find("span#resetIDColumnBtn"));
  element.attr("data-toggle", 'tooltip');
  tmpSpan.attr('title', `Default Data Type ${element.data('value').toUpperCase()}\nCurrent data format NUMERIC`);
  const tmpCurrSelVal = element.val().split(" ")[0];
  if (tmpCurrSelVal === 'Donation') {
    element.attr("title", `Default Data Type ${element.data('value').toUpperCase()}\nCurrent data format NUMERIC`);
  } else if (tmpCurrSelVal === "Unique") {
    element.attr("title", `Default Data Type ${element.data('value').toUpperCase()}\nCurrent data format NUMERIC`);
  } else if (tmpCurrSelVal === "Text") {
    element.attr("title", `Default Data Type ${element.data('value').toUpperCase()}\nCurrent data format TEXT`);
  } else if (tmpCurrSelVal === "Numeric") {
    element.attr("title", `Default Data Type ${element.data('value').toUpperCase()}\nCurrent data format NUMERIC`);
  } else if (tmpCurrSelVal === 'GEO-Location') {
    element.attr("title", `Default Data Type ${element.data('value').toUpperCase()}\nCurrent data format GEO-Location`);
  }

  // element.removeAttr('title');  // to remove current tooltip if exists, avoid tooltip bug
  const elementLiParent = $(element.parent().parent());
  const dataIX = parent.data("idx");

  // check if the value not empty to add
  try {
    if (element.val() === "") {
      // here if the member select blank or empty option
      element.attr('title', 'Data format is empty!');

      element.addClass('border border-danger');
      // setCriterias();
      // return;

    }
    optionsSelected[dataIX] = element.val().trim().toLowerCase();


  } catch (e) {
    if (e instanceof TypeError) {
      // statements to handle TypeError exceptions
      console.error(e);
      // console.error(tmpValue);
    } else {
      // statements to handle any unspecified exceptions
      console.error(e)
    }
  } finally {
    setCriterias();
  }
  const selectOpVal = element.find("option:selected");
  // to save not validate column name
  let liColName = parent[0].firstChild.textContent.replace(/\s/g, '');
  liColName = liColName.replace(/([A-Z])/g, " $1");
  liColName = liColName.charAt(0).toUpperCase() + liColName.slice(1);
  liColName = liColName.trim();
  // check the data type if convert from number to text and otherwise
  if ((element.data("value").toLowerCase().includes("text".toLowerCase()) === true && selectOpVal.text().toLowerCase().includes('numeric') === true) || (element.data("value").toLowerCase().includes('text') === true && selectOpVal.text().toLowerCase().includes("Donation Field".toLowerCase()) === true)) {
    // this to save not validate data type columns
    const liColValue = element.data("value");
    const liColSelectedValue = selectOpVal.val();
    notValidateColumns[liColName] = {
      "from": liColValue,
      "to": liColSelectedValue.split(' ')[0]
    };

    let confirmMsg = `Warning. You are converting a default '${element.data("value").toUpperCase()}' data type to a '${selectOpVal.text().replace(" Field", "")}' data type!`;

    // check if this call from reselect columns function to ignore show the dialog of change data type warning
    // check if member click no set the select option to null, else select the option
    if ((typeof option === undefined) || (typeof option === 'undefined')) {
      swConfirmDtype(element, confirmMsg, tmpSpan, dataIX);

    } else if (option === 'reselect') {
      tmpSpan.show();
      // tmpSpan.attr('title', `Default Data Type ${element.data('value').toUpperCase()}\nCurrent data format ${element.data('value').toUpperCase()}`);
      if (tmpCurrSelVal === 'Donation') {
        tmpSpan.attr("title", `Default Data Type ${element.data('value').toUpperCase()}\nCurrent data format NUMERIC`);
      } else if (tmpCurrSelVal === "Unique") {
        tmpSpan.attr("title", `Default Data Type ${element.data('value').toUpperCase()}\nCurrent data format ${element.data('value').toUpperCase()}`);
      } else if (tmpCurrSelVal === "Text") {
        tmpSpan.attr("title", `Default Data Type ${element.data('value').toUpperCase()}\nCurrent data format TEXT`);
      } else if (tmpCurrSelVal === "Numeric") {
        tmpSpan.attr("title", `Default Data Type ${element.data('value').toUpperCase()}\nCurrent data format NUMERIC`);
      }
      element.addClass('border border-danger');
      element.data("reselected", "1");
      element.attr("data-toggle", 'tooltip');
      // check if the donation field selected to make it visible with check mark
      if (element.val().toLowerCase().includes('donation') === true) {
        $("#donationField").html(checkIconHtml);
      }
      // check if the geo-location field selected to make it visible with check mark
      if (element.val().toLowerCase().includes('geo') === true) {
        $("#geoLocationField").html(checkIconHtml);
      }
    }

  } else {
    tmpSpan.hide();
    // this to remove the column from not validate columns
    if (Object.keys(notValidateColumns).includes(liColName) === true) {
      delete notValidateColumns[liColName];
    }
  }
  // check if the member select the id so disabled on the others select
  if ((element.val().toLowerCase() === "Unique Identifier (ID)".toLowerCase())) {
    element.data('is-uid', '1');
    if (element.data("value") !== "") {
      $(".column-option-dtype  option:contains('Unique Identifier (ID)')").attr("disabled", "disabled");
      isUniqueIDSelected = true;
      tmpIDSpan.show();
      element.attr("disabled", "disabled");
      element.addClass("disabled");
      element.attr('data-toggle', 'tooltip');
      element.attr("title", `Default Data Type ${element.data('value').toUpperCase()}\nCurrent data format ${element.data('value').toUpperCase()}`);

      // when member click on the reset unique button
      tmpIDSpan.on("click", function(e) {
        let clickedResetID = $(this);
        let clickedResetIDParent = $(this).parent().find("select");
        $(".column-option-dtype  option:contains('Unique Identifier (ID)')").removeAttr("disabled");
        // let ix = optionsSelected.indexOf("Unique Identifier (ID)".toLowerCase());
        // optionsSelected.splice(ix, 1);  // delete the id from the array
        delete optionsSelected[dataIX]; // delete the id from the json object
        clickedResetID.hide();
        isUniqueIDSelected = false;
        element.removeAttr('title');
        clickedResetIDParent.val("");
        $("#selectUniqueID").html(timesIconHtml);
        // $("#isValidateData").html(timesMark).removeClass("text-success").addClass("text-danger");
        element.addClass('border border-danger');
        clickedResetIDParent.removeAttr("disabled");
        clickedResetIDParent.removeClass("disabled");
        setCriterias();

      });

    } else {
      swAlert("Error", "Unique ID must be not NULL!", 'error');
      delete optionsSelected[dataIX]; // delete the id from the json object
      element.val("");
      element.removeAttr('title');
    }
  }


  // check if the member select unique id option, check mark criteria of it
  setCriterias();


}


// this function will set the criterias if the user delete, ...etc
function setCriterias() {
  let cirStatus = false;
  let cirMsg = "";
  // check if the member select unique id option, check mark criteria of it
  if (checkValueExists(optionsSelected, "Unique Identifier (ID)".toLowerCase()) === true) {
    $("#selectUniqueID").html(checkIconHtml);
    isUniqueIDSelected = true;
  } else {
    $("#selectUniqueID").html(timesIconHtml);
    isUniqueIDSelected = false;
    cirStatus = true;
    cirMsg = 'error in uid';
  }
  // check if donation field selected

  if (checkValueExists(optionsSelected, "Donation Field".toLowerCase()) === true) {
    $("#donationField").html(checkIconHtml);
  } else {
    $("#donationField").html(minusIconHtml);

  }
  if (checkValueExists(optionsSelected, "geo-location field".toLowerCase()) === true) {
    $("#geoLocationField").html(checkIconHtml);
  } else {
    $("#geoLocationField").html(minusIconHtml);

  }


  // check if the length more than 3 options mean select 3 columns, check its criteria
  if (Object.keys(optionsSelected).length <= 2) {
    $("#isValidateData").html(timesIconHtml);
    cirStatus = true;
    cirMsg = 'error in minimum selected'

  } else {
    $("#isValidateData").html(checkIconHtml);
  }

  // check if text fields more than 2
  if (countJsonItems(optionsSelected, "Text Field".toLowerCase()) > 2) {
    $("#isSelect3Col").html(checkIconHtml);
  } else {
    $("#isSelect3Col").html(timesIconHtml);
    cirStatus = true;
    cirMsg = 'error text fields less than 3';

  }


  $(".column-option-dtype").each(function(idx, val) {
    let currTmpEle = $(val);

    if ((currTmpEle.val() !== '') && (currTmpEle.val() !== null)) {
      // here if the element is not uid
      // check if the it is reselect data attribute exists to keep the red border

      currTmpEle.removeClass("border border-danger");
      if (currTmpEle.data('reselected') === '1') {
        currTmpEle.addClass("border border-danger");
      }

    } else if ((currTmpEle.data('is-uid') === '1') && (currTmpEle.val() === null)) {
      // here if the element is uid
    } else {
      // here if the element is empty
      currTmpEle.addClass("border border-danger");
      $("#isValidateData").html(timesIconHtml);
      cirStatus = true;
      cirMsg = 'emtpy select';
    }
  });
  if (cirStatus === true) {
    // console.error('there errors!!!');
    // console.error(cirMsg);
    enableValidateProcBtn('disable');

  } else {
    // here no errors or all criterias are good to go
    enableValidateProcBtn('enable');
  }
}

// reset all criteria after reset button clicked
function resetAllCriteria() {
  $("#isValidateData").html(timesIconHtml);
  $("#isSelect3Col").html(timesIconHtml);
  $("#selectUniqueID").html(timesIconHtml);
  $("#donationField").html(minusIconHtml);
  $("#geoLocationField").html(minusIconHtml);
  $("#validateColumnsBtn").addClass("btn-light-primary disabled");
  $("#validateColumnsBtn").attr("disabled", "disabled");
  $("#validateColumnsBtn").attr("style", "cursor: not-allowed;");
}

// this function will disable or enable validate or process buttons as needed
function enableValidateProcBtn(action) {
  if (action === 'enable') {
    $("#validateColumnsBtn").removeClass("disabled btn-light-primary");
    $("#validateColumnsBtn").removeAttr("disabled style");
    $("#validateColumnsBtn").addClass("btn-primary");
  } else {
    $("#validateColumnsBtn").addClass("btn-light-primary disabled");
    $("#validateColumnsBtn").attr("disabled", "disabled");
    $("#validateColumnsBtn").attr("style", "cursor: not-allowed;");
  }
}


let targetNodes = $("#pickedColumnsList");
let MutationObserver = window.MutationObserver || window.WebKitMutationObserver;
let myObserver = new MutationObserver(mutationHandler);
let obsConfig = {
  childList: true,
  characterData: true,
  attributes: true,
  subtree: true
};
//--- Add a target node to the observer. Can only add one node at a time.
targetNodes.each(function() {
  myObserver.observe(this, obsConfig);
});

function mutationHandler(mutationRecords) {

  // console.info("mutationHandler:");
  mutationRecords.forEach(function(mutation) {
    // this condition if one the childes is delete or remove from the dom
    if (typeof mutation.removedNodes === 'object') {
      try {
        const textContent = mutation.removedNodes[0].textContent.trim() ? (typeof mutation.removedNodes !== undefined) : "";
        if (textContent !== "") {
          let pickedRightCol = $(mutation.removedNodes);
          const pickedRightSelect = pickedRightCol.find('select');
          const rightSelectParentLi = pickedRightSelect.parents('li');
          // check if the removed item is the unique id
          if (pickedRightSelect.is(":disabled") === true) {
            //unique identifier (id)
            for (key in optionsSelected) {
              if (optionsSelected.hasOwnProperty(key) && optionsSelected[key] === 'unique identifier (id)') {
                delete optionsSelected[key];
                $(".column-option-dtype  option:contains('Unique Identifier (ID)')").removeAttr("disabled");
                isUniqueIDSelected = false;
              }
            }
          } else {
            const idx = rightSelectParentLi.data('idx');
            delete optionsSelected[idx];

          }
          setCriterias();


        }

      } catch (e) {
        if (e instanceof TypeError) {

        }
        if (!(e instanceof TypeError)) {
          console.error(e);
        }
      }
    }

    if (typeof mutation.addedNodes === 'object') {
      //dualbox-btn
      let pickTotal = $("#pickedColumnsList li").length;
      // check if there are any pick columns
      if (pickTotal > 0) {
        $("#resetColumnBoxBtn").prop('disabled', false);
      } else {
        $("#resetColumnBoxBtn").prop("disabled", true);
      }
      let pickedRightCol = $(mutation.addedNodes);
      const pickedRightSelect = pickedRightCol.find('select');
      if (pickedRightSelect.length > 0) {
        if (isUniqueIDSelected === true) {
          $(".column-option-dtype  option:contains('Unique Identifier (ID)')").attr("disabled", "disabled");
        } else {
          $(".column-option-dtype  option:contains('Unique Identifier (ID)')").removeAttr("disabled");
        }
        setCriterias();

        // here for set criteria to false because no data type selected for new column

      }
    }


  });
}


jQuery(document).ready(function() {
  //mutationObservFunc();
  selectAvaliableColumns();
  selectPickedRightColumns();
  let addColumnBtn = $("#addColumnBtn");
  addColumnBtn.on("click", addItemRightColumn);
  let removeColumnBtn = $("#removeColumnBtn");
  removeColumnBtn.on('click', addItemLeftColumn);
  let addAllColumnsBtn = $("#addAllColumnsBtn");
  addAllColumnsBtn.on('click', addAllRightColumnItems);
  let removeAllColumnsBtn = $("#removeAllColumnsBtn");
  removeAllColumnsBtn.on('click', addAllLeftColumnItems);
  let validateColumnsBtn = $("#validateColumnsBtn");
  validateColumnsBtn.on("click", validatePickedColumns);
  let columnsDataTypeOptions = $(".column-option-dtype");
  $("#pickedColumnsList").on("change", ".column-option-dtype", function(evt, option) {
    columnOptionsChangeSaved(this, option);
  });



  let totalInterval = setInterval(function() {
    setColumnsTotal();
  }, 200);


  //removePickedColumn();
  let resetColumnBoxBtn = $("#resetColumnBoxBtn");
  resetColumnBoxBtn.on("click", resetAllColumnsToDefault);



});
