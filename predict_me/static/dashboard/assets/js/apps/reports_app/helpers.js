"use strict";

let currentFilterOptionSelected = ""; // this will change dynamically when user change filter option
let typingTimer; //timer identifier
let doneTypingInterval = 100; //time in ms, 5 second for example
let displayedColumnsArray = []; // this array will hold any columns checked by label to display it in the report table
let webSiteUrl = window.location.origin;

function swAlert(alertTitle, alertMsg, alertType) {
  swal.fire(`${alertTitle}`, `${alertMsg}`, `${alertType}`);
}

// this function to build or set the query in url
function setURLQuery(reportFilterOption) {
  let wholeURL = window.location.href; // this to use with query parameters
  let originURL = new URL(window.location.origin.concat("/dashboard/reports/"));

  let urlObj = new URL(wholeURL);
  let tmpChangedURL = "";
  // this to check if the member select option from the select menu
  if (reportFilterOption.val() !== null) {
    location.href = originURL.href.concat(reportFilterOption.val());
  }
}

// function will set the select option value based on the url query parameter
function setFilterOptions() {
  let filterTypeSelect = $("#filterTypeSelect");
  //<option selected disabled value="choose">Choose report section</option>
  let wholeURL = new URL(window.location.href); // this to use with query parameters
  let currentReportsVal = wholeURL.href.split("/").slice(-1)[0]; // to get last part or reports url /users, /plans
  // check if there is value in the url

  if (currentReportsVal !== "") {
    $("#no-filter-option").hide();
    filterTypeSelect.val(currentReportsVal).trigger("change");
    // $("#filterTypeSelect").select2(wholeSearchParam.get("reports")).trigger('change');
  } else {
    $("#no-filter-option").show();
    filterTypeSelect
      .find("optgroup:first")
      .before(
        '<option selected disabled value="choose">Choose report section</option>'
      );
  }
}

// this function will enable other organization type input if member select other from select menu
function enableOtherOrgType(selectID, otherInputID) {
  let selectIDJq = $(selectID);
  let otherIDJq = $(otherInputID);
  selectIDJq.on("change", function (evt) {
    const selectedValue = $(this).val();
    if (selectedValue === "Other") {
      // selectIDJq.toggleClass('disabled').attr("disabled", "disabled");
      otherIDJq
        .toggleClass("disabled")
        .removeAttr("disabled")
        .removeClass("not-allowed-cursor");
    } else {
      otherIDJq
        .toggleClass("disabled not-allowed-cursor")
        .attr("disabled", "disabled")
        .val("");
    }
  });
}

// this function will reset the filters fire when click reset filter button
function resetFilters() {
  location.href = window.location.origin.concat("/dashboard/reports/");
}

function testCookies() {
  console.log(document.cookie);
  document.cookie = "filters=one";
  document.cookie = "filters2=two";
  console.log(document.cookie);
}

// this function will watch any change on the filters to save it in cookies
function watchFilters() {
  $(".reports-filter-input").on(
    "keyup change paste propertychange input",
    function (evt) {
      clearTimeout(typingTimer);
      const filterInputField = () => {
        setCookieFilterFunc(this);
      };
      typingTimer = setTimeout(filterInputField, doneTypingInterval);
    }
  );

  $(".reports-filter-input").on("keydown", function () {
    clearTimeout(typingTimer);
  });
}

// this function will set the cookie when input changed
function setCookieFilterFunc(element) {
  const elem = $(element);
  /*$(elem[0].attributes).each(function () {
        console.log(this.nodeName + ' => ' + this.nodeValue);
    });*/
  setFiltersCookie(elem.attr("id"), elem.val());
}

// function to set cookie with its key and value
function setFiltersCookie(key, value) {
  document.cookie = `${key}=${value}`;
}

// function to delete cookie by name or all cookies
function deleteCookie(name, isAll) {
  if (isAll === true) {
    const cookies = document.cookie.split(";");
    for (let i = 0; i < cookies.length; i++)
      deleteCookie(cookies[i].split("=")[0]);
  } else {
    document.cookie = `${name}= ; expires = Thu, 01 Jan 1970 00:00:00 GMT`;
  }
}

// function to get cookie value by name
function getCookieValue(name) {
  return document.cookie
    .split("; ")
    .find((row) => row.startsWith(name))
    .split("=")[1];
}

// function will run after page load to check all filters cookies and set the value if exists
function setFilterInputCookieValue() {
  const cookies = document.cookie.split(";");
  for (let i = 0; i < cookies.length; i++) {
    const cookieName = cookies[i].split("=")[0].trim();
    const jqSelector = `#${cookieName}`;
    // first check if the cookie not the csrftoken (django cookie)
    if (cookieName !== "csrftoken") {
      // check if the input has select2 class
      if ($(jqSelector).hasClass("select2") === true) {
        $(jqSelector).val(getCookieValue(cookieName)).trigger("change");
      } else {
        // set the value of the input
        $(jqSelector).val(getCookieValue(cookieName));
      }
    }
  }
}

// this method will run when member click on reset button in report
function resetButton() {
  $("#members-table-reset-btn").on("click", function (evt) {
    console.error("delete all cookies...");
    deleteCookie("", true);
    $(".reports-filter-input").val("");
  });
}

// this function will return all cookies {name: value}
function getAllCookies() {
  let allCookies = {};
  const cookies = document.cookie.split(";");
  for (let i = 0; i < cookies.length; i++) {
    const cookieName = cookies[i].split("=")[0].trim();
    const jqSelector = `#${cookieName}`;
    // first check if the cookie not the csrftoken (django cookie)
    if (cookieName !== "csrftoken") {
      allCookies[cookieName] = getCookieValue(cookieName);
    }
  }

  return allCookies;
}

// this function will set the checked label to display the checked columns in the data table
function setReportTableColumns() {
  $(".lbl-reports-filter-display").on("change", function (evt) {
    const elem = $(this);
    const colName = elem.data("col-name");
    // if checked add to the array, otherwise delete it from the array
    if (this.checked === true) {
      displayedColumnsArray.push(colName);
    } else {
      displayedColumnsArray.splice(displayedColumnsArray.indexOf(colName), 1);
    }
    // console.warn(displayedColumnsArray);
  });
}

// report table draw function
function drawReportTable(reportTableData, reportSectionName) {
  //$("#data_handler_table > tbody tr").empty();
  let tableJQObj = null;
  let tableBodyElement = null;
  let tableHeader = null;
  const tableHeaderColumns = reportTableData["table_header"];
  if (reportSectionName === "users") {
    tableJQObj = $("#all-users-report-table");
    tableHeader = $("#all-users-report-table > thead tr:last");
    // tableBodyElement = $("#all-users-report-table > tbody tr:last");
  }

  // first thing is display the table columns header
  let allColumnsName = new Array();
  for (let col of tableHeaderColumns) {
    let colJQ = $(`.lbl-reports-filter-display[data-col-name="${col}"]`);
    allColumnsName.push(colJQ.data("display-name"));
  }
  let allTh = "";
  tableHeader.empty(); // to avoid and duplicate columns name
  for (let colN of allColumnsName) {
    allTh += `
        <th data-header-name="${colN}">
            ${colN}
        </th>

        `;
  }
  tableHeader.append(allTh);
}

// this function will take head name and return the name with small case and underscore instead space
function fixTableHeadName(name) {
  return name.replace(" ", "_").toLocaleLowerCase();
}
// the array contain items not filter its values
const notSearchArray = ["first_name", "last_name", "email"];

// this function will filter and clean the values of the filters
function filterAndCleanTheValue(value) {
    return value;
}


// function to convert filter names to camelCase
function camelize(str) {
    return str
        .replace(/(?:^\w|[A-Z]|\b\w)/g, function (word, index) {
            return index === 0 ? word.toLowerCase() : word.toUpperCase();
        })
        .replace(/\s+/g, '');
}

// this function will take the name and replace it with the correct name from the db
function replaceName(name) {
    switch (name) {
        case 'organization_name':
            return 'org_name';

        case 'organization_type':
            return 'org_type';

        case 'user_status':
            return 'status';

        case "plan":
            return "slug";

        case "register_date":
            return 'date_joined'

        default:
            return name;
    }
}

// function will clean and return the filter results
function preparingReportsFiltersWithValues(filtersArray) {
    const extractFilterNamesAndValues = (filterArray) => {
        let allResult = {};
        const data = filterArray.map(filterItem => {

            const filterName = replaceName(_.snakeCase(filterItem["filter_name"]));
            const filterValue = filterAndCleanTheValue(filterItem['filter_value']);
            // console.log(filterName, "---> ", filterValue)
            allResult[filterName] = filterValue;

        });
        return allResult;
    }
    return extractFilterNamesAndValues(filtersArray);
}

let allSearchResults = [];

// this function will take the prepared Reports Filters with its values and return report results from the filter
function getTheReportData(preparedFilters, filterData) {
    console.info(preparedFilters);
    console.log('Length of filters', '---> ', Object.keys(preparedFilters).length);
    // this map to filter the whole results from the backend
    let allCleanData = []; // the container of all report data with validation

    const filterDataResults = filterData.map(filterItem => {
        const preparedKeys = Object.keys(preparedFilters);
        for (let key in preparedKeys) {
            const preparedFilterKey = preparedKeys[key]; // filter key of the filter from the user
            const preparedValue = preparedFilters[preparedFilterKey]; // the value from the user selected in reports filter in the front end
            const filterValue = filterItem[preparedFilterKey]; // the value from the data in the data base query
            //   console.log(preparedFilterKey, "--->", preparedValue, "======", filterValue);
            // first check if it is not in the notSearchArray
            if (!notSearchArray.includes(preparedFilterKey)) {
                // console.log(preparedFilterKey, "--->", preparedValue, "======", filterValue);
                // check if the value from the reports filter match the value from the db
                // first check if the value is string or number
                if (typeof filterValue === 'string') {
                    const pattern = "^" + preparedValue + "$";
                    const regexObj = new RegExp(pattern);
                    // check if the string the user send match from the db
                    if(Array.isArray(regexObj.exec(filterValue)) === true){
                        // console.log(preparedFilterKey, "--->", preparedValue, "======", filterValue);
                        allSearchResults.push(filterItem);

                    }

                }else if(typeof filterValue === 'number'){
                    if((parseInt(preparedValue) === parseInt(filterValue)) || (parseInt(preparedValue) <= parseInt(filterValue))){
                        // console.log(preparedFilterKey, "--->", preparedValue, "======", filterValue);
                        allSearchResults.push(filterItem);
                    }
                }
            }

        }
        // console.log(filterItem)
    });
    // console.log(allSearchResults.length);
    // const nonDuplicateResults = Set(allSearchResults); // remove the duplicate items
    // console.log(new Set(allSearchResults).size);
    const nonDuplicateResults = _.uniqBy(allSearchResults, "MID");
    return nonDuplicateResults;

}

// report table draw function
function drawGeneratedReportTable(reportData, filtersArray) {
  console.log(reportData)
  // this function will save the filter name with its value, from filtersArray
  const preparedArray = preparingReportsFiltersWithValues(filtersArray);
  const allReportData = getTheReportData(preparedArray, reportData['report_data']);
  const extractFilters = (filtersArr) => {
    const filterdResults = filtersArr.map((fItem) => {
      const filterName = replaceName(camelize(fItem["filter_name"]));
      // console.log(filterName);
      return filterName;
    });
  };
  const fResults = extractFilters(filtersArray);
  // console.log(fResults);
  // console.log(Object.keys(reportData));
  // console.log(reportData);
  const obj = reportData["report_data"];
  const headerArray = reportData["table_header"];
  for (let header in headerArray) {
    headerArray[header] = fixTableHeadName(headerArray[header]);
  }

  // const reportObj = JSON.parse(reportData['report_data']);
  // console.log(reportData['report_data'])
  let reportObj = reportData["report_data"];
  // console.log(JSON.stringify(reportObj));
  //$("#data_handler_table > tbody tr").empty();
  let tableTd = "";
  let allTableRow = "";
  let tmpTableTd = "";
  let tmpTableTr = "";
  let tableJQObj = null;
  let tableBodyElement = null;
  let tableHeader = null;
  // const tableHeaderColumns = reportTableData['table_header'];
  if (reportData["report_section_name"] === "users") {
    tableJQObj = $("#all-users-report-table");
    tableHeader = $("#all-users-report-table > thead tr:last");
    tableBodyElement = $("#all-users-report-table > tbody");
  } else if (reportData["report_section_name"] === "data-usage") {
    //data-usage-report-table
    tableHeader = $("#data-usage-report-table > thead tr:last");
    tableBodyElement = $("#data-usage-report-table > tbody");
  }
  tableBodyElement.empty();
  // for(const [key, value] of Object.entries(reportData['report_data'])){
  //   console.log(key, value)
  // }
  // console.log(reportData['report_data'])
  for (let rowReport of allReportData) {
    for (let name of reportData["table_header"]) {
      // console.log(fixTableHeadName(name))
      // check if the cancelled_users or active_user is here
      let headName = fixTableHeadName(name);
      // console.log(reportData['table_header'])
      if (headName === "user_status") {
        headName = "status";
      } else if (headName === "plan") {
        headName = "slug";
      } else if (headName == "organization_type") {
        headName = "org_type";
      }
      tmpTableTd += `
        <td>
          ${rowReport[headName]}
        </td>
      `;
    }
    // console.log(headName, rowReport[headName])
    tableBodyElement.append(`
        <tr>
          ${tmpTableTd}
        </tr>
        `);
    tmpTableTr = "";
    tmpTableTd = "";
  }
}

// console.log(tableRow)
// tableBodyElement.append(tableRow);
// console.log(reportData['report_data']);

// this function will draw the table header
function drawReportTableHeader(columns) {
  let reportSection = window.location.href.split("/");
  reportSection = reportSection.pop();
  // console.log(reportSection)
  // all-users-report-table, data-usage-report-table, profit-share-report-table, revenue-report-table
  let table;
  if (reportSection === "users") {
    table = $("#all-users-report-table > thead");
  } else if (reportSection === "data-usage") {
    table = $("#data-usage-report-table > thead");
  }

  table.empty();
  let tableHeader = "<tr>";
  for (let col of columns) {
    tableHeader += `
          <th>${col}</th>
      `;
  }
  tableHeader += "</thead>";
  table.append(tableHeader);
}
