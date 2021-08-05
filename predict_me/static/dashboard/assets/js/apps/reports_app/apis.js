'use strict';

// this function will send request with
function fetchReportRequest(reportSectionName, displayedColumns, allFilterCookies) {
    let sendData = {
        "reports_section_name": reportSectionName,
        'displayed_columns': JSON.stringify(displayedColumns),
        'all_filter_cookies': JSON.stringify(allFilterCookies),
    };
    return $.ajax({
        url: webSiteUrl + "/dashboard/reports/api/fetch",
        beforeSend: function (xhr, settings) {
            xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
        },
        method: "POST",
        data: sendData,
        dataSrc: '',
        error: function (error) {
            //called when there is an error
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

        }

    });
}

// this function will send all filters and its values
function sendFiltersValues(filtersArray, reportSectionName) {
    let sendData = {
        "filtersArray": JSON.stringify(filtersArray),
        "reportSectionName": reportSectionName
    };

    return $.ajax({
        url: webSiteUrl + "/dashboard/reports/api/filters",
        beforeSend: function (xhr, settings) {
            xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
        },
        method: "POST",
        data: sendData,
        dataSrc: '',
        error: function (error) {
            //called when there is an error
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

        }

    });
}
// this is the loader where the report options show loading
let loader = $(".loader-filter-options");
// this function will fetch all data for custom column
function fetchDataForReports(columnName) {
    return $.ajax({
        url: webSiteUrl + "/dashboard/reports/api/fetch-custom-report-data",
        beforeSend: function (xhr, settings) {
            xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
            // $("#filterOptionsBlock").html("");
            loader.show();
        },
        complete: function (xhr, settings) {
            loader.show();
        },
        method: "POST",
        data: {
            "columnName": columnName
        },
        dataSrc: '',
        error: function (error) {
            //called when there is an error
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

        }

    });
}
