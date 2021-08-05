"use strict";
let filterOptionsBlock = $("#filterOptionsBlock");
let selectedFilterUL = $("#deselectedFilterUL");
const genericFilterItems = $(".generic-filter-li-item");
const genericFilterItemsDeselected = $(".generic-filter-item-selected");
let currentClickedLeftItem = null;
let currentClickedRightItem = null;
let currentClickedLeftItemData = {
  ITEM: {},
};
let currentClickedRightItemData = {
  ITEM: {},
};
const middleDeselectFilterOptionBtn = $("#middleDeselectFilterOptionBtn");
const middleSelectFilterOptionBtn = $("#middleSelectFilterOptionBtn");
const genericResetFilterBtn = $("#genericResetFilterBtn");
const leftFiltersUL = $("#leftFiltersUL");
let selectedFiltersArray = [];
// const noOptionsMsg = "<h4>Please Select filters from filter on right</h4>";
const noOptionsMsg = "<h4>This filter has no options</h4>";

// thsi function will return all data related to clicked element from left side
function getAllClickedFilterData(element, rightOrLeft) {
  if (rightOrLeft === "L") {
    const reportSectionName = element.data("report-section-name");
    const reportFilterName = element.data("filter-name");
    const reportFilterIdx = element.data("id");
    const reportFilterHasOptions = element.data("has-options");
    const reportInputID = element.data("input-id");
    currentClickedLeftItemData["ITEM"] = {};
    currentClickedLeftItemData["ITEM"] = {
      idx: reportFilterIdx,
      filterName: reportFilterName,
      reportSectionName: reportSectionName,
      reportFilterHasOptions: reportFilterHasOptions,
      reportInputID: reportInputID,
    };
    return [
      reportFilterIdx,
      reportSectionName,
      reportFilterName,
      reportFilterHasOptions,
      reportInputID,
    ];
  } else if (rightOrLeft === "R") {
    /*
  		filterId: "country"
      filterName: "Countries"
      filterValue: "ALL"
      hasOptions: true
      inputId: "li_country"
      reportSectionName: "users"
		*/
    const reportSectionName = element.data("report-section-name");
    const reportFilterName = element.data("filter-name");
    const reportFilterValue = element.data("filter-value");
    const reportFilterHasOptions = element.data("has-options");
    const reportInputID = element.data("input-id");
    currentClickedRightItemData["ITEM"] = {};
    currentClickedRightItemData["ITEM"] = {
      filterName: reportFilterName,
      reportSectionName: reportSectionName,
      reportFilterHasOptions: reportFilterHasOptions,
      reportInputID: reportInputID,
    };
    return [
      reportSectionName,
      reportFilterName,
      reportFilterValue,
      reportFilterHasOptions,
      reportInputID,
    ];
  }
}

// this function will return selected column with its choosen option
function generateSelectedFilter(
  filterItemID,
  reportSectionName,
  filterName,
  filterOption,
  filterInputID
) {
  let theValue = "";
  let theOption = "";
  if (filterOption === "False") {
    theValue = "All";
  }

  const listItem = `
		<li class="list-group-item generic-filter-item-selected" data-input-id="${filterInputID}" data-filter-id="${filterItemID}" data-filter-name="${filterName}" data-report-section-name="${reportSectionName}" data-has-options="${filterOption}" data-filter-value="${theValue}">
			<span id="filterSelectedName">${filterName}</span>
			<!-- <span id="filterSelectedOption" class="label label-light-info label-inline font-weight-bolder float-right">${theOption}</span> -->
		</li>
	`;

  return listItem;
}

// this function will return selected column with its choosen option, when user clicked on right arrow btn
function generateSelectedFilterAfterClick(inputObjValues) {
  let multipleCode = "";
  if (inputObjValues["isMultiple"] === true) {
    multipleCode = `
			<span id="filterSelectedOption" class="label label-light-info label-inline font-weight-bolder float-right">${inputObjValues["filterValue"].length}</span>
		`;
  }
  const listItem = `
    <li class="list-group-item generic-filter-item-selected" data-filter-value="${inputObjValues["filterValue"]}" data-has-options="${inputObjValues["hasOptions"]}" data-filter-id="${inputObjValues["filterInputID"]}" data-filter-name="${inputObjValues["filterName"]}" data-report-section-name="${inputObjValues["filterReportSectionName"]}" data-input-id="${inputObjValues["mainFilterID"]}">
      <span id="filterSelectedName">${inputObjValues["filterName"]}</span>
      ${multipleCode}
    </li>
  `;

  return listItem;
}

// this function will take an item and render it directly to right column if it has no options, otherwise will display the options in the middle column
function renderFilterToMiddleOrRightColumn(showOnly, lOrR) {
  if (lOrR === "L") {
    const [
      reportFilterIdx,
      reportSectionName,
      reportFilterName,
      reportFilterHasOptions,
      reportInputID,
    ] = getAllClickedFilterData(currentClickedLeftItem, "L");
    // check if the element exists in the selected array
    if (selectedFiltersArray.includes(reportFilterName) === false) {
      const rightItem = generateSelectedFilter(
        reportFilterIdx,
        reportSectionName,
        reportFilterName,
        reportFilterHasOptions,
        reportInputID
      );
      selectedFiltersArray.push(reportFilterName);
      if (showOnly === true) {
        selectedFilterUL.append(rightItem);
        currentClickedLeftItem.addClass(
          "disabled bg-gray-100 not-allowed-cursor"
        );
      }
    }
  } else if (lOrR === "R") {
    /*
    reportSectionName,
    reportFilterValue,
    reportFilterName,
    reportFilterHasOptions,
    reportInputID
    */
  }
}

function fetchReportOptions(filterIdx, filterName, reportSection) {
  // console.log(filterIdx, filterName, reportSection);
  // this function will fetch or generate the required options for spicific filter
  let inputGenObj = null;
  switch (filterName) {
    case "Country":
    case "State":
      inputGenObj = new InputGenerator(
        filterIdx,
        "country",
        "country",
        "select",
        "Country",
        reportSection
      );
      filterOptionsBlock.html(inputGenObj.countrySelectGenerator());
      break;

    case "City":
      inputGenObj = new InputGenerator(
        filterIdx,
        "city",
        "city",
        "text",
        "City",
        reportSection
      );
      filterOptionsBlock.html(inputGenObj.cityInputGenerator());
      break;

    case "Organization Type":
      inputGenObj = new InputGenerator(
        filterIdx,
        "org_type",
        "org_type",
        "text",
        "Organization Type",
        reportSection
      );
      filterOptionsBlock.html(inputGenObj.orgTypeInputGenerator());
      break;

    case "Organization Name":
      inputGenObj = new InputGenerator(
        filterIdx,
        "org_name",
        "org_name",
        "text",
        "Organization Name",
        reportSection
      );
      filterOptionsBlock.html(inputGenObj.selectMenuGenerator());
      break;

    case "Register Date":
      inputGenObj = new InputGenerator(
        filterIdx,
        "register_date",
        "register_date",
        "date",
        "Register Date",
        reportSection
      );
      filterOptionsBlock.html(inputGenObj.registerDateInputGenerator());
      break;

    case "Job Title":
      inputGenObj = new InputGenerator(
        filterIdx,
        "job_title",
        "job_title",
        "text",
        "Job Title",
        reportSection
      );
      filterOptionsBlock.html(inputGenObj.jobsInputGeneratro());
      break;

    case "Run Model":
      inputGenObj = new InputGenerator(
        filterIdx,
        "run_model",
        "run_model",
        "radio",
        "Run Model",
        reportSection,
        "Members who run the model or not"
      );
      filterOptionsBlock.html(inputGenObj.yesNoInputGenerator("run_model"));
      break;

    case "Annual Revenue":
      inputGenObj = new InputGenerator(
        filterIdx,
        "annual_revenue",
        "annual_revenue",
        "",
        "Annual Revenue",
        reportSection
      );
      filterOptionsBlock.html(inputGenObj.annoualInputGenerator());
      break;

    case "Total Staff":
      inputGenObj = new InputGenerator(
        filterIdx,
        "total_staff",
        "total_staff",
        "number",
        "Total Staff",
        reportSection
      );
      filterOptionsBlock.html(inputGenObj.textInputGenerator());
      break;

    case "Number of Volunteer":
      inputGenObj = new InputGenerator(
        filterIdx,
        "num_of_volunteer",
        "num_of_volunteer",
        "number",
        "Number of Volunteer",
        reportSection
      );
      filterOptionsBlock.html(inputGenObj.textInputGenerator());
      break;

    case "Number of Board Members":
      inputGenObj = new InputGenerator(
        filterIdx,
        "num_of_board_members",
        "num_of_board_members",
        "number",
        "Number of Board Members",
        reportSection
      );
      filterOptionsBlock.html(inputGenObj.textInputGenerator());
      break;

    case "Plan":
      inputGenObj = new InputGenerator(
        filterIdx,
        "plan",
        "plan",
        "",
        "Plan",
        reportSection
      );
      filterOptionsBlock.html(inputGenObj.planSelectGenerator());
      break;

    case "Start Offer Date":
      inputGenObj = new InputGenerator(
        filterIdx,
        "start_offer_date",
        "start_offer_date",
        "date",
        "Start Offer Date",
        reportSection
      );
      filterOptionsBlock.html(inputGenObj.dateInputsGenerator());
      break;

      case "User Status":
        inputGenObj = new InputGenerator(
          filterIdx,
          "status",
          "status",
          "date",
          "User Status",
          reportSection
        );
        filterOptionsBlock.html(inputGenObj.userStatusMenu());
        break;

      case "Days Left":
        inputGenObj = new InputGenerator(
          filterIdx,
          "days_left",
          "days_left",
          "date",
          "Days Left",
          reportSection
        );
        filterOptionsBlock.html(inputGenObj.dateInputsGenerator());
        break;

      case "Revenue Start Date":
        inputGenObj = new InputGenerator(
          filterIdx,
          "revenue_start_date",
          "revenue_start_date",
          "date",
          "Revenue Start Date",
          reportSection
        );
        filterOptionsBlock.html(inputGenObj.dateInputsGenerator());
        break;

      case "Plan Start Date":
        inputGenObj = new InputGenerator(
          filterIdx,
          "plan_start_date",
          "plan_start_date",
          "date",
          "Plan Start Date",
          reportSection
        );
        filterOptionsBlock.html(inputGenObj.dateInputsGenerator());
        break;

      case "Last Run":
        inputGenObj = new InputGenerator(
          filterIdx,
          "last_run",
          "last_run",
          "date",
          "Last Run",
          reportSection
        );
        filterOptionsBlock.html(inputGenObj.dateInputsGenerator());
        break;

      case "Usage":
        inputGenObj = new InputGenerator(
          filterIdx,
          "usage",
          "usage",
          "select",
          "Usage",
          reportSection
        );
        filterOptionsBlock.html(inputGenObj.dataUsageInputGenerator());
        break;

    default:
      break;
  }
  selectAndDeselectFiltersBtns();
}

function getFilterOption(element, lOrR) {
  // this function will take jquery element and set its own filter option in #filterOptionsBlock based on the filter selected

  // first check if the user click or double click
  const [
    reportFilterIdx,
    reportSectionName,
    reportFilterName,
    reportFilterHasOptions,
    reportInputID,
  ] = getAllClickedFilterData(element, lOrR);
  // console.log(reportFilterIdx, reportFilterName, reportSectionName);
  // check if the filter name containe an options to filter, or otherwise directly move it to right (last column)

  if (reportFilterHasOptions === "True") {
    fetchReportOptions(reportFilterIdx, reportFilterName, reportSectionName);
    renderFilterToMiddleOrRightColumn(false, "L");
  } else {
    // the filter has no options
    // first notifiy the user that is no option for current filter by
    filterOptionsBlock.html(
      "<h5>No options for current filter you can select it directly</h5>"
    );
  }
}

// single and double click on left column function, this will fire the events
function selectFiltersOptions() {
  // single click function
  genericFilterItems.on("click", function(event) {
    const item = $(this);
    // console.log(item.data())
    const filterName = item.data("filter-name");
    currentClickedLeftItem = item;
    // check if it is selected filter before
    if (item.hasClass("disabled") === false) {
      $(".generic-filter-li-item.bg-primary-o-40").removeClass(
        "bg-primary-o-40"
      );

      currentClickedLeftItem.addClass("bg-primary-o-40");
      const [
        reportFilterIdx,
        reportSectionName,
        reportFilterName,
        reportFilterHasOptions,
        reportInputID,
      ] = getAllClickedFilterData(currentClickedLeftItem, "L");
      if (
        currentClickedLeftItemData["ITEM"]["reportFilterHasOptions"] === "True"
      ) {
        // generateSelectedFilter(filterItemID, filterName, reportSectionName, filterOption)
        getFilterOption(currentClickedLeftItem, "L");
      } else {
        filterOptionsBlock.html(noOptionsMsg);
      }
    }
  });

  // double click function
  genericFilterItems.on("dblclick", function(event) {
    const item = $(this);
    // console.log(item.data())
    const filterName = item.data("filter-name");
    if (selectedFiltersArray.includes(filterName) === false) {
      if (
        currentClickedLeftItemData["ITEM"]["reportFilterHasOptions"] === "True"
      ) {
        // generateSelectedFilter(filterItemID, filterName, reportSectionName, filterOption)
        getFilterOption(currentClickedLeftItem, "L");
      } else {
        renderFilterToMiddleOrRightColumn(true, "L");
        currentClickedLeftItem = null;
        filterOptionsBlock.html(noOptionsMsg);
      }
    }
  });
}

// single and double click on left column function, this will fire the events
function deselectFiltersOptions() {
  // single click function
  $("#deselectedFilterUL").on(
    "click",
    ".generic-filter-item-selected",
    function(event) {
      const item = $(this);
      // console.log(item.data());
      currentClickedRightItem = item;
      const [
        reportSectionName,
        reportFilterName,
        reportFilterValue,
        reportFilterHasOptions,
        reportInputID,
      ] = getAllClickedFilterData(currentClickedRightItem, "R");
      fetchReportOptions("", reportFilterName, reportSectionName);
    }
  );

  // double click function
  $("#deselectedFilterUL").on(
    "dblclick",
    ".generic-filter-item-selected",
    function(event) {
      const item = $(this);
      currentClickedRightItem = item;
      // console.log(item.data())
      renderToRightFilterBlock(item);
      filterOptionsBlock.html(noOptionsMsg);
    }
  );
}

// this function will enable and hide deselected item from right
function renderToRightFilterBlock(item) {
  //list-group-item generic-filter-li-item py-0 bg-primary-o-40 disabled bg-gray-100 not-allowed-cursor
  const inputID = currentClickedRightItem.data("input-id");
  const tmpID = `.generic-filter-li-item[data-input-id='${inputID}']`;
  const leftItem = $(tmpID);
  // console.log(tmpID)
  leftItem.removeClass(
    "disabled bg-gray-100 not-allowed-cursor bg-primary-o-40"
  );
  item.detach();
}

// this function will prepare the json file from selectFilterBtn click event to render it by calling renderFilterToMiddleOrRightColumn function
function prepareRenderElement(inputsArray) {
  // for (let arr of inputsArray) {
  //   // console.log(arr)
  //   const rightItemCode = generateSelectedFilterAfterClick(arr);
  //   selectedFilterUL.append(rightItemCode);
  // }
  const tmpId = inputsArray[0].filterInputID; //data-filter-id li[data-company='Microsoft']
  const tmpElement = `li[data-filter-id="${tmpId}"]`;

  const ch = selectedFilterUL.find(tmpElement);
  // check if the element exists before
  if(ch.length === 0){
    const rightItemCode = generateSelectedFilterAfterClick(inputsArray[0]);
    selectedFilterUL.append(rightItemCode);
  }


}

// this function will fire the select and deselete buttons when user click on them
function selectAndDeselectFiltersBtns() {
  const deSelectFilterBtn = $(".deSelectFilterBtn");
  const selectFilterBtn = $(".selectFilterBtn");

  /* $("#filterOptionsBlock").on("click", selectFilterBtn.prop("tagName"), function(event){

	}); */
  // select button
    // $("#filterOptionsBlock").on("click", "button.selectFilterBtn", function(event) {
    $("#filterOptionsBlock").off().on("click", "button.selectFilterBtn", function(event) {
      // i used off to prevent any repeating for event fireing
    // $("#filterOptionsBlock button.selectFilterBtn").one("click", function(event) {
      let startDate = "";
      let endDate = "";
      let fullDate = "";
      let savedElement = {};
      let allSavedElement = [];
      currentClickedLeftItem.addClass(
        "disabled bg-primary-o-40 not-allowed-cursor"
      );
      let allInputsArray = []; // this array will hold all inputs with its values in the middle block
      const selectedInput = $("#" + $(this).data("filter-input-id")); // fetch the input in the middle block
      let allInputsArrayFilter = (array, fieldName) => {
        let allKeys = new Set();
        array.map(function(item){
          // console.log(Object.keys(ar))
          // allKeys.push(item.filterName);
          // allKeys.add(item.filterName);
          // console.log(allKeys)
        });
        // console.log(array, fieldName)
      }

      const selectedFilterWrapper = $(this).closest(".filter-options-wrapper"); // get the parent of all inputs in the block
      const allInputsInBlock = selectedFilterWrapper.find(".filter-input");
      // console.log(allInputsInBlock, "\n")
      // const checkElements = allInputsInBlock.(function(item){
      //   console.log(item);
      // });
      // console.log(checkElements)
      let appendedKeys = new Set();
      allInputsInBlock.each(function(index, el) {
        const element = $(el);
        const filterName = element.data("filter-name");

        // first check if the inputs are date pick range
        if (element.hasClass("datePickerInputs") === true) {
          if (filterName.includes("start_date") === true) {
            startDate = element.val();
          }
          if (filterName.includes("end_date") === true) {
            endDate = element.val();
          }
          fullDate = startDate.concat(" - ").concat(endDate);
          savedElement = {
            filterName: element.data("input-full-name"),
            filterValue: fullDate,
            isMultiple: true ? Array.isArray(element.val()) : false,
            filterInputID: element.attr("id"),
            filterReportSectionName: element.data("report-section-name"),
            mainFilterID: element.data("input-id"),
            hasOptions: element.data("has-options"),
          };
          // console.log(savedElement)
          // console.log(allInputsArray)

        } else {
          // normal inputs not date inputs
          // console.log(element.val())
          // console.log(element.data("tmpValue"))
          savedElement = {
            filterName: filterName,
            filterValue: element.val(),
            isMultiple: true ? Array.isArray(element.val()) : false,
            filterInputID: element.attr("id"),
            filterReportSectionName: element.data("report-section-name"),
            mainFilterID: element.data("input-id"),
            hasOptions: element.data("has-options"),
          };
          // console.log(savedElement)
          // console.log(allInputsArray)
          // allInputsArray.push(savedElement);
          // allInputsArrayFilter(allInputsArray, "one")
        }
        // console.info(allInputsArray)
      });
      // console.log(savedElement)
      allInputsArray.push(savedElement);
      // console.log(allInputsArray)
      // console.log("base", allInputsArray)
      // console.log(_.uniqBy(allInputsArray, 'filterName'))
      prepareRenderElement(allInputsArray);
      allInputsArray = []; // reset the array
      // savedElement = {};
      filterOptionsBlock.html(noOptionsMsg);

    });


    // deselect button
    $("#generic-filters-wrapper").on("click", "button.deSelectFilterBtn", function(event) {
      console.log('deselect the value')
    });
}

// this function will run when admin click on middle select filter button
function selectFilterOption(event) {
  // check if the currentClickedLeftItem is not null run the event
  if (currentClickedLeftItem !== null) {
    renderFilterToMiddleOrRightColumn(true, "L");
    filterOptionsBlock.html(noOptionsMsg);
    currentClickedLeftItem = null;
  }
}

// this function will reset the default filters
function resetDefaultReports() {
  currentClickedLeftItem = null;
  currentClickedRightItem = null;
  currentClickedLeftItemData = {
    ITEM: {},
  };
  currentClickedRightItemData = {
    ITEM: {},
  };
  filterOptionsBlock.html(noOptionsMsg);
  selectedFiltersArray = [];
  genericFilterItems.each(function(idx, element) {
    const ele = $(element);
    ele.removeClass("disabled bg-gray-100 not-allowed-cursor bg-primary-o-40");
  });
  const allSelectedFilters = selectedFilterUL.find("li");
  allSelectedFilters.each(function(idx, element) {
    const ele = $(element);
    ele.remove();
  });
}

// this function will run when filter submit button clicked
function filterReportSubmitBtn() {
  $("#members-submit-filter-btn").on("click", function(event) {
    const reportsWrapper = $("#reports-content-wrapper");
    // first, get the children of the reportsWrapper [revenue-reports-wrapper, data-usage-reports-wrapper, extra-records-reports-wrapper, profit-share-reports-wrapper]
    const firstReportSection = reportsWrapper.find("section").first();
    const allSelectedFilters = selectedFilterUL.find("li");
    let allFiltersArr = [];
    allSelectedFilters.each(function(idx, ele) {
      const element = $(ele);
      /*
			filterId: "state"
			filterName: "State"
			filterValue: "Alaska"
			hasOptions: true
			inputId: "li_state"
			reportSectionName: "users"
			*/
      const dataObj = {
        filter_id: element.data("filter-id"),
        filter_name: element.data("filter-name"),
        filter_value: element.data("filter-value"),
        report_section_name: element.data("report-section-name"),
        has_options: element.data("has-options"),
      };
      allFiltersArr.push(dataObj);
    });
    // check if there is any filter selected then send the request
    if(allFiltersArr.length > 0){
      const reportSection = window.location.href.split("/");
      const filterRequest = sendFiltersValues(allFiltersArr, reportSection.pop());
      $.when(filterRequest).done(function(data, textStatus, jqXHR) {
        // console.log(Object.keys(data));
        // console.log(data);
        // console.log(textStatus);
        // console.log(jqXHR);
        // console.log(jqXHR.status);
        if (textStatus === "success" && jqXHR.status === 200) {
          drawReportTableHeader(data["table_header"]);
          drawGeneratedReportTable(data, allFiltersArr);
        }
      });
    }else{
      console.error("Please Select filter!!");
    }

  });
}

//
function setFilterOptionsFireFunc() {
  middleSelectFilterOptionBtn.on("click", function(event) {
    selectFilterOption(event);
  });
}

$(document).ready(function() {
  selectFiltersOptions();
  deselectFiltersOptions();
  setFilterOptionsFireFunc();
  selectAndDeselectFiltersBtns();
  genericResetFilterBtn.on("click", function(event) {
    resetDefaultReports();
  });
  filterReportSubmitBtn();
  // enable states select menu when select country usa
  $("#filterOptionsBlock").on("change", "#country", function(event) {
    const ele = $(this);
    const usa = ["United States of America", "United States"];
    const found = ele.val().some((r) => usa.indexOf(r) >= 0);
    if (found === true) {
      $("#state").removeClass("disabled").removeAttr("disabled");
    } else {
      $("#state").addClass("disabled").attr("disabled", "disabled");
    }
  });
});
