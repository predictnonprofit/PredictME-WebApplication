let undoValue = ""; // the undo value
let undoValue2 = ""; // the undo value which will save when save button clicked
let undoElement = null; // the undo input element
let isDownloaded = false; // if true mean the member download the data template
let acceptDownloadObj = {};
$(function () {

  // enable upload btn by check agree terms and conditions
  const agreeDataHandlerCheckBox = $("#agreeDataHandlerCheckBox");
  const dataUploadBtn = $("#dataUploadBtn");
  agreeDataHandlerCheckBox.on("change", function () {
    if (this.checked) {
      dataUploadBtn.removeAttr("disabled");
      dataUploadBtn.removeClass("my-disabled-btn");
      $("#semitransparent").addClass("d-none");

      $("#donerFile").removeAttr("disabled not-allowed-cursor");
    } else {
      dataUploadBtn.attr("disabled", "disabled");
      $("#semitransparent").removeClass("d-none");
      $("#donerFile").attr("disabled", "disabled").addClass('not-allowed-cursor');
    }
  });

  // enable the check button on the instruction modal
  let validateObj = {
    agree: false,
  };
  const instructionsCheckButtons = $("#instruction-check-btn");
  instructionsCheckButtons.on("change", function (evt) {
    let checkedDataVal = $(this).data("action");
    if ($(this).is(":checked")) {
      // $('#downloadTemplateLink').show();
      validateObj[checkedDataVal] = true;
    } else {
      validateObj[checkedDataVal] = false;
    }

    // if two checked enable download button
    if (validateObj["agree"] === true) {
      $("#downloadTemplateLink")
        .removeClass("disabled not-allowed-cursor btn-outline-success")
        .addClass("btn-success");
      $("#downloadTemplateLink").attr("href", "/profile/download");
    } else {
      $("#downloadTemplateLink")
        .addClass("disabled not-allowed-cursor btn-outline-success")
        .removeClass("btn-success");
      $("#downloadTemplateLink").removeAttr("href");
    }
  });

  // this for disable the upload button when user not accept the terms from the modal dialog
  let closeUploadInstBtn = $("#closeUploadInstBtn");
  let acceptUploadInstBtn = $("#acceptUploadInstBtn");
  let downloadTemplateLink = $("#downloadTemplateLink");

  downloadTemplateLink.on("click", function (evt) {
    // check if the download button is disabled or not
    if ($(this).hasClass("disabled") === false) {
      isDownloaded = true;

      // check if the two options checked enable the check button in the modal
      $("#acceptUploadInstBtn")
        .removeClass("disabled notAllowedCur")
        .removeAttr("disabled");
      $("#donerFile")
        .removeClass("disabled not-allowed-cursor")
        .removeAttr("disabled");
      $("#uploadDataFileBtn")
        .removeClass("disabled notAllowedCur")
        .removeAttr("disabled");
      $("#acceptsCheckMark").replaceWith(
        '<i class="icon-lg text-success la la-check-double" id="acceptsCheckMark"></i>'
      );
      $("#session-name").removeAttr("disabled").removeClass("disabled");
      $("#instruction-check-btn")
        .attr("disabled", "disabled")
        .addClass("disabled");
      $("#fileUploadOverlay").fadeOut('slow').css({
        "background-color": "rgba(27, 197, 189, 0.12)"
      }).fadeIn('slow').delay(2000).fadeOut();
    }
  });

  // accept upload instruction terms button
  acceptUploadInstBtn.click(function (e) {
    $("#semitransparent").toggleClass("d-none");
    $("#donerFile").removeAttr("disabled").removeClass('not-allowed-cursor');
    dataUploadBtn.removeAttr("disabled");
    agreeDataHandlerCheckBox.prop("checked", true);
    $("#instruction-check-btn").on("change", function (evt) {
      if ($(this).is(":checked")) {
        acceptDownloadObj["is_accept_terms"] = true;
        /* if (elem.data('action') === "download") {
            acceptDownloadObj['is_accept_download_template'] = true;
        } */
      }
    });
    acceptDownloadObj["is_download_template"] = isDownloaded;

    const acceptDownloadResponse = saveMemberAccepts(acceptDownloadObj);
    $.when(acceptDownloadResponse).done(function (data, textStatus, jqXHR) {
      if (textStatus === "success" && jqXHR.status === 200) {
        // console.log(data);
      } else {
        swAlert("Error", data, "error");
      }
    });
  });

  // not accept upload instruction terms button
  closeUploadInstBtn.click(function (e) {
    // check if agree upload terms checkbox checked or not
    if (
      agreeDataHandlerCheckBox.prop("checked") === false ||
      agreeDataHandlerCheckBox.prop("checked") === true
    ) {
      agreeDataHandlerCheckBox.prop("checked", false);
      dataUploadBtn.prop("disabled", true);
    }
    $("#downloadTemplateLink")
      .addClass("disabled not-allowed-cursor btn-outline-success")
      .removeClass("btn-success");
    $("#downloadTemplateLink").removeAttr("href");
  });

  // this for the next button when user click next in pay or upgrade subscription dialog
  // all forms sections vars
  const askPayUpgradeSection = $("#askPayUpgradeSection");
  const payExtraRecordsSection = $("#payExtraRecordsSection");
  const upgradeSubscriptionSection = $("#upgradeSubscriptionSection");
  const closeUpgradeModalBtn = $("#closeUpgradeModalBtn");
  let currentShownSection = "";


  // when member want to close the dialog
  closeUpgradeModalBtn.on("click", function () {
    Swal.fire({
      title: "Are you sure?",
      text: "You want to abort this operation?",
      icon: "warning",
      showCancelButton: true,
      allowOutsideClick: false,
      cancelButtonText: "No",
      confirmButtonColor: "#3085d6",
      cancelButtonColor: "#d33",
      confirmButtonText: "Yes",
    }).then((result) => {
      if (result.value) {
        $("#extraRecordsModel").modal("hide");
      }
    });
  });


  // upload data file functionality
  const uploadDataFileBtn = $("#uploadDataFileBtn");
  const uploadDataFileForm = $("#uploadDataFileForm");

  uploadDataFileForm.submit(function (e) {
    e.preventDefault();
    uploadDataFileFunction(this);
  });

  const donerFile = $("#donerFile");
  donerFile.on("change", function (event) {
    $("#uploadDataFileForm").trigger("submit");
  });

  const deleteTheProcessDataHandlerBtn = $(".deleteTheProcessDataHandlerBtn, #dhWizardDeleteBtn");
  deleteTheProcessDataHandlerBtn.on("click", (event) => {
    deleteAndReuploadDataFile();
  });

  // check if the data is valid
  checkValidatedData();

  // here when the user click on execute the model
  const execModelBtn = $("#executeModelBtn");
  // execModelBtn.on("click", (event) => {
  //   // executePredictiveModel();
  //   confirmRunModal();
  // });

  // here to trigger the event when member search in data handler table
  let typingTimer; //timer identifier
  let doneTypingInterval = 1000; //time in ms, 5 second for example
  let $input = $("#searchQuery");

  //on keyup, start the countdown
  $input.on("keyup", function (event) {
    clearTimeout(typingTimer);
    typingTimer = setTimeout(doneTyping, doneTypingInterval);
  });

  //on keydown, clear the countdown
  $input.on("keydown", function () {
    clearTimeout(typingTimer);
  });

  function doneTyping() {
    const searchQueryValue = $("#searchQuery");
    let searchQuery = searchQueryValue.val().trim();
    if (searchQuery !== "") {
      // clone the nav btns to detch them and re-insert them after clean search query with the same previous settings
      clonedNavBtns = $("#data-table-nav-parent").clone(true, true);
      isSearchMode = true;
      fetchRecordsBySearchQuery(searchQuery);
      $("#loadingDataSpinner").fadeOut();
      $(".data-table-nav-btns")
        .attr("disabled", "disabled")
        .addClass("disabled");
      $("#undoBtn")
        .addClass("disabled")
        .tooltip("hide")
        .attr("disabled", "disabled");
    }
  }

  // this function to set the data table overview data
  callDataHandlerTableFunc();

  // run model btn
  const runModelBtnWizard = $("#runModelBtnWizard");
  runModelBtnWizard.on("click", async (event) => {
    // check if the user allowed to run the model, or cress the limit of membership
    const isAllowedRunModel = $("#isAllowedRunModel");
    const checkSessionDtypesRequest = await checkSessionDtypesValid();
    // check if the data is valid then he can run the Model
    if (checkSessionDtypesRequest['is_validate_data'] === false) {
      swAlert('Error', "Please fix the data!", "error");
    } else {
      // if the data is valid
      const isAllowedRequest = await checkIsAllowedToRunModel();
      // const isAllowedRequest = {"is_allowed": true};
      // console.log("isAllowedRequest -> ", isAllowedRequest);
      if (isAllowedRequest['is_allowed'] === false) {
        // set the extra records model input values
        const extraRowsPurchased = $("#extraRowsPurchased");

        $("#extraRecordsModel").modal("show");
        $("#extraRecordsModel").modal("handleUpdate");
      } else if (isAllowedRequest['is_allowed'] === true) {
        executePredictiveModel();
      }
    }

  });

  // export updated data file btns
  const exportUpdatedDataBtns = $(".export-data-file-btn");
  exportUpdatedDataBtns.on("click", (event) => {
    event.preventDefault();
    downloadUpdatedDataFile(event.target);
  });

  // upgrade membership buttons in extraRecordsModel modal
  const upgradeMembershipsBtns = $('.upgrade-membership-extra-modal-btn');
  upgradeMembershipsBtns.on("click", (event) => {
    const btn = $(event.currentTarget);
    const newMembership = btn.data('membership');
    alert(`You will upgrade to -> ${newMembership} <- membership`);
  });


}); // end of $(function)

// show new stripe card input
const newStripeCardBtn = $("#newStripeCardBtn");
const newStripeInput = $("#newStripeInput");
newStripeCardBtn.click(function (e) {
  newStripeInput.fadeIn();
});

$(document).ready(function () {
  // setTheCookie();
  // stripeElementsFormDataHandler();

  // save button when member click on save button after click on undo button
  let saveDataFileBtn = $("#saveDataFileBtn");
  saveDataFileBtn.click(function (e) {
    e.preventDefault();
    // this when save button clicked after undo
    $("#dataListTable").css("opacity", "0.3");
    $(".data-table-col").attr("disabled", "disabled");
    $("#save-row-loader").fadeIn();
    // console.log(undoElement.data());
    let clonedNewRowsUpdates = allNewRowsUpdates;
    // console.log(clonedNewRowsUpdates);
    for (let row in clonedNewRowsUpdates) {
      clonedNewRowsUpdates[row]["colValue"] = undoElement.data("undo-val");
      // console.log(undoElement.data());
      // console.log(allNewRowsUpdates[row]);
      // console.log(clonedNewRowsUpdates[row]);
    }

    // throw new Error("Tess");
    let saveDataRespone = updateMemberDataFile(clonedNewRowsUpdates);
    $.when(saveDataRespone).done(function (data, textStatus, jqXHR) {
      // console.log(textStatus);
      // console.log(jqXHR);
      console.log(data);

      if (textStatus === "success" && jqXHR.status === 200) {
        showToastrNotification("Saved successfully");
        $("#save-row-loader").fadeOut();
        $("#dataListTable").css("opacity", "1");
        $(".data-table-col").removeAttr("disabled");
        saveDataFileBtn.addClass("disabled").tooltip("hide");
        saveDataFileBtn.attr("disabled", "disabled");
        saveDataFileBtn.attr("style", "cursor: not-allowed");
        $("#undoBtn")
          .addClass("disabled")
          .tooltip("hide")
          .attr("disabled", "disabled");

        // window.location.reload();
      } else {
        showToastrNotification("Error while saving the data!", "danger");
      }
    });
  });

  // when I want to delete the data file
  let deleteDataFileBtn = $("#deleteDataFileBtn");
  deleteDataFileBtn.click(function (e) {
    e.preventDefault();
    let conBox = confirm("Do you want to delete the data file!!");
    if (conBox === true) {
      let deleteDataFileResponse = deleteDataFile();
      $.when(deleteDataFileResponse).done(function (data, textStatus, jqXHR) {
        // console.log(textStatus);
        // console.log(jqXHR);
        // console.log(data);

        if (textStatus === "success") {
          swAlert(
            "Success",
            "Your data file has been deleted successfully!",
            "success"
          );
          // window.location.reload();
          window.location.href = window.location.origin + "/profile/data/";
        } else {
          swAlert("Error", "Error when delete the data file!", "error");
        }
      });
    }
  });

  let cancelReuploadBtn = $("#cancelReuploadBtn");
  cancelReuploadBtn.on("click", function (evt) {
    deleteAndReuploadDataFile();
  });

  const reselectColumnsBtn = $("#reselectColumnsBtn");
  reselectColumnsBtn.on("click", function (e) {
    e.preventDefault();
    $('[data-toggle="tooltip"]').tooltip("dispose");
    reselectColumnsFunc(true);
  });

  const resetSortTableBtn = $("#resetSortTableBtn");
  resetSortTableBtn.on("click", function () {
    $("#data_handler_table > tbody tr").empty();
    resetSorting();
    $("#searchQuery").val(""); // empty search query
    $(this).addClass("disabled");
    $(this).attr("disabled", "disabled");
    $(this).attr("style", "cursor: not-allowed;");
    isClickedFilterCol = false;
    isSearchMode = false;
    clickedRecordsCount = 25;
    lastRowCountTotal = 0;
    clickedFilteredColName = "";
    clonedNavBtns = "";
    $("#no-data-watermark").hide();
    $("[data-action='first']")
      .attr("disabled", "disabled")
      .addClass("disabled")
      .tooltip("hide");
    $("[data-action='previous']")
      .attr("disabled", "disabled")
      .addClass("disabled")
      .tooltip("hide");
    // check the length of the used rows if less than 50 disable all pagination buttons by default
    if ($("#records-count-alert").find("b").first().text() <= 50) {
      $("[data-action='next']")
        .attr("disabled", "disabled")
        .addClass("disabled")
        .tooltip("hide");
      $("[data-action='last']")
        .attr("disabled", "disabled")
        .addClass("disabled")
        .tooltip("hide");
    } else {
      $("[data-action='next']")
        .removeAttr("disabled")
        .removeClass("disabled")
        .tooltip("update");
      $("[data-action='last']")
        .removeAttr("disabled")
        .removeClass("disabled")
        .tooltip("update");
    }

    $("#undoBtn")
      .attr("disabled", "disabled")
      .addClass("disabled")
      .tooltip("hide");
  });

  const showRecordsSumSelect = $("#showRecordsSumSelect");
  // data handler pagination section pagination
  const dataTableNavBtns = $(".data-table-nav-btns");
  dataTableNavBtns.on("click", function (evt) {
    // TODO: Fix the pagination functions
    // console.log(clickedRecordsCount);  // initiate value to clicked records Count is 25
    $("#data_handler_table > tbody tr").empty();
    $("#resetSortTableBtn").removeClass("disabled");
    $("#resetSortTableBtn").removeAttr("disabled style");

    const selectedRecCount = $(this).val();
    const theAction = $(this).data("action");
    if (theAction === "next") {
      clickedRecordsCount += 25;
      // console.log('in on click event:-> ', clickedRecordsCount);
      let checkLastPageResponse = fetchDataFileRows(clickedRecordsCount);
      $.when(checkLastPageResponse).done(function (data, textStatus, jqXHR) {
        if (textStatus === "success" && jqXHR.status === 200) {
          if (
            (typeof data["data"] === undefined) ||
            (typeof data["data"] === "undefined")
          ) {
            $("[data-action='next']")
              .attr("disabled", "disabled")
              .addClass("disabled")
              .tooltip("hide");
            $("[data-action='last']")
              .attr("disabled", "disabled")
              .addClass("disabled")
              .tooltip("hide");
            $("[data-action='first']")
              .removeAttr("disabled")
              .removeClass("disabled")
              .tooltip("update");
          } else {
            // console.log(parseInt(perPage + data.total_rows));
            let perPage = parseInt($("#paginationPerPage").text());
            $("#paginationPerPage").html(parseInt(perPage + data.total_rows));
            fetchRecordsByCount(clickedRecordsCount);
          }
        }
      });
    } else if (theAction === "previous") {

      if (clickedRecordsCount !== 25) {
        clickedRecordsCount = clickedRecordsCount - 25;
        // check if the next indicator ">" is disabled because the member was in the last page, enable it
        if ($("[data-action='next']").is(":disabled") === true) {
          $("[data-action='next']")
            .removeAttr("disabled")
            .removeClass("disabled")
            .tooltip("update");
          $("[data-action='last']")
            .removeAttr("disabled")
            .removeClass("disabled")
            .tooltip("update");
        }
        $("#paginationPerPage").html(parseInt(clickedRecordsCount));
        fetchRecordsByCount(clickedRecordsCount);
      }
      // let perPage = parseInt($("#paginationPerPage").text());
      // $("#paginationPerPage").html(parseInt(perPage - data.total_rows));
    } else if (theAction === "first") {
      // when member click on first page
      clickedRecordsCount = 25;
      $("[data-action='previous']")
        .attr("disabled", "disabled")
        .addClass("disabled");
      $(this).tooltip("hide").attr("disabled", "disabled").addClass("disabled");
      $("[data-action='next']")
        .tooltip("update")
        .removeAttr("disabled")
        .removeClass("disabled");
      $("[data-action='last']")
        .tooltip("update")
        .removeAttr("disabled")
        .removeClass("disabled");
      $("#paginationPerPage").html(0);

      fetchRecordsByCount(clickedRecordsCount);

    } else if (theAction === "last") {
      // when member click on last btn
      const fetchLastInfoRequest = fetchDhTableLastPageInfo();
      $.when(fetchLastInfoRequest).done(function (data, textStatus, jqXHR) {
        if ((textStatus === "success") && (jqXHR.status === 200)) {
          clickedRecordsCount = parseInt(data['last_page_content']);
          // clickedRecordsCount = parseInt(data['last_page_content']) - 25;
          // console.log('clickedRecordsCount ', clickedRecordsCount);
          // code when connection success
          const oldVal = parseInt($("#paginationPerPage").html());
          $("#paginationPerPage").html(parseInt(data['last_page_content']));
          $("[data-action='next']")
            .attr("disabled", "disabled")
            .addClass("disabled")
            .tooltip("hide");
          $("[data-action='last']")
            .attr("disabled", "disabled")
            .addClass("disabled")
            .tooltip("hide");
          $("[data-action='first']")
            .removeAttr("disabled")
            .removeClass("disabled")
            .tooltip("update");
          // $(this).tooltip("hide").attr("disabled", "disabled").addClass("disabled");
          // $("#loadingDataSpinner").fadeOut("fast");
          fetchRecordsByCount(clickedRecordsCount, true);

        } else {
          // code when connection error
          console.error("Error msg");
        }
      });


    }

    if (clickedFilteredColName !== "") {
      let notValidateRowsResponse = fetchNotValidateRows(
        clickedFilteredColName
      );
      $.when(notValidateRowsResponse).done(function (data, textStatus, jqXHR) {
        if (textStatus == "success" && jqXHR.status == 200) {
          $("#loadingDataSpinner").fadeOut();
          drawDataTableRows(data, false);
        } else {
          swAlert("Error", data, "error");
        }
      });
    }
    /* else {
      // this block cause the last page dh table issue
      $("#loadingDataSpinner").fadeOut("fast");
      console.log('in here in else block');
      fetchRecordsByCount(clickedRecordsCount);
      console.log(clickedRecordsCount);
    } */
  });

  const searchDataTableBtn = $("#searchDataTableBtn");
  searchDataTableBtn.on("click", function (evt) {
    const searchQueryValue = $("#searchQuery");
    let searchQuery = searchQueryValue.val().trim();
    if (searchQuery !== "") {
      // clone the nav btns to detch them and re-insert them after clean search query with the same previous settings
      clonedNavBtns = $("#data-table-nav-parent").clone(true, true);
      isSearchMode = true;
      fetchRecordsBySearchQuery(searchQuery);
      $("#loadingDataSpinner").fadeOut();
      $(".data-table-nav-btns")
        .attr("disabled", "disabled")
        .addClass("disabled");
      $("#undoBtn")
        .addClass("disabled")
        .tooltip("hide")
        .attr("disabled", "disabled");
    }
  });

  const searchQueryInput = $("#searchQuery");
  searchQueryInput.on("search", function (event) {
    searchQueryResetView(this);
    return false;
  });

  // data table search form onsubmit
  const searchForm = $("#data-table-search-form");
  searchForm.on("submit", function (event) {
    $("#searchDataTableBtn").trigger("click");
    return false;
  });

  // save changes btn
  const saveChangesBtn = $("#save-data-table-changes-btn");
  const saveChangesBtn2 = $("#save-data-table-changes-btn2");
  saveChangesBtn.on("click", function (event) {
    saveChangesFunc();
  });
  saveChangesBtn2.on("click", function (event) {
    saveChangesFunc();
  });

  // the undo button
  const undoBtn = $("#undoBtn");
  undoBtn.on("click", undoFunc);
  // save the old value to make undo
  saveUndo();

  // data handler wrapper function
  // dataHandlerWrapperTabs();

  // this to reset upload checkbox when closed
  $("#instructionsModal").on("show.bs.modal", function () {
    let instructionInputs = $("#instruction-check-btn");
    // this to reset the check boxes in upload instruction model if closed and not click on check mark
    $(this).prop("checked", false);

    $(this).find(".modal-body").css({
      "max-height": "100%",
    });
  });
  $("#instructionsModal").on("close.bs.modal", function () {
    let instructionInputs = $("#instruction-check-btn");
    // this to reset the check boxes in upload instruction model if closed and not click on check mark
    $(this).prop("checked", false);
    $("#downloadTemplateLink")
      .addClass("disabled not-allowed-cursor btn-outline-success")
      .removeClass("btn-success");
    $("#downloadTemplateLink").removeAttr("href");

    $(this).find(".modal-body").css({
      "max-height": "100%",
    });
  });

  // this to make pick column window responsive
  $("#columnsDualBoxModal").on("show.bs.modal", function () {
    $(this).find(".modal-body").css({
      "max-height": "100%",
      "max-width": "100%",
    });
  });

  // this to prevent the sessions table dropdown from close when sort the sessions table
  $(document).on(
    "click",
    "#sessions-table-dropdown .dropdown-menu",
    function (e) {
      e.stopPropagation();
    }
  );

  // here when member will delete single session from table
  deleteSingleSession();

  $('#wrapper-ul a[data-toggle="tab"]').on("shown.bs.tab", function (e) {
    // console.log(e.target) // newly activated tab
    // console.log(e.relatedTarget) // previous active tab
    const activeTab = $(e.target);
    if (activeTab.data("section-name") === "pick_columns") {
      reselectColumnsFunc();
    }
  });

  // when member click on rename session button in details page
  renameSessionFunc();
  // to run the function of save the new updates of data table cells
  // saveNewUpdatedData();

  // to calculate the payment table overview
  // calcPaymentOverview();
}); // end of $(document).ready() event

// handler to be called when all Ajax requests have completed.
/*$(function(){
    setTimeout(checkMemberSessionStatus,10000);
});*/
$(document).ajaxError(function () {
  console.error("Triggered ajaxError handler.");
});