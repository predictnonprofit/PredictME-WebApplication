/*
    this file contain custom js functions for ajax,...etc
*/
"use strict";
var selectedPickedColumns = Array(); // global array will include the picked and validated column names
// var webSiteUrl = window.location.origin;
const tooltipInfo = {
  "object": "Text or mixed numeric and non-numeric values",
  "int64": "Integer numbers",
  "float64": "Floating point numbers",
  "bool": "True/False values",
  "datetime64": "Date and time values",
  "category": "Finite list of text values",
  "timedelta": "Differences between two datetimes",
};

// this variable will save all new update for the every row that change its data
var allRowsUpdated = {}; // object of new updated rows
var clickedRecordsCount = 25; // the current records number that appear to the member
var clickedFilteredColName = ""; // the clicked column to filter, "" -> means no column has been clicked
var isClickedFilterCol = false; // true means the member clicked on the column header to sort the columns
var undoValuesObj = []; // this object will contain all values that changed with old values
var lastResultsLayout = {}; // this will hold the current layout position, and display the data based on it
var isSearchMode = false; // when this is true the user search in data table
var lastRowCountTotal = 0; // this will equal the sum of last row total
var clonedNavBtns = ""; // this is the clone of nav btns will reset after clen search query


function swConfrim(title, msg) {

  bootbox.confirm("This is the default confirm!", function (result) {
    console.log('This was logged in the callback: ' + result);
  });

  // return ;

}

// sweetalert2 confirm custom dialogbox only show when the memeber change the data type of the column
function swConfirmDtype(elem, msg, tmpSpan, dataIX) {

  const swalWithBootstrapButtons = Swal.mixin({
    customClass: {
      confirmButton: 'btn btn-success',
      cancelButton: 'btn btn-danger'
    },
    buttonsStyling: false
  })

  swalWithBootstrapButtons.fire({
    title: 'Are you sure?',
    text: msg,
    icon: 'warning',
    showCancelButton: true,
    confirmButtonText: 'Yes',
    cancelButtonText: 'No',
    backdrop: true,
    allowOutsideClick: false,
    allowEscapeKey: false,
    allowEnterKey: false,
    showLoaderOnConfirm: true,
    reverseButtons: true,
    stopKeydownPropagation: false,
    focusCancel: true,

  }).then((result) => {
    if (result.value) {

      tmpSpan.show();

    } else if (
      /* Read more about handling dismissals below */
      result.dismiss === Swal.DismissReason.cancel
    ) {
      elem.val("");
      tmpSpan.hide();
      delete optionsSelected[dataIX];
      setCriterias(); // to fix criterias

    }
  });


}

// this will get the function name
function getFunctionName(fun) {
  let funName = fun.toString();
  funName = funName.substr('function '.length);
  funName = funName.substr(0, funName.indexOf('('));
  return funName;
}


// count duplicated items in array
function coutItems(arrayVar, value) {
  let count = 0;
  arrayVar.forEach((v) => (v === value && count++));
  return count;
}

// count duplicated values in json object
function countJsonItems(jsonObj, value) {
  let count = 0;
  for (let i in jsonObj) {
    if (jsonObj[i] === value) {
      count++;
    }
  }
  return count;
}

// check if value exists in json object
function checkValueExists(json, value) {
  for (let key in json) {
    if (typeof (json[key]) === "object") {
      return checkForValue(json[key], value);
    } else if (json[key] === value) {
      return true;
    }
  }
  return false;
}


// this ajax function which will upload the donor data file
function uploadDonorDataFile(uploadForm) {

  const donerFileInput = $("#donerFile");
  let donerFile = document.querySelector('#donerFile');
  let allowedFileTypes = [
    "application/vnd.ms-excel",
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    'text/csv'
  ];
  if (window.FileReader && window.Blob) {
    // All the File APIs are supported
    const fileType = donerFile.files[0].type;
    // check if the uploaded file type is allowed
    if (allowedFileTypes.includes(fileType) === true) {
      if (donerFileInput.val()) {
        // $form = uploadForm;
        let formData = new FormData($("#uploadDataFileForm")[0]);
        const fileName = donerFileInput.val().split(/(\\|\/)/g).pop(); // get the file name to parse it in url
        formData.append('session-label', $("#session-name").val());
        formData.append('file_name', fileName);
        // ajax request to data handler init
        return $.ajax({
          method: "POST",
          cache: false,
          // async: false,
          processData: false,
          contentType: false,
          timeout: 300000, // 5 minutes
          // timeout: 5000,
          url: `${webSiteUrl}/dashboard/data/upload/${fileName}`,
          data: formData,
          beforeSend: function (xhr, settings) {
            let timerInterval;
            xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
            let swalUploadProgressDialog = swal.fire({
              title: "Uploading...",
              text: "Uploading your data file, Please wait...",
              showConfirmButton: false,
              allowOutsideClick: false,
              allowEscapeKey: false,
              allowEnterKey: false,
              // stopKeydownPropagation: false,
              // keydownListenerCapture: true,
              // timer: 3000,
              willOpen: () => {
                Swal.showLoading()
                timerInterval = setInterval(() => {
                  const content = Swal.getContent()
                  if (content) {
                    const b = content.querySelector('b')
                    if (b) {
                      b.textContent = Swal.getTimerLeft()
                    }
                  }
                }, 100)
              },
              willClose: () => {
                clearInterval(timerInterval);
                $("#dataHandlerUploadProgressLabel").html('Please wait while counting your records...');
              }
            });
          },
          complete: (jqXHR, textStatus) => {
            // refresh data handler table overview
            callDataHandlerTableFunc();
          },
          error: function (error) {
            //called when there is an error
            // console.log(error);
            swAlert("Error", `${error.statusText}:-> ${error.message}`, "error");
          },
          statusCode: {
            404: function () {
              swAlert("Error", "Page not Found!!", "error");
            },
            400: function () {
              swAlert("Error", "Bad Request!!!", "error");
            },
            401: function () {
              swAlert("Error", "Unauthorized!!", "error");
            },
            403: function () {
              swAlert("Error", "Forbidden!!", "error");
            },
            500: function () {
              swAlert("Error", "Internal Server Error!!", "error");
            },
            502: function () {
              swAlert("Error", "Bad Gateway!!", "error");
            },
            503: function () {
              swAlert("Error", "Service Unavailable!!", "error");
            },

          },
          xhr: function () {
            var xhr = $.ajaxSettings.xhr();
            xhr.onprogress = function (e) {
              // For downloads
              // $('.dhInput').attr("disabled", 'disabled').addClass('progress-cursor');
              if (e.lengthComputable) {
                // console.log(e.loaded / e.total);
              }
            };
            xhr.upload.onprogress = function (e) {
              // For uploads
              // console.log(e);
              if (e.lengthComputable) {
                // console.log(e.loaded / e.total);
              }
            };
            return xhr;
          }
        }).done(function (e) {
          Swal.close();
          setSessionLastName("upload");
          // first, delete all saved sessions
          // console.log('delete all sessions...');
          window.sessionStorage.clear();
          // save last session id
          const lastSessionID = parseInt(e['last_session_id']);
          // console.log('set last session: ', lastSessionID);
          window.sessionStorage.setItem("lastSessionID", lastSessionID);

        }).fail(function (e) {
          console.error("upload failed!!");
          console.error(e);
        });

      } else {
        swal.fire("Error", "You have to select a file!", "error");
      }
    } else {
      /* Swal.fire(
        'Error!',
        'Not allowed file type!',
        'error'
      ); */
      alert('Not allowed file type!');
    }
  } else {
    // File and Blob are not supported
    swAlert("Error", "Your web browser not support File and Blob API!", "error");

  }

}



// this function will sort the columns for data handler table
function setColumnNamesHeader(columnsList) {
  // this to delete any th elements exists before, to avoid duplicate th elements
  $("#data_handler_table > thead > tr").children("th").remove();
  let tableHeaderElement = $("#data_handler_table > thead > tr:last");
  for (let col of columnsList) {
    let row = "";
    if (col['isUnique'] === true) {
      row = `
            <th style="cursor: default !important; white-space: nowrap;" data-col-name='${col["headerName"]}' data-is-unique-col="1" onclick='sortHeader(this);' class='dataTableHeader text-center'>
            ${col["headerName"]}<i style="top: 2px" class="icon-md d-none position-relative text-danger la la-sort"></i>
            <i style="top: 2px" class="icon-md la la-info-circle error-icon-table-header text-danger d-none position-relative"></i>
            </th>
        `;
    } else {
      row = `
            <th style="cursor: default !important; white-space: nowrap;" data-col-name='${col["headerName"]}' data-is-unique-col="0" onclick='sortHeader(this);' class='dataTableHeader text-center'>
            ${col["headerName"]}<i style="top: 2px" class="icon-md d-none position-relative text-danger la la-sort"></i>
            <i style="top: 2px" class="icon-md la la-info-circle error-icon-table-header d-none position-relative text-danger"></i>
            </th>
        `;
    }
    tableHeaderElement.append(row);
  }
}


// this function return markup objects of every table cell will append to every row in the datatable
function drawDataTableRows(rowsData, isValidate, isLastPage) {
  const paginationPerPage = $("#paginationPerPage");
  let oldPerPageVal = parseInt(paginationPerPage.html());
  // check if the value equal 0
  if (oldPerPageVal === 0) {
    paginationPerPage.html(parseInt(oldPerPageVal + rowsData.total_rows));
  }

  $("#noFileUploadedElement").hide();
  $("#data-handler-table-wrapper").show();
  let currentRowData = rowsData.data;
  // console.log(clickedRecordsCount);
  lastRowCountTotal = clickedRecordsCount;
  // set the page records total
  let perPage = parseInt($("#paginationPerPage").text());
  $(".datatable-row").remove(); // to update the new rows when revalidate the columns

  // check the length of total rows came from excel file, in case one row, or less than 50 rows
  if (rowsData.total_rows < 25) {
    $(".data-table-nav-btns").addClass('disabled').attr('disabled', 'disabled');
  } else {
    $(".data-table-nav-btns").removeClass('disabled').removeAttr('disabled');
  }

  // console.log(currentRowData[0]);
  // console.log(currentRowData);
  // check if it is last page btn
  if (isLastPage === true) {
    $("[data-action='next'], [data-action='last']").attr("disabled", "disabled").addClass("disabled").tooltip('hide');
  }
  if ((typeof currentRowData === undefined) || (typeof currentRowData === 'undefined')) {
    // here when no rows, 0
    console.error("No records to display!!");
    $("[data-action='next']").attr("disabled", "disabled").addClass("disabled").tooltip('hide');
  } else {
    if (isSearchMode === true) {
      $('.data-table-nav-btns').attr("disabled", 'disabled').addClass('disabled');
    } else {
      // check if the (clickedRecordsCount) = 50 this mean the user in the first page, then disable the previous (<) indicator of pagination
      if (clickedRecordsCount === 25) {
        $("[data-action='previous']").attr("disabled", "disabled").addClass("disabled").tooltip('hide');
        $("[data-action='first']").attr("disabled", "disabled").addClass("disabled").tooltip('hide');
      } else {
        $("[data-action='previous']").removeAttr("disabled").removeClass("disabled").tooltip('update');
        $("[data-action='first']").removeAttr("disabled").removeClass("disabled").tooltip('update');
      }
    }
    // check if this data not validate
    if (isValidate === false) {
      let tableBodyElement = $("#data_handler_table > tbody tr:last");

      for (let colIdx = 0; colIdx < currentRowData.length; colIdx++) {
        let currentDataObj = currentRowData[colIdx];

        if (currentDataObj["PANDAS_ID"] === 4) {
          // console.log(currentDataObj);
        }
        // console.log(currentDataObj);
        let allCells = "";
        let tableRow = "<tr class='datatable-row'> ";
        // console.log(Object.entries(currentDataObj));
        // loop through key and value in the json object of the row
        for (let [key, value] of Object.entries(currentDataObj)) {
          // console.log(key, value);
          if (key !== "PANDAS_ID") {
            const tableColHeader = $(`#data_handler_table > thead tr > th[data-col-name='${key}']`);
            // the below to mark the column header it has error
            // tableColHeader.addClass('protip');
            // tableColHeader.attr('data-pt-classes', 'bg-secondary text-dark');
            // tableColHeader.attr('data-pt-gravity', 'top');
            // tableColHeader.attr('data-pt-animate', 'animate__animated animate__fade');
            // tableColHeader.attr('data-pt-delay-in', '500');
            // tableColHeader.append("<span id='newItem'>New</span>")
            tableColHeader.addClass("red-tooltip");
            tableColHeader.attr('data-toggle', 'tooltip');
            tableColHeader.attr("title", "");
            // tableColHeader.attr("data-trigger", "click");  // just for developments
            tableColHeader.attr("data-html", "true");
            tableColHeader.attr("data-placement", "top");
            tableColHeader.attr("data-container", "body");
            const tmpCurrSelVal = value['data_type'].split(" ")[0];
            // console.log('tmpCurrSelVal -> ', tmpCurrSelVal);
            if (tmpCurrSelVal === 'donation') {
              tableColHeader.attr("data-original-title", `Default data type ${capitalizeFirstLetter(value['original_dtype'])} <br /> Current data type Numeric`);
            } else if (tmpCurrSelVal === "unique") {
              tableColHeader.attr("data-original-title", `Default data type ${capitalizeFirstLetter(value['original_dtype'])} <br /> Current data type Numeric`);
            } else if (tmpCurrSelVal === "text") {
              tableColHeader.attr("data-original-title", `Default data type ${capitalizeFirstLetter(value['original_dtype'])} <br /> Current data type Text`);
            } else if (tmpCurrSelVal === "numeric") {
              tableColHeader.attr("data-original-title", `Default data type ${capitalizeFirstLetter(value['original_dtype'])} <br /> Current data type Numeric`);
            } else if (tmpCurrSelVal === 'geo-location') {
              tableColHeader.attr("data-original-title", `Default data type ${capitalizeFirstLetter(value['original_dtype'])} <br /> Current data type GEO-Location`);
            }

            if (value.is_error === false) {
              // check if the data type is numeric or donation will restric the member from enter numeric data
              if (value.data_type === "donation field" || value.data_type === "numeric field") {
                var cellMarkup = `

                    <td class=''>
                        <input class='form-control data-table-col data-table-input' data-row-id='${currentDataObj["PANDAS_ID"]}' onkeypress="return isNumber(event)" type='text' name='${key}' value='${value.value}' />
                    </td>

                `;
              } else if (value.data_type === "unique identifier (id)") {
                var cellMarkup = `

                    <td class=''>
                        <input class='form-control data-table-col data-table-input' data-row-id='${currentDataObj["PANDAS_ID"]}' onkeypress="return isNumber(event)" readonly="readonly" type='text' name='${key}' value='${value.value}' />
                    </td>

                `;
              } else {
                var cellMarkup = `

                    <td class=''>
                        <input class='form-control data-table-col data-table-input' data-row-id='${currentDataObj["PANDAS_ID"]}' type='text' name='${key}' value='${value.value}' />
                    </td>

                `;
              }
            } else if (value.is_error === true) {
              // the below to mark the column header it has error
              tableColHeader.attr("data-is-error", '1');
              tableColHeader.css('cursor', "pointer");
              // tableColHeader.attr('data-pt-classes', 'bg-danger text-white');
              // const tableColHeaderWithErrorIcon = `${tableColHeader.html()} <i class="icon-xl la la-info-circle"></i>`;
              // tableColHeader.html(tableColHeaderWithErrorIcon);
              const colText = tableColHeader.text().trim();
              // check if the current table td value has error, highlighted the column name header
              if (key.trim() === colText) {
                //console.log("error", colText);
                // console.log(tableColHeader.find("i.error-icon-table-header"));
                tableColHeader.find("i.error-icon-table-header").removeClass("d-none");
                // tableColHeader.addClass("bg-light-danger")
                tableColHeader.addClass("text-danger");
              }

              if (value.data_type === "donation field" || value.data_type === "numeric field" || value.data_type === "unique identifier (id)") {
                var cellMarkup = `

                    <td class='text-center'>
                        <input class='form-control bg-light-danger data-table-col data-table-input' onkeypress="return isNumber(event)" data-row-id='${currentDataObj["PANDAS_ID"]}' type='text' name='${key}' value='${value.value}' />
                    </td>

                `;
              } else {
                var cellMarkup = `

                    <td class='text-center'>
                        <input class='form-control bg-light-danger data-table-col data-table-input' data-row-id='${currentDataObj["PANDAS_ID"]}' type='text' name='${key}' value='${value.value}' />
                    </td>

                `;
              }

            }
            allCells += cellMarkup;
          }
        }

        tableRow += allCells + "</tr>";
        tableBodyElement.after(tableRow);
        $('.red-tooltip').tooltip();
      }
      $("#dataListTable").css("opacity", "1");

      // to run the function of save the new updates of data table cells
      // saveNewUpdatedData();
    } else {
      // console.log(currentRowData);
      // this else if the data are not valid

      let tableBody = document.getElementById("data_handler_body");
      tableBody.innerHTML = "";
      //$("#data_handler_table tbody tr").fadeIn();
      for (let colIdx = 0; colIdx < currentRowData.length; colIdx++) {
        let currentDataObj = currentRowData[colIdx];
        let allCells = "";
        let tableRow = "<tr> ";
        // console.log(currentDataObj);
        for (let [key, value] of Object.entries(currentDataObj)) {

          if (key !== "PANDAS_ID") {
            // console.log(currentDataObj["ID"], "|", key, "|", value.value);
            //console.log(key, '---', value);


            if (value.is_error === false) {
              if (value.data_type === "donation field" || value.data_type === "numeric field" || value.data_type === "unique identifier (id)") {
                var cellMarkup = `

                            <td>
                                <input class='form-control form-control-solid data-table-col data-table-input' onkeypress="return isNumber(event)" data-row-id='${currentDataObj["PANDAS_ID"]}' type='text' name='${key}' value='${value.value}' />
                            </td>

                        `;
              } else {
                var cellMarkup = `

                            <td>
                                <input class='form-control form-control-solid data-table-col data-table-input' data-row-id='${currentDataObj["PANDAS_ID"]}' type='text' name='${key}' value='${value.value}' />
                            </td>

                        `;
              }


            } else if (value.is_error === true) {

              if (value.data_type === "donation field" || value.data_type === "numeric field" || value.data_type === "unique identifier (id)") {
                var cellMarkup = `

                    <td>
                        <input class='form-control bg-light-danger is-invalid data-table-col form-control-solid data-table-input' onkeypress="return isNumber(event)" data-row-id='${currentDataObj["PANDAS_ID"]}' type='text' name='${key}' value='${value.value}' />
                    </td>

                `;
              } else {
                var cellMarkup = `

                    <td>
                        <input class='form-control bg-light-danger is-invalid data-table-col form-control-solid data-table-input' data-row-id='${currentDataObj["PANDAS_ID"]}' type='text' name='${key}' value='${value.value}' />
                    </td>

                `;
              }

            }
            allCells += cellMarkup;
          }

          // console.log(allCells);
          // throw new Error("Something went badly wrong!");

        }
        tableRow += allCells + "</tr>";
        tableBody.innerHTML += tableRow;


      }

      // to run the function of save the new updates of data table cells
      // saveNewUpdatedData();


    }
  }


  $("#dataListTable").css("opacity", "1");
  $("#loadingDataSpinner").fadeOut('fast');

  saveNewUpdatedData();

}




// this function when user upload the file, and show the progress modal,
// this will hide or show as needed
function uploadProgressModal(isOk, data) {


  var optionsList = '';
  var dataFileColumnsSelect = $("#availableColumnsList");
  // is Ok mean if the row counts dont cross the records limit of the member supscription plan

  let rowCount = parseInt(data['row_count']);
  var rowCountProgressDialog = $("#recordsCountModal");
  var recordsCounterProgressBar = $("#recordsCounterProgressBar");
  let currentRowCounter = $("#currentRowCounter > b");
  let progressWarnText = $("#progressWarnText");
  let nextProgressBtnModal = $("#nextProgressBtnModal");
  let allowdedRowsCount = $("#progressRecords > b:first");
  rowCountProgressDialog.modal('show');
  rowCountProgressDialog.modal('handleUpdate');
  recordsCounterProgressBar.attr("aria-valuemax", '100');
  let progVal = 0;
  // the interval
  var progressInterval = setInterval(progressIntervalFunc, 35);


  function progressIntervalFunc() {
    // $('.dhInput').attr('disabled', 'disabled').addClass('progress-cursor disabled');  // disable inputs
    // $('.dhInput').removeAttr('disabled').removeClass('progress-cursor disabled');  // enable the inputs
    let recordNowValue = parseInt(recordsCounterProgressBar.attr("aria-valuenow"));

    let progressPercentage = ((recordNowValue / rowCount) * 100);
    // console.log(progressPercentage);
    //set the labels and width to progressbar

    if (progressPercentage <= 100) {
      recordsCounterProgressBar.children().text(progressPercentage.toFixed() + "%");
      recordsCounterProgressBar.css('width', progressPercentage + '%');
      recordsCounterProgressBar.attr("aria-valuenow", recordNowValue + 1);
    }
    currentRowCounter.text(recordNowValue + " Rows");

    if (isOk === true) {
      if (progVal <= rowCount) {
        progVal++;
        // console.log(progVal, ' of ', rowCount);

      } else {
        clearInterval(progressInterval);
        let i = 0;
        // check if there is columns
        if (typeof data['columns'] !== "undefined") {
          for (let [name, dType] of Object.entries(data['columns'])) {
            i++;

            let tmpMarkupLi = `
                      <li data-idx='${i}' class="columnItem list-group-item d-flex justify-content-between align-items-center cursor-pointer list-group-item-action noselect">
                                  ${i}. ${name.trim()}
                                  <span class="noselect">
                                  <span class="noselect label label-inline label-light-primary font-weight-bold w-60px">${getDataType(dType)}</span>


                             </span>
                              </li>
                          \n
                      `;
            tmpMarkupLi.replace(/ /g, "");
            optionsList += tmpMarkupLi;
          }
        }

        // console.log(optionsList);
        dataFileColumnsSelect.html(optionsList);
        $("#dataHandlerUploadProgressLabel").html("Upload Complete");
        rowCountProgressDialog.modal('hide');
        $("#uploadFileModal").modal('hide');
        enableDisableDhBtn("enable");

      }


    } else {
      // here in this else block, when records count more than the allowed
      if (progVal <= parseInt(allowdedRowsCount.text())) {
        progVal++;
        // console.log(progVal);
      } else {
        // clearInterval(progressInterval);
        $("#uploadFileModal").modal('hide');
        currentRowCounter.addClass("text-danger bg-danger-o-50 p-1");
        recordsCounterProgressBar.removeClass("bg-success");
        recordsCounterProgressBar.addClass("bg-danger-o-50");
        nextProgressBtnModal.fadeIn();
        $("#useSubPlanBtn").fadeIn();
        progressWarnText.fadeIn();


      }


    }


  }

  nextProgressBtnModal.on('click', function (ev) {
    clearInterval(progressInterval);
    rowCountProgressDialog.modal('hide');

    $("#extraRecordsModel").modal("show");
    $("#extraRecordsModel").modal("handleUpdate");
  });


}


// this function will return Numerice or String for the data type
function getDataType(dt) {
  // const dataTypeArray = ["", "object", "int64", "float64", 'bool', 'datetime64', 'category', 'timedelta'];
  if (dt === "int64" || dt === "float64") {
    return "Numeric";
  } else if ((dt === "object") || (dt === "category") || (dt === "bool")) {
    return "Text";
  } else {
    return "Alphanumeric";
  }
}

// this function will set the options list of the select to every column (item) in the right side
function dataTypeOptions(dataType, setSelected, uniqueColumn, colName) {
  let optionsMarkup = "";
  // this to set the selected option selected
  if ((typeof setSelected !== 'undefined' || setSelected === true) && (typeof uniqueColumn !== 'undefined') && (typeof colName !== 'undefined')) {
    // console.log(dataType, setSelected, uniqueColumn, colName);
    for (let dType of dataTypesOptions) {

      // check if isUniqueIDSelected is true make it selected by default, to avoid unique id enabled in the new items come from left side after selecte it
      if ((colName === uniqueColumn) && (dType.includes('Unique Identifier') === true)) {
        isUniqueIDSelected = true;
        optionsMarkup += `<option selected="selected" data-unique-id-col="1" value='${dType}'>${dType}</option>\n`;


      } else {
        // check to set selected if the column match the data type, so in this case make the option selected with the dtype
        if (dataType.toLowerCase() === dType.toLowerCase()) {
          // console.log(colName, '--> ', dataType.toLowerCase(), '==>  ', dType);
          optionsMarkup += `<option value='${dType}' selected="selected">${dType}</option>\n`;
        } else {
          optionsMarkup += `<option value='${dType}'>${dType}</option>\n`;
        }

      }

    }
    // return optionsMarkup;
  } else {
    for (let dType of dataTypesOptions) {

      // check if isUniqueIDSelected is true make it selected by default, to avoid unique id enabled in the new items come from left side after selecte it
      optionsMarkup += `<option value='${dType}'>${dType}</option>\n`;

    }
    // return optionsMarkup;
  }

  return optionsMarkup;

}

// when user click on reselect columns btn
function reselectColumnsFunc(openDialog) {
  $("#closeReselectColsModal").removeClass("d-none");
  let optionsList = '';
  let rightOptionsList = '';
  let dataFileColumnsSelect = $("#availableColumnsList");
  let rightPickedColumnsList = $("#pickedColumnsList");
  const columnsDualBoxModal = $("#columnsDualBoxModal");
  $("#closeColumnsDualBoxBtn").show();

  const allColumnsResponse = fetchDataFileAllColumns(true);


  $.when(allColumnsResponse).done(function (data, textStatus, jqXHR) {
    /*console.log(textStatus);
    console.log(jqXHR);
    console.log(data);*/
    // check if there is any data from data file of the user
    if (typeof data === 'object') {
      $("#noFileUploadedElement").hide();
      $("#data-handler-table-wrapper").show();
      const tmpSelectedColsArr = Object.keys(data['selected_columns']); // member selected columns
      let i = 0;
      for (let [name, dType] of Object.entries(data['all_columns'])) {
        i++;
        // console.log([name, dType]);
        let tmpMarkupLi = "";

        // console.log(getDataType(dType), dType);
        // check if the column name in the picked columns, so will disable it
        if (tmpSelectedColsArr.includes(name) === true) {
          tmpMarkupLi = `
                      <li data-idx = '${i}' class="disabled noselect bg-gray-200 columnItem list-group-item d-flex justify-content-between align-items-center cursor-pointer list-group-item-action" >
                                 ${i}. ${name.trim()}
                                 <span>
                                      <span class="noselect label label-inline label-light-primary font-weight-bold w-60px">${getDataType(dType)}</span>

                                 </span>
                              </li>
                          \n
                      `;
        } else {
          tmpMarkupLi = `
                      <li data-idx = '${i}' class="noselect columnItem list-group-item d-flex justify-content-between align-items-center cursor-pointer list-group-item-action" >
                                 ${i}. ${name.trim()}
                                 <span>
                                      <span class="noselect label label-inline label-light-primary font-weight-bold w-60px">${getDataType(dType)}</span>

                                 </span>
                              </li>
                          \n
                      `;
        }

        tmpMarkupLi.replace(/ /g, "");
        optionsList += tmpMarkupLi;

        // here set the columns options for the right side, which mean the previously selected columns
        let tmpRightColOpMarkup = "";
        if (tmpSelectedColsArr.includes(name) === true) {
          // this to set isUniqueIDSelected = true
          // console.log(getDataType(dType), true, data['unique_column'], name);  // Numeric true Donor_Id Donor_Id
          // console.log(data['selected_columns'][name]);
          tmpRightColOpMarkup = `
                      <li data-idx="${i}"
                          class='pickedItem list-group-item d-flex justify-content-between align-items-center cursor-pointer list-group-item-action'>
                          ${name}
                          <span class="nav-label mx-10" >
                              <select data-value='${getDataType(dType)}' class="form-control form-control-sm column-option-dtype w-110px">
                                      ${dataTypeOptions(data['selected_columns'][name], true, data['unique_column'], name)}
                              </select>
                          </span>
                          <span class="label position-absolute" style='background-color: unset; right: 12px; display: none;'>
                                <i class="icon-lg la la-info-circle text-warning font-weight-bolder"></i>
                          </span>
                          <span class="label position-absolute" style='background-color: unset; right: 12px; display: none;' id="resetIDColumnBtn" title="Reset ID column">
                                <i class="icon-lg la la-minus-circle text-danger font-weight-bolder"></i>
                          </span>

                      </li>
                      \n
                  `;

          rightOptionsList += tmpRightColOpMarkup;
        }

      }

      dataFileColumnsSelect.html(optionsList);
      rightPickedColumnsList.html(rightOptionsList);
      fixSelectedColumnsItems(rightPickedColumnsList);
      if (openDialog === true) {
        columnsDualBoxModal.modal("handleUpdate");
        columnsDualBoxModal.modal("show");
      }
    } else if (typeof data === 'string') {
      $("#noFileUploadedElement").show();
      $("#data-handler-table-wrapper").hide();
    }



  });

}

// this function will take the current item from right side to set the options of unique id column
function fixSelectedColumnsItems(allRightColsParent) {
  const allRightJQElement = $(allRightColsParent);
  allRightJQElement.children('li').each(function (index, element) {
    const liElem = $(element);
    const liSelectMenu = liElem.find('select.column-option-dtype');
    let opSelectUniqueIDCol = $(liSelectMenu.children('option[data-unique-id-col="1"]'));
    // liSelectMenu.attr('disabled', 'disabled');
    // console.log(liSelectMenu.val());
    liSelectMenu.trigger('change', 'reselect');
  })


}

// quick function to check if undefind
function checkUndefind(value) {
  console.log(typeof value === 'undefined');
}


// function will reset the data table to default sorting
function resetSorting() {
  $("#loadingDataSpinner").fadeIn();
  // let tableBody = document.getElementById("data_handler_body");
  // tableBody.innerHTML = "";
  let resetFetchRecoredsResponse = fetchDataFileRows();
  $.when(resetFetchRecoredsResponse).done(function (data, textStatus, jqXHR) {
    if (textStatus === "success") {
      $("#loadingDataSpinner").fadeOut(200);
      drawDataTableRows(data, false);
    } else {
      swAlert("Error", data, 'error');
    }
  });

}

// this function well return the array without duplicate
function removeDuplicates(originalArray, prop) {

  let newArray = [];
  let lookupObject = {};

  for (let i in originalArray) {
    lookupObject[originalArray[i][prop]] = originalArray[i];
  }

  for (let i in lookupObject) {
    newArray.push(lookupObject[i]);
  }
  return newArray;
}


var allNewRowsUpdates = {};
// var allNewRowsUpdates = [];
//setup before functions
var typingTimer, undoTimer; //timer identifier
var doneTypingInterval = 30000; //time in ms, 30 second for example
// var doneTypingInterval = 5000;  //time in ms, 30 second for example
var allEditedValues = new Array(); // this array will hold all inputs changed from the data handler table

// this function will run on change the input of the data file
function saveNewUpdatedData() {

  $('.data-table-col').each(function (key, value) {

    let elem = $(this);
    // allNewRowsUpdates["ROW_"+elem.data('row-id')] = Array();
    // console.log(allNewRowsUpdates);
    // throw new Error("Something went badly wrong!");
    // Save current value of element
    elem.data('oldVal', elem.val());

    // Look for changes in the value
    elem.bind("propertychange keyup input paste", function (event) {
      // console.log("propertychange event fire");
      // If value has changed...
      if (elem.data('oldVal') !== elem.val()) {
        // Updated stored value
        elem.data('oldVal', elem.val());
        // console.log(elem.data());
        clearTimeout(typingTimer);
        clearTimeout(undoTimer);
        undoTimer = setTimeout(function () {
          let prev = elem.data('undo-val');
          let current = elem.val();
          let rowItem = {};
          const rowID = "ROW_" + elem.data('row-id');
          rowItem[rowID] = {
            'oldValue': prev,
            'newValue': current,
            "rowElement": elem,
          };
          undoValuesObj.push(rowItem);
        }, 1000);
        typingTimer = setTimeout(function () {
          allEditedValues.push(elem);
          runSaveFunc();
        }, doneTypingInterval);


      }

    });

    elem.bind("keypress", function (event) {
      // console.log('keydown run')
      clearTimeout(typingTimer);
    });

    elem.bind("SaveUndoValueEvent", function (evt) {
      runSaveFunc($(this));
    });


  });

  $('.data-table-col').on("blur", function (event) {
    const currentInput = $(event.currentTarget);
    allEditedValues.push(currentInput);

  });


}

// this variables if there is any error when update cell in the table
var isErrorSave = false;
var errorMsgSave = "";

// this function will fire when timer run
function runSaveFunc() {
  $("#undoBtn").removeClass("disabled").addClass("text-primary font-weight-bolder");
  $("#undoBtn").removeAttr("disabled").removeAttr("style");
  // check if there is any items edited or updated by the user
  if (allEditedValues.length > 0) {
    for (let curElem of allEditedValues) {
      let rowNumTmp = "ROW_" + curElem.data('row-id');
      allNewRowsUpdates[rowNumTmp] = Array();
      let currentRowIdx = curElem.data('row-id');
      let currentColumnName = curElem.attr("name");
      let currentTableCellVal = curElem.val().trim();
      // check if the column exists or not
      let tmpData = {
        "colName": currentColumnName,
        "colValue": currentTableCellVal
      };
      allNewRowsUpdates[rowNumTmp].push(tmpData);
      // to remove duplicate column name
      let nonDuplicateValues = removeDuplicates(allNewRowsUpdates[rowNumTmp], 'colName');
      // console.log(nonDuplicateValues);
      allNewRowsUpdates[rowNumTmp] = nonDuplicateValues;
      // allNewRowsUpdates[rowNumTmp].push(nonDuplicateValues);
      // console.log(allNewRowsUpdates[rowNumTmp]);
      // console.log(allNewRowsUpdates);
      saveTheUpdates(allNewRowsUpdates, curElem);
    }
    if (isErrorSave === true) {
      showToastrNotification('Error while saving the data, please try again later!', "danger");
    } else {
      showToastrNotification('Data saved successfully!');
    }
  }


}

// this function will run every 1s in set time out when member update his data
function saveTheUpdates(allUpdatedRows, elem) {
  let currInput = $(elem);
  // console.log(allUpdatedRows);
  $("#dataListTable").css("opacity", "0.3");
  $(".data-table-col").attr("disabled", "disabled");
  $("#save-row-loader").fadeIn();
  let saveDataRespone = updateMemberDataFile(allUpdatedRows);
  $.when(saveDataRespone).done(function (data, textStatus, jqXHR) {
    if ((textStatus === "success") && (jqXHR.status === 200)) {
      undoValue = "";
      undoValue2 = "";
      // console.log(currInput.data());
      // console.log(data['msg']);
      if (data['is_error'] === true || data['msg'].includes("could not")) {
        currInput.addClass("is-invalid bg-light-danger", {
          duration: 1000
        });
        isErrorSave = true;
        errorMsgSave = "Error while saving the data, check the data type or try later!";
        // showToastrNotification("Error while saving the data, check the data type or try later!", "danger");
        // currInput.focus();

      } else {
        currInput.removeClass("is-invalid bg-light-danger", {
          duration: 1000
        }).addClass("bg-success-o-40", {
          duration: 1000
        });
        setTimeout(function () {
          currInput.removeClass("bg-success-o-40", {
            duration: 1000
          });
        }, 1500);
        // currInput.focus();
        // showToastrNotification(data['msg'][1]);
        isErrorSave = false;
        // console.log(errorMsgSave);
      }

      // allNewRowsUpdates = {};
      // console.log(currInput.data());
      $("#dataListTable").css("opacity", "1");
      $(".data-table-col").removeAttr("disabled");
      $("#save-row-loader").fadeOut();

      // currInput.focus();

    } else {
      swAlert("Error", "Error when save the data!", "error");
      showToastrNotification("Error when save the data!", "danger");

    }


  });
  // empty the newrowsupdate, and the updated inputs
  allNewRowsUpdates = {};
  allEditedValues = [];
}

// this function will run when member click on save button
function saveChangesFunc() {
  runSaveFunc();
}


// this function to save the old data to undo action
function saveUndo() {

  $(document).on('focusin', '.data-table-col', function (event) {
    // console.log("Saving value " + $(this).val());
    // undoValue = $(this).val();
    // console.log($(this).data());
    undoValue = undoValue2 = $(this).data('undo-val');
    undoElement = $(this);
    $(this).data('undo-val', $(this).val());
  }).on('change', '.data-table-col', function (event) {
    let prev = $(this).data('undo-val');
    let current = $(this).val();

    /*console.log("this is change event");
    console.log("Prev value " + prev);
    console.log("New value " + current);*/

  });
  //

}

// undo function
function undoFunc() {
  // undoElement.val(undoValue).trigger('propertychange');
  // check if the length of the undo array elements greater than 0
  if ((undoValuesObj === undefined) || (undoValuesObj.length === 0)) {
    $("#undoBtn").addClass("disabled").tooltip('hide').attr("disabled", "disabled").attr("style", "cursor: not-allowed;");

  } else {
    let lastUndoItem = undoValuesObj.pop();
    let lastUndoName = Object.keys(lastUndoItem)[0];
    let tmpLastJQ = $(lastUndoItem[lastUndoName]['rowElement']);
    tmpLastJQ.val(tmpLastJQ.data('undo-val'));
    // trigger when member clicked on undo to save the old value instead of the new value
    tmpLastJQ.trigger('SaveUndoValueEvent');

  }


  $("#saveDataFileBtn").removeClass("disabled").removeAttr("disabled style");
  // undoValue = "";

  // $(".data-table-input").on("change");
  // undoElement = null;
}

// function to display Toastr Notifications
function showToastrNotification(msg, msgType = "success") {
  let icon = "";
  if (msgType === "danger") {
    icon = "icon la la-times";
  } else {
    icon = "icon la la-check";
  }
  $.notify({
    // options
    message: msg,
    icon: icon,
    showProgressbar: true,
  }, {
    // settings
    type: msgType,
    animate: {
      enter: 'animate__animated animate__ animate__faster animate__slideInRight',
      exit: 'animate__animated animate__ animate__faster animate__slideOutRight'
    },
    z_index: 1031,
    timer: 1000,
  });

}

// function well set cookie if the member does not upload any data file yet, this cookie if it set, it will prevent the user from reload the page and disable f5 key
function setTheCookie() {
  let setTheCookieResponse = checkIfMemberUploadDataFile()
  $.when(setTheCookieResponse).done(function (data, textStatus, jqXHR) {
    // console.log(textStatus);
    // console.log(jqXHR.status);
    // console.log(data);

    if (data !== "None" && jqXHR.status === 200) {
      $(document).on("keydown", disableF5);
      window.onbeforeunload = function (e) {
        e = e || window.event;

        // For IE and Firefox prior to version 4
        if (e) {
          e.returnValue = 'Sure?';
        }

        // For Safari
        return 'Sure?';
      };
    } else {
      window.onbeforeunload = null;
    }
  });
}


// Restricts input for the given textbox to the given inputFilter function.
function isNumber(evt) {
  evt = (evt) ? evt : window.event;
  let charCode = (evt.which) ? evt.which : evt.keyCode;
  if (charCode > 31 && (charCode < 48 || charCode > 57)) {
    return false;
  }
  return true;
}

// this function will run after all page load and all ajax requests have complete, to check if the user has previous seesions or not
function checkMemberSessionStatus() {
  const checkMemberProcessStatusResponse = checkIfMemberProcessStatus();
  $.when(checkMemberProcessStatusResponse).done(function (data, textStatus, jqXHR) {
    // console.log(textStatus);
    // console.log(jqXHR);
    // console.log(data);
    if ((textStatus === 'success') && (jqXHR.status === 200) && (data === false)) {
      const swalWithBootstrapButtons = Swal.mixin({
        customClass: {
          confirmButton: 'btn btn-success',
          cancelButton: 'btn btn-danger'
        },
        buttonsStyling: false
      })

      swalWithBootstrapButtons.fire({
        title: 'Attention!',
        text: "There is previously session, do you want to restore it?",
        icon: 'warning',
        showCancelButton: true,
        confirmButtonText: 'Yes, restore it!',
        cancelButtonText: 'No, start fresh!',
        // reverseButtons: true,
        backdrop: true,
        allowOutsideClick: false,
        allowEscapeKey: false,
        allowEnterKey: false,
        showLoaderOnConfirm: true,
      }).then((result) => {
        if (result.value) {
          const newResponse = checkIfMemberProcessStatus("Restore");
        } else if (
          /* Read more about handling dismissals below */
          result.dismiss === Swal.DismissReason.cancel
        ) {
          const newResponse = checkIfMemberProcessStatus("Fresh");
        }
      })
    }
  });
}

// disable F5 Key
function disableF5(e) {
  if ((e.which || e.keyCode) === 116) e.preventDefault();
}

// function will calculate the numbers in payment table overview page
function calcPaymentOverview() {
  const abovePlanLimitRecord = $("#abovePlanLimitRecord");
  const additionalFeePerExtraRecord = $("#additionalFeePerExtraRecord");
  const totalCostForAdditionalRows = $("#totalCostForAdditionalRows");
  if ((typeof abovePlanLimitRecord.html() !== 'undefined') && (typeof additionalFeePerExtraRecord.html() !== 'undefined')) {
    const abovePlanValue = parseInt(abovePlanLimitRecord.html().trim());
    const additionValue = parseFloat(additionalFeePerExtraRecord.html().trim());
    const totalValue = additionValue * abovePlanValue;
    totalCostForAdditionalRows.html(`$${totalValue}`);
  }

}

// this function will handle the data handler wrapper tabs
/* function dataHandlerWrapperTabs() {
  //tabindex="-1", aria-disabled="true"

  let fetchLastSessionNameResponse = fetchLastSessionName();
  $.when(fetchLastSessionNameResponse).done(function (data, textStatus, jqXHR) {
    //  console.log(textStatus);
    // console.log(jqXHR);
    // console.log(data);
    if ((textStatus === 'success') && (jqXHR.status === 200)) {
      $("#data-handler-wrapper-spinner").fadeOut();
      $("#wrapper-ul").fadeIn();
      $("#wrapper-content").fadeIn();
      // This event fires on tab show, but before the new tab has been shown
      $('#wrapper-ul').on('show.bs.tab', function (event) {
        // do something...
        const ulElement = $(this);
        // ulElement.find('a[data-section-name="data_process"]').addClass('disabled');
        const previousActiveTab = $(event.relatedTarget);
        const previousSectionName = previousActiveTab.data('section-name');
        const activeTab = $(event.target);
        const activeSectionName = activeTab.data('section-name');

      });
    }
  })


} */

// this function will set the label of the data handler session
async function setSessionLabel() {
  let checkStatus = ''; // if the check label is false means no session in the db
  // first check if the current session has label or not


  if (!checkStatus) {
    const {
      value: sessionLabel
    } = await Swal.fire({
      title: 'Enter Label for current session',
      input: 'text',
      allowOutsideClick: false,
      allowEscapeKey: false,
      // inputValue: inputValue,
      showLoaderOnConfirm: true,
      showCancelButton: false,
      confirmButtonText: "Submit",
      inputValidator: (value) => {
        if (!value) {
          return 'You need to write something!'
        }
      }
    })

    if (sessionLabel) {
      let sessionLabelRespone = setSessionLabelRequest(sessionLabel);
      $.when(sessionLabelRespone).done(function (data, textStatus, jqXHR) {
        if ((jqXHR.status === 200) && (textStatus === 'success')) {
          document.title = sessionLabel;
          $("#data-handler-dashboard-label").text(sessionLabel);
          Swal.fire(data);
          window.location.href = webSiteUrl.concat("/profile/dashboard");
        }
      })
    }
  }

}


// delete single session from table
function deleteSingleSession() {
  $(".delete-data-session, #deleteAllSessionsBtn").on('click', function (evt) {
    const elem = $(this);
    const sessionID = elem.data('session-id');
    let deleteMsg = ""
    if (typeof sessionID === 'number') {
      deleteMsg = "Do you want to delete your session with its file, You won't be able to revert this!";
    } else {
      deleteMsg = "Do you want to delete all your sessions and files!, You won't be able to revert this!";
    }
    Swal.fire({
      title: 'Are you sure?',
      text: deleteMsg,
      icon: 'warning',
      showCancelButton: true,
      confirmButtonColor: '#3085d6',
      cancelButtonColor: '#d33',
      confirmButtonText: 'Yes, delete!',
      allowEnterKey: false,
    }).then((result) => {
      if (result.value) {
        const deleteSessionResponse = deleteDataSessionsRequest(sessionID);
        $.when(deleteSessionResponse).done(function (data, textStatus, jqXHR) {
          //  console.log(textStatus);
          // console.log(jqXHR);
          // console.log(data);
          if ((textStatus === 'success') && (jqXHR.status === 200)) {
            Swal.fire(
              'Deleted!',
              'Delete Successfully!.',
              'success'
            );
            setTimeout(function () {
              window.location.reload();
            }, 1000);
          }
        });

      }
    })


  })
}


// rename session function
function renameSessionFunc() {
  $("#rename-session-btn").on('click', function (evt) {
    const newSessionNameJq = $("#rename-session-input");
    if (newSessionNameJq.val() !== "") {
      const renameSessionResponse = renameSessionRequest(newSessionNameJq.val());
      $.when(renameSessionResponse).done(function (data, textStatus, jqXHR) {
        /* console.log(textStatus);
        console.log(jqXHR);
        console.log(data);*/
        if ((textStatus === 'success') && (jqXHR.status === 200)) {
          Swal.fire(
            'Updated!',
            'Rename Successfully!.',
            'success'
          );
          setTimeout(function () {
            window.location.reload();
          }, 1000);
        }
      });
    }


  });
}

// this function will run when member clear the search input and reset the previous results
function searchQueryResetView(elem) {
  const searchInput = $(elem);
  // clickedFilteredColName
  // isClickedFilterCol
  // check if search input is empty or cleared
  if (searchInput.val() === "") {
    isSearchMode = false; // to enable pagination nav btns
    $("#data-table-nav-parent").detach();
    $("#data-table-nav-wrapper").append(clonedNavBtns);
    clonedNavBtns = "";
    // check if the user was in not filtered columns or filtered column
    if ((isClickedFilterCol === true) && (clickedFilteredColName !== "")) {
      $("#loadingDataSpinner").fadeOut('fast');
      let notValidateRowsResponse = fetchNotValidateRows(clickedFilteredColName);
      $.when(notValidateRowsResponse).done(function (data, textStatus, jqXHR) {
        if ((textStatus == "success") && (jqXHR.status == 200)) {
          $("#data_handler_table > tbody tr").empty();
          drawDataTableRows(data, false);
        } else {
          swAlert("Error", data, 'error');
        }
      });
    } else {
      // clickedRecordsCount = clickedRecordsCount - 50;
      $("#loadingDataSpinner").fadeOut('fast');
      fetchRecordsByCount(clickedRecordsCount);
    }

  }
}

// this will run to initiate the data table
function initiateDataTable() {
  const sessionID = extractLastSessionID();
  if (Number.isInteger(sessionID) === true) {
    let fetchedColumns = fetchDataFileColumns(sessionID);
    $.when(fetchedColumns).done(function (data, textStatus, jqXHR) {
      // check if the data not equal "", this mean no columns
      if ((textStatus === 'success') && (jqXHR.status === 200)) {
        if (data !== "") {
          let sortedColumns = Array();
          let columnsLabels = data;
          for (let cl in data) {
            //unique identifier (id)
            if (data[cl] === "unique identifier (id)") {
              sortedColumns.push({
                "isUnique": true,
                "headerName": cl
              });
            } else {
              sortedColumns.push({
                "isUnique": false,
                "headerName": cl
              });
            }

          }
          // sortedColumns = sortedColumns.sort();
          //initialise columns for the data table
          setColumnNamesHeader(sortedColumns);
          //initialise (fetch) rows, fetch the rows to datatable
          let dataFileRows = fetchDataFileRows(25);
          $.when(dataFileRows).done(function (rowData, rowTextStatus, rowJqXHR) {

            //  console.log(rowData);
            // console.log(rowTextStatus);
            // console.log(rowJqXHR);

            // check if there is any returned data
            if ((rowTextStatus === 'success') && (rowJqXHR.status === 200)) {
              // first hide the spinner loding div
              $("#loadingDataSpinner").hide();
              let rowsObject = rowData;
              // console.log(rowsObject);
              drawDataTableRows(rowsObject, false);
            }


          });
        }
      }

    });

    // call pagination for data handler table
    dhPagination();
  }

}

function deleteAndReuploadDataFile() {

  // check if the session has id
  const sessionID = extractLastSessionID();
  // check the session if a number
  if (Number.isInteger(sessionID) === true) {
    // let ask = confirm("Are you sure?");
    Swal.fire({
      title: 'Attention!',
      text: "Are you sure?",
      icon: 'question',
      showCancelButton: true,
      confirmButtonColor: '#3085d6',
      cancelButtonColor: '#d33',
      confirmButtonText: 'Yes, delete!',
      allowOutsideClick: false,
      allowEscapeKey: false,
      allowEnterKey: false,
    }).then((result) => {
      if (result.isConfirmed) {
        const deleteDataFileResponse = deleteDataFile(sessionID);
        $.when(deleteDataFileResponse).done(function (data, textStatus, jqXHR) {

          if ((textStatus === "success") && (jqXHR.status === 200)) {
            swAlert("Please wait...", "Your data file has been deleted successfully!", "success");
            window.sessionStorage.clear();
            setTimeout(function () {
              location.reload();
            }, 1000);
            // $("#columnsDualBoxModal").modal("hide");
          } else {
            swAlert("Error", "Error when delete the data file!", "error");
          }

        });
      }
    });


  }
}

// upload data file function
function uploadDataFileFunction(formInputEle) {
  // disable all inputs while uploading
  let donorFileuploadFormRequest = uploadDonorDataFile($(formInputEle));
  $(".dhInputs").addClass("progress-cursor").attr('disabled', "disabled");
  $.when(donorFileuploadFormRequest).done(function (data, textStatus, jqXHR) {

    if ((textStatus === "success") && (jqXHR.status === 200)) {

      if (typeof data === "object") {
        if (data['is_allowed'] === true) {
          // this mean the records total more than the allowed in subscription plan
          uploadProgressModal(true, data);
          $("#dhWizardDeleteBtn").show();


        } else if (data['is_allowed'] === false) {
          if (data['row_count'] === 0) {
            // this mean no row count, which means the donor id column not exists
            swAlert("attention!!".toUpperCase(), `${data['msg']}`, 'error');

          } else {
            uploadProgressModal(true, data);
            $("#dhWizardDeleteBtn").show();
          }


        } else if ((data['is_allowed'] === false) && (data['is_empty'] === true)) {
          // this mean no row count, which means the donor id column not exists
          swAlert("attention!!".toUpperCase(), `${data['msg']}`, 'error');
        }


      }

    } else {
      // in case the user upload wrong file type
      swAlert("Error!", 'There is error while uploading the data file, please try again later', "error");
    }


  });

  $("#uploadDataFileBtn, #uploadDataFileForm, #instruction-check-btn, #downloadTemplateLink").addClass("disabled").attr("disabled", 'disabled');

  // reload overview data table
  callDataHandlerTableFunc();
}


// function to handle hide and show datahandler wizard button
function handleDataHandlerWizardBtn() {
  const wizardBtn = $("#dataHandlerWizardBtn");
  // check if the session has id
  const sessionID = extractLastSessionID();
  if (Number.isInteger(sessionID) === true) {
    const fetchSessionRequest = fetchDataSessionInfo(sessionID);
    $.when(fetchSessionRequest).done(function (data, textStatus, jqXHR) {
      if ((textStatus === "success") && (jqXHR.status === 200)) {

        // check if the data is not null
        if (data['data'] !== null) {
          let isProcessComplete = data['data']['is_process_complete'];
          let currentSessionName = data['data']['current_session_name'];
          let isValidateData = data['data']['is_validate_data'];
          wizardBtn.html('Next');
          wizardBtn.removeAttr('disabled').removeClass('disabled not-allowed');
          // check if is process is completed
          /* if (isProcessComplete === true) {
            wizardBtn.removeAttr('disabled').removeClass('disabled not-allowed');
          } */

        } else {
          // if the data is null
        }

      } else {
        swAlert("Error", data, 'error');
      }
    });
  }


}


// this function will call to chekc if the data is validated
function checkValidatedData() {
  const checkRequest = checkValidDataRequest();
  $.when(checkRequest).done(function (data, textStatus, jqXHR) {
    if ((textStatus === "success") && (jqXHR.status === 200)) {
      const validateDataAlert = $("#validateDataAlert");
      const notValidateDataAlert = $("#notValidateDataAlert");
      if (data['status'] === true) {
        validateDataAlert.show();
        notValidateDataAlert.hide();
      } else {
        notValidateDataAlert.show();
        validateDataAlert.hide();
      }
    } else {
      swAlert("Error", data, "error");
    }

  });
}


// this function will send ajax request with the selected columns
function sendSelectedColumns() {
  selectedPickedColumns = _.uniq(selectedPickedColumns); // to avoid duplicate columns name
  // console.log(selectedPickedColumns);
  // throw new Error("Something went badly wrong!");
  let selectedColumnsRequest = sendPickedColumns();
  $.when(selectedColumnsRequest).done(function (data, textStatus, jqXHR) {

    if ((textStatus === "success") && (jqXHR.status === 200)) { // change the condition
      setSessionLastName("data_process");
      initiateDataTable();
    } else {
      swAlert("Error", data, "error");
    }

  });
}


// this function will fire when user click on execute model button
function executePredictiveModel() {
  // request to check if the user allowed to run the model
  const checkRecordNumberRequest = checkIfUserAllowedRecordNumber();
  $.when(checkRecordNumberRequest).done(function (data, textStatus, jqXHR) {

    if ((textStatus === "success") && (jqXHR.status === 200)) {
      if (data['records'] > 0) {
        // check if the user use more than allowed records, show him extra records modal
        $("#extraRecordsModel").modal("show");
        $("#extraRecordsModel").modal("handleUpdate");

      } else {
        // here if the user records usage allowed
        if (data['isValidate'] === true) {
          (async () => {
            const {
              value: sessionName
            } = await Swal.fire({
              customClass: {
                confirmButton: 'btn btn-primary font-weight-bolder',
                cancelButton: 'btn btn-light-danger font-weight-bolder'
              },
              buttonsStyling: false,
              title: 'Donor Predictions Model Name',
              width: 500,
              showCancelButton: true,
              input: 'text',
              // inputLabel: '',
              // inputPlaceholder: 'Session',
              confirmButtonText: 'Save and Execute Model',
              cancelButtonText: "Cancel and Return",
              allowOutsideClick: false,
              allowEscapeKey: false,
              allowEnterKey: false,
              inputValidator: (value) => {
                if (!value) {
                  return 'You need to write name!';
                }
              },
            });

            if (sessionName) {
              const setSessionNameRequest = setSessionLabelRequest(sessionName);
              $.when(setSessionNameRequest).done(function (data, textStatus, jqXHR) {

                if ((textStatus === "success") && (jqXHR.status === 200)) { // change the condition
                  runSocket();
                } else {
                  swAlert("Error", data, "error");
                }

              });
            }
          })()

        } else {
          // here if the data not valid
          Swal.fire(
            'Error',
            'You have to validate your data first!',
            'error'
          )
        }

      } // end of else
    } else {
      swAlert("Error", data, "error");
    }

  });
}


// this function will be in the interval to call the setDataHandlerTableOverview function
function callDataHandlerTableFunc() {
  setDataHandlerTableOverview();

  // const timeout = setTimeout(callDataHandlerTableFunc, 5000);

}

// this function will send a request to integrate the table overview in data handler section
async function setDataHandlerTableOverview() {
  try {
    const tableOverviewOverlay = $(".tableOverviewOverlay");
    // show table overlay layer
    tableOverviewOverlay.fadeIn();
    const dataTableRequest = await fetchDataForDataTable();
    const dhTdParentTableOverview = $(".dhTdParentTableOverview");
    const dhPlanName = $(".dhPlanName");
    const dhPlanLimit = $(".dhPlanLimit");
    const dhCurrentDataUsed = $(".dhCurrentDataUsed");
    const dhAtOrBelowPlanLimit = $(".dhAtOrBelowPlanLimit");
    const dhAbovePlanLimitRecord = $(".dhAbovePlanLimitRecord");
    const dhAdditionalFeePerExtraRecord = $('.dhAdditionalFeePerExtraRecord');
    const dhTotalCostForAdditionalRows = $(".dhTotalCostForAdditionalRows");
    // check the status code, or the connection is successfully
    if (dataTableRequest.status === 200) {
      const data = dataTableRequest.data;
      dhPlanName.html('').html(data['plan_name']);
      dhPlanLimit.html('').html(data['plan_limit']);
      dhCurrentDataUsed.html('').html(data['current_data_used']);
      // check if the records total above or below the plan limit
      if (data['check_records_total'] === true) {
        dhTdParentTableOverview.removeClass('bg-primary-o-50').addClass("bg-danger-o-50");
      } else {
        dhTdParentTableOverview.removeClass('bg-danger-o-50').addClass("bg-primary-o-50");
      }
      dhAtOrBelowPlanLimit.html('').html(data['at_or_below_plan_limit']);
      dhAbovePlanLimitRecord.html('').html(data["above_plan_rows"]);
      dhAdditionalFeePerExtraRecord.html('').html(data['additional_fee']);
      dhTotalCostForAdditionalRows.html('').html(data['total_cost_for_additional']);

      // hide the table overlay layer
      tableOverviewOverlay.fadeOut();

    } else {
      // this else if there error in the connection
      console.error('Error When fetch data for data table overview!');
      console.error(dataTableRequest.status);
    }
  } catch (error) {
    if (error instanceof TypeError) {
      setDataHandlerTableOverview();
      console.info('Error in connection!!, please wait...');
    } else {
      console.error(error);
    }
  }
}


// this function to make the pagination for data handler table
function dhPagination() {
  // TODO: Fix the pages numbers
  const paginationRequest = sendRequests('/dashboard/data/api/get-table-pagination', 'Pagination Request');
  $.when(paginationRequest).done(function (data, textStatus, jqXHR) {

    // check if there is any returned data
    if ((textStatus === 'success') && (jqXHR.status === 200)) {
      const results = data['data'];
      const pagesItems = [];
      // console.log(results);
      const dhTablePaginationWrapper = $("#dhTablePaginationWrapper");
      // const previousBtn = dhTablePaginationWrapper.find("#previousBtn");
      // const nextBtn = dhTablePaginationWrapper.find("#nextBtn");
      const paginationTotalResults = $("#paginationTotalResults");
      paginationTotalResults.html(results['total_records']);

      // loop through pages and create pages items
      for (let page = 1; page <= results['total_pages']; page++) {
        const element = page;
        // console.log(object);
        const htmlElement = `<a class="btn btn-icon btn-sm border-0 btn-light btn-hover-primary mr-2 my-1 data-table-nav-btns not-allowed-cursor disabled" disabled='disabled'>${page}</a>`.trim();
        pagesItems.push(htmlElement);
      }
      // $(pagesItems.toString()).insertAfter(previousBtn);  // insert the pages number to ui

    }


  });
}


// this function will download new updated data file
function downloadUpdatedDataFile(btn) {
  const clickedBtn = $(btn);
  const fileType = clickedBtn.data("type");
  const exportRequest = downloadUpdatedFileRequest(fileType);
  $.when(exportRequest).done(function (data, textStatus, jqXHR) {

    // check if there is any returned data
    if ((textStatus === 'success') && (jqXHR.status === 200)) {
      let fileExt = '';
      // check what type of file to set the ext
      if (data['type'] === "text/csv") {
        fileExt = ".csv"
      } else {
        fileExt = ".xlsx";
      }
      const today = new Date();
      const fullFileName = "PredictME_" + today.getFullYear() + '-' + (today.getMonth() + 1) + '-' + today.getDate() + fileExt;
      let link = document.createElement('a');
      link.download = fullFileName;

      link.href = URL.createObjectURL(data);
      link.click();

      URL.revokeObjectURL(link.href);
    }


  });
}


// this function will enable and disable data handler navigation button
function enableDisableDhBtn(status) {
  const btn = $("#dataHandlerWizardBtn");
  if (status === 'disable') {
    btn.attr("disabled", 'disabled').addClass("not-allowed-cursor disabled pointer-event-none").removeClass('pointer-event-all');
  } else if (status === 'enable') {
    btn.removeAttr("disabled").removeClass("not-allowed-cursor disabled pointer-event-none").addClass('pointer-event-all');
  }
}