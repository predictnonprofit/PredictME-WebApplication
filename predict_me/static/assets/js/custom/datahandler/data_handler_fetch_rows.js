"use strict";
var isAjaxRequestDone = { // this object will be in the success(), method of ajax requests, to set true mean all done, false not done
  isDone: "",
  functionName: "",
};


// this function will fetch the rows of the saved file
function fetchDataFileRows(recordsCount) {
  const sessionID = extractLastSessionID();
  if (typeof recordsCount === 'undefined') {
    recordsCount = 25;
  }
  if (Number.isInteger(sessionID) === true) {
    return $.ajax({
      url: webSiteUrl + "/dashboard/data/api/rows",
      beforeSend: function (xhr, settings) {
        xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
      },
      method: "POST",
      data: {
        "recordsCount": parseInt(recordsCount),
        'session_id': parseInt(sessionID),
      },
      error: function (error) {
        //called when there is an error
        swAlert("Error", `${error.statusText}:-> ${error.message}`, "error");
      },
      complete: function (jqXHR, textStatus) {
        /*  console.log(textStatus);
          console.log(jqXHR.status);
          console.log(jqXHR);*/
        // check if the request complete successfully
        /* if(textStatus === 'success' && jqXHR.status === 200){

         }*/

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
}

// this function will fetch rows with not validate data
function fetchNotValidateRows(colName) {
  const parameters = window.location.pathname;
  const sessionID = extractLastSessionID();
  if (Number.isInteger(sessionID) === true) {
    return $.ajax({
      url: webSiteUrl + "/dashboard/data/api/filter-rows",
      beforeSend: function (xhr, settings) {
        xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
      },
      method: "POST",
      data: {
        "column_name": colName,
        'records_number': clickedRecordsCount,
        'session_id': parseInt(sessionID),
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
}

// function will sort the rows based on the errors...
function sortHeader(colObj) {
  // check if there is no search query, to run the validate
  if ($("#searchQuery").val() === "") {
    $("#resetSortTableBtn").removeClass("disabled");
    $("#resetSortTableBtn").removeAttr("disabled style");
    isClickedFilterCol = true;
    const colJqObj = $(colObj);
    const colName = colJqObj.data("col-name");
    clickedFilteredColName = colName;
    //console.log(colJqObj[0].attributes);
    // check if the clicked column has error in validation of his cell(s)
    if (colJqObj.data('is-error') === 1) {
      //data_handler_table
      const dataTable = $("#data_handler_table");
      $("#loadingDataSpinner").fadeIn();
      // $("#data_handler_table tbody tr").detach();
      document.getElementById("data_handler_body").innerHTML = "";

      let fetchNotValidateRowsResponse = fetchNotValidateRows(colName);
      $.when(fetchNotValidateRowsResponse).done(function (rowData, rowTextStatus, rowJqXHR) {
        /* console.log(rowData);
        console.log(rowTextStatus);
        console.log(rowJqXHR); */
        // console.log(rowData);
        drawDataTableRows(rowData, true);
      });
    }
  } else {
    return false;
  }
}


// function will call when user change the select menu of how many records will display
function fetchRecordsByCount(recordsCount, isLastPage) {
  const recCount = parseInt(recordsCount);
  $("#data_handler_table > tbody tr").empty();
  $("#loadingDataSpinner").fadeIn('fast');
  // let tableBody = document.getElementById("data_handler_body");
  // tableBody.innerHTML = "";
  let resetFetchRecoredsResponse = fetchDataFileRows(recCount);
  $.when(resetFetchRecoredsResponse).done(function (data, textStatus, jqXHR) {
    if (textStatus == "success") {
      if (isLastPage === true) {
        drawDataTableRows(data, false, true);
      } else {
        drawDataTableRows(data, false);
      }
    } else {
      swAlert("Error", data, 'error');
    }
  });
}


// this function will fetch the rows which contain search query
function fetchDataFileRowsBySearchQuery(searchQuery) {
  // check if the session has id
  const sessionID = extractLastSessionID();
  // check if session is numeric
  if (Number.isInteger(sessionID) === true) {
    return $.ajax({
      url: webSiteUrl + "/dashboard/data/api/search-query-records",
      beforeSend: function (xhr, settings) {
        xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
      },
      method: "POST",
      data: {
        "searchQuery": searchQuery,
        'session_id': parseInt(sessionID),
      },
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
}

// function will call when user change the select menu of how many records will dispaly
function fetchRecordsBySearchQuery(searchQuery) {
  $("#data_handler_table > tbody tr").empty();
  $("#loadingDataSpinner").fadeIn();
  $("#resetSortTableBtn").removeClass("disabled");
  $("#resetSortTableBtn").removeAttr("disabled style");
  // let tableBody = document.getElementById("data_handler_body");
  // tableBody.innerHTML = "";
  let searchQureyResponse = fetchDataFileRowsBySearchQuery(searchQuery);
  $.when(searchQureyResponse).done(function (data, textStatus, jqXHR) {
    if ((textStatus == "success") && (jqXHR.status === 200)) {
      // console.log(data);
      drawDataTableRows(data, false);
    } else {
      swAlert("Error", data, 'error');
    }
  });
}


// function will save if the member accept and download upload template
function saveMemberAccepts(acceptData) {
  const parameters = window.location.pathname;
  return $.ajax({
    url: webSiteUrl + "/dashboard/data/api/accepts-download",
    beforeSend: function (xhr, settings) {
      xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
    },
    method: "POST",
    data: {
      "accept_data": JSON.stringify(acceptData),
      'parameters': parameters,
    },
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


// function will send request for the server to check if member upload data file, this will use in setTheCookie function
function checkIfMemberUploadDataFile() {
  const parameters = window.location.pathname;

  return $.ajax({
    url: webSiteUrl + "/dashboard/data/api/check-upload-member",
    beforeSend: function (xhr, settings) {
      xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
    },
    method: "POST",
    data: {
      'parameters': parameters
    },
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


// function will check if the member set his process steps to done
function checkIfMemberProcessStatus(choice) {
  const parameters = window.location.pathname;
  let data = "";
  if (typeof choice !== "undefined") data = {
    "choice": choice,
    'parameters': parameters
  }
  return $.ajax({
    url: webSiteUrl + "/dashboard/data/api/check-process-status",
    beforeSend: function (xhr, settings) {
      xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
    },
    method: "POST",
    data: data,
    global: false,
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


// fetch the last session name of the member
function fetchLastSessionName() {
  const parameters = window.location.pathname;
  let webSiteUrl = window.location.origin;
  const data = {
    'parameters': parameters
  };

  return $.ajax({
    async: false,
    url: webSiteUrl + "/dashboard/data/api/fetch-last-session-name",
    beforeSend: function (xhr, settings) {
      xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
    },
    method: "POST",
    data: data,
    global: false,
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

// fetch the last session name of the member
function checkIfUserAllowedRecordNumber() {
  const parameters = window.location.pathname;
  let webSiteUrl = window.location.origin;
  const data = {
    'parameters': parameters
  };

  return $.ajax({
    async: false,
    url: webSiteUrl + "/dashboard/data/api/check-user-records-number",
    beforeSend: function (xhr, settings) {
      xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
    },
    method: "POST",
    data: data,
    global: false,
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

// set the last session name or the last step on datahandler
function setSessionLastName(sessionName) {
  const parameters = window.location.pathname;
  return $.ajax({
    url: webSiteUrl + "/dashboard/data/api/set-last-session-name",
    beforeSend: function (xhr, settings) {
      xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
    },
    method: "POST",
    data: {
      "session_name": sessionName,
      'parameters': parameters
    },
    global: false,
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

function checkSessionLabelRequest() {
  const parameters = window.location.pathname;
  return $.ajax({
    url: webSiteUrl + "/dashboard/data/api/set-session-label",
    beforeSend: function (xhr, settings) {
      xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
    },
    method: "POST",
    data: {
      'get_session_label': true,
      'parameters': parameters
    },
    // global: false,
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

function setSessionLabelRequest(sessionLabel) {
  const sessionID = extractLastSessionID();
  return $.ajax({
    url: webSiteUrl + "/dashboard/data/api/set-session-label",
    beforeSend: function (xhr, settings) {
      xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
    },
    method: "POST",
    data: {
      'session_id': sessionID,
      "session_label": sessionLabel,
    },
    // global: false,
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

// delete single or all sessions for the user
function deleteDataSessionsRequest(singleOrAll) {
  const parameters = window.location.pathname;
  let data = {
    'parameters': parameters,
    "method": singleOrAll
  };
  return $.ajax({
    url: webSiteUrl + "/dashboard/data/api/delete-data-session",
    beforeSend: function (xhr, settings) {
      xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
    },
    method: "POST",
    data: data,
    global: false,
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

function renameSessionRequest(sessionName) {
  const parameters = window.location.pathname;
  let data = {
    'parameters': parameters,
    "session_name": sessionName
  };
  return $.ajax({
    url: webSiteUrl + "/dashboard/data/api/rename-data-session",
    beforeSend: function (xhr, settings) {
      xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
    },
    method: "POST",
    data: data,
    global: false,
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

// this is the function will run the Model
function runModel() {
  const parameters = window.location.pathname;
  let data = {};
  return $.ajax({
    url: webSiteUrl + "/dashboard/data/api/run-model",
    beforeSend: function (xhr, settings) {
      xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
    },
    method: "POST",
    data: data,
    global: false,
    error: function (error) {
      //called when there is an error
      swAlert("Error", `${error.statusText}:-> ${error.message}`, "error");
    },
    success: function (results) {
      console.log("results", results)
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




// this is the function will always check if the data is valid
function checkValidDataRequest() {
  const parameters = window.location.pathname;
  let data = {};
  return $.ajax({
    url: webSiteUrl + "/dashboard/data/api/check-valid-data",
    beforeSend: function (xhr, settings) {
      xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
    },
    method: "POST",
    data: data,
    global: false,
    error: function (error) {
      //called when there is an error
      swAlert("Error", `${error.statusText}:-> ${error.message}`, "error");
    },
    success: function (results) {
      // console.log("results", results)
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

// this is the function fetch all information about the current session
function fetchDataSessionInfo(sessionID) {
  const parameters = window.location.pathname;
  let data = {
    "session_id": parseInt(sessionID)
  };
  return $.ajax({
    url: webSiteUrl + "/dashboard/data/api/fetch-data-session-info",
    beforeSend: function (xhr, settings) {
      xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
    },
    method: "POST",
    data: data,
    global: false,
    error: function (error) {
      //called when there is an error
      swAlert("Error", `${error.statusText}:-> ${error.message}`, "error");
    },
    success: function (results) {
      // console.log("results", results)
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


// this function will fetch the columns of the saved file
function fetchDataFileColumns(sessionID) {
  return $.ajax({ // should return to can access from $.when()
    method: "POST",
    cache: false,
    // processData: false,
    // contentType: false,
    timeout: 300000, // 5 minutes
    url: webSiteUrl + "/dashboard/data/api/get-columns",
    // dataType: "json",
    data: {
      'session_id': parseInt(sessionID)
    },
    beforeSend: function (xhr, settings) {
      xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
    },
    /*  success: function (data) {
         for(let c of data){
             columnsList.push(c);
         }

     }, */
    error: function (error) {
      //called when there is an error
      swAlert("Error", error.message, "error");
      //console.log(e.message);
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

// this function will send not validate columns
function notValidateColumnsRequest(notValideCols) {
  // check if the session has id
  const sessionID = extractLastSessionID();
  // this function when memeber want to validate the data type in dual dialog box
  return $.ajax({ // should return to can access from $.when()
    method: "POST",
    cache: false,
    // processData: false,
    // contentType: false,
    timeout: 300000, // 5 minutes
    url: webSiteUrl + "/dashboard/data/api/not-validate-columns",
    // dataType: "json",
    data: {
      "columns": JSON.stringify(notValideCols),
      'session_id': parseInt(sessionID),
    },
    beforeSend: function (xhr, settings) {
      xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
    },
    //  success: function (data, status, xhr) {
    //     alert('not valide columns has been sent');
    //     notValidateColumns = {};
    //
    // },
    error: function (error) {
      //called when there is an error
      swAlert("Error", error.message, "error");
      //console.log(e.message);
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

// delete data file function
function deleteDataFile(sessionID) {
  const parameters = window.location.pathname;
  return $.ajax({ // should return to can access from $.when()
    method: "POST",
    cache: false,
    // processData: false,
    // contentType: false,
    timeout: 300000, // 5 minutes
    url: webSiteUrl + "/dashboard/data/api/delete-file",
    // dataType: "json",
    data: {
      "rows[]": allRowsUpdated,
      'parameters': parameters,
      "session_id": parseInt(sessionID),
    },
    beforeSend: function (xhr, settings) {
      xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
    },
    /*  success: function (data) {
         for(let c of data){
             columnsList.push(c);
         }

     }, */
    error: function (error) {
      //called when there is an error
      swAlert("Error", error.message, "error");
      //console.log(e.message);
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

// this function to get the details of data handler table overview
function fetchDataForDataTable() {
  const sessionID = extractLastSessionID();
  const url = `${webSiteUrl}/dashboard/data/api/fetch-table-overview`;

  // check if sessionID exists
  try {
    return fetch(url, {
        method: "POST",
        headers: {
          "Content-Type": "application/json;charset=utf-8",
          "X-CSRFToken": getCookie('csrftoken')
        },
        body: JSON.stringify({
          sessionID: parseInt(sessionID)
        })
      })
      .then(response => {
        // check the response status
        if (response.ok) {
          return response.json();
        } else {
          // fetchDataForDataTable();
        }
      })
      .catch(error => {
        if (error instanceof TypeError) {
          console.info('Error in connection!!, please wait...');
        } else {
          console.error(error);
        }
      });
  } catch (error) {
    if (error instanceof TypeError) {
      console.info('Error in connection!!, please wait...');
    } else {
      console.error(error);
    }
  }

}


// this function when user want to save changes to data file
function updateMemberDataFile(updatedRowsObj) {
  const sessionID = extractLastSessionID();
  // check the session if it is numeric
  if (Number.isInteger(sessionID) === true) {
    return $.ajax({ // should return to can access from $.when()
      method: "POST",
      cache: false,
      // processData: false,
      // contentType: false,
      timeout: 300000, // 5 minutes
      url: webSiteUrl + "/dashboard/data/api/update-rows",
      // dataType: "json",
      data: {
        "rows": JSON.stringify(updatedRowsObj),
        "session_id": parseInt(sessionID),
      },
      // dataType: "json",
      beforeSend: function (xhr, settings) {
        xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));

      },
      /*  success: function (data) {
           for(let c of data){
               columnsList.push(c);
           }

       }, */
      error: function (error) {
        //called when there is an error
        swAlert("Error", error.message, "error");
        //console.log(e.message);
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

}


// this function will send the type of exported file
function downloadUpdatedFileRequest(fileType) {
  // check if the session has id
  const sessionID = extractLastSessionID();
  // check if the session id exists
  if (Number.isInteger(sessionID) === true) {
    return $.ajax({ // should return to can access from $.when()
      method: "POST",
      cache: false,
      // processData: false,
      // contentType: false,
      timeout: 300000, // 5 minutes
      url: webSiteUrl + "/dashboard/data/api/export",
      xhrFields: {
        responseType: 'blob'
      },
      data: {
        'session_id': parseInt(sessionID),
        'file_type': fileType,
      },
      beforeSend: function (xhr, settings) {
        xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
      },

      error: function (error) {
        //called when there is an error
        swAlert("Error", error.message, "error");
        //console.log(e.message);
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
}

// this function will check if the member is allowed to run the model or not
function checkIsAllowedToRunModel() {
  const sessionID = extractLastSessionID();
  const url = `${webSiteUrl}/dashboard/data/api/check-is-allowed-run-model`;
  try {
    return fetch(url, {
        method: "POST",
        headers: {
          "Content-Type": "application/json;charset=utf-8",
          "X-CSRFToken": getCookie('csrftoken')
        },
        body: JSON.stringify({
          sessionID: parseInt(sessionID)
        })
      })
      .then(response => {
        // check the response status
        if (response.ok) {
          return response.json()
        } else {
          return {
            data: "Error",
            status: response.status,
            statusText: response.statusText,
          }
        }
      })
      .catch(error => {
        if (error instanceof TypeError) {
          console.info('Error in connection!!, please wait...');
        } else {
          console.error(error);
        }
      });
  } catch (error) {
    if (error instanceof TypeError) {
      console.info('Error in connection!!, please wait...');
    } else {
      console.error(error);
    }
  }

}


// this function will check if the session dtypes are valid
function checkSessionDtypesValid() {
  const sessionID = extractLastSessionID();
  const url = `${webSiteUrl}/dashboard/data/api/check-session-dtype-valid`;
  try {
    return fetch(url, {
        method: "POST",
        headers: {
          "Content-Type": "application/json;charset=utf-8",
          "X-CSRFToken": getCookie('csrftoken')
        },
        body: JSON.stringify({
          sessionID: parseInt(sessionID)
        })
      })
      .then(response => {
        // check the response status
        if (response.ok) {
          return response.json()
        } else {
          return {
            data: "Error",
            status: response.status,
            statusText: response.statusText,
          }
        }
      })
      .catch(error => {
        if (error instanceof TypeError) {
          console.info('Error in connection!!, please wait...');
        } else {
          console.error(error);
        }
      });
  } catch (error) {
    if (error instanceof TypeError) {
      console.info('Error in connection!!, please wait...');
    } else {
      console.error(error);
    }
  }

}

// this function will send request to charge extra records
function chargeExtraRecords(formData) {
  const sessionID = extractLastSessionID();
  const url = `${webSiteUrl}/profile/membership/charge-extra-records`;
  try {
    return fetch(url, {
        method: "POST",
        headers: {
          "Content-Type": "application/json;charset=utf-8",
          "X-CSRFToken": getCookie('csrftoken')
        },
        credentials: 'same-origin',
        body: JSON.stringify({
          sessionID: parseInt(sessionID),
          "formData": JSON.stringify(formData),
        })
      })
      .then(response => {
        // check the response status
        if (response.ok) {
          return response.json()
        } else {
          return {
            data: "Error",
            status: response.status,
            statusText: response.statusText,
          }
        }
      })
      .catch(error => {
        if (error instanceof TypeError) {
          console.info('Error in connection!!, please wait...');
        } else {
          console.error(error);
        }
      });
  } catch (error) {
    if (error instanceof TypeError) {
      console.info('Error in connection!!, please wait...');
    } else {
      console.error(error);
    }
  }

}

// this function will fetch all columns in the data file to make the member reselect the columns
function fetchDataFileAllColumns(withDtypes) {
  const sessionID = extractLastSessionID();
  // check if the session has number
  if (Number.isInteger(sessionID) === true) {
    const parameters = window.location.pathname;
    let data = '';
    if (typeof withDtypes !== undefined) {
      data = {
        "with_dtype": true,
        'parameters': parameters
      };
    } else {
      data = {
        'parameters': parameters
      };
    }
    data['sessionID'] = sessionID;
    return $.ajax({ // should return to can access from $.when()
      method: "POST",
      cache: false,
      // processData: false,
      // contentType: false,
      timeout: 300000, // 5 minutes
      data: data,
      url: webSiteUrl + "/dashboard/data/api/get-all-columns",
      // dataType: "json",
      //data: fetchedColumns,
      beforeSend: function (xhr, settings) {
        xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
      },
      /*  success: function (data) {
           for(let c of data){
               columnsList.push(c);
           }

       }, */
      error: function (error) {
        //called when there is an error
        swAlert("Error", error.message, "error");
        //console.log(e.message);
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



}


// this function which will take the picked columns and send them to make the datatable view
function sendPickedColumns() {
  const parameters = window.location.pathname;
  // check if the session has id
  const sessionID = extractLastSessionID();
  // let selectedColumns = JSON.stringify(pickedColumns);
  // let selectedColumns = JSON.parse(pickedColumns);
  // console.log(typeof JSON.stringify(selectedValidateColumns));
  let selectedColumns = {
    "columns": selectedPickedColumns,
    "columns_with_datatype": JSON.stringify(selectedValidateColumns),
    'parameters': parameters,
    "sessionID": parseInt(sessionID),
  };
  // console.log(selectedColumns);
  // throw new Error("Wait");

  // ajax request to data handler init
  return $.ajax({ // should return to can access from $.when()
    method: "POST",
    cache: false,
    // processData: false,
    // contentType: false,
    timeout: 300000, // 5 minutes
    url: webSiteUrl + "/dashboard/data/api/save-columns",
    // dataType: "json",
    data: selectedColumns,
    beforeSend: function (xhr, settings) {
      xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
    },
    error: function (error) {
      //called when there is an error
      swAlert("Error", error.message, "error");
      //console.log(e.message);
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

// this function will validate columns in dualbox
function validateColumnsAjaxRequest(columnsObj) {
  // this function when memeber want to validate the data type in dual dialog box
  // check if the session has id
  const sessionID = extractLastSessionID();
  // check if sessionID not NAN
  if (Number.isInteger(sessionID) === true) {
    return $.ajax({ // should return to can access from $.when()
      method: "POST",
      cache: false,
      // processData: false,
      // contentType: false,
      timeout: 300000, // 5 minutes
      url: webSiteUrl + "/dashboard/data/api/validate-columns",
      // dataType: "json",
      data: {
        "columns": JSON.stringify(columnsObj),
        "session_id": parseInt(sessionID),
      },
      beforeSend: function (xhr, settings) {
        xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
      },
      /*  success: function (data) {
           for(let c of data){
               columnsList.push(c);
           }

       }, */
      error: function (error) {
        //called when there is an error
        swAlert("Error", error.message, "error");
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
  } else {
    // in case no session id
    console.error("No Session ID!!");
  }

}


// this function will fetch all columns in the data file to make the member reselect the columns
function fetchDhTableLastPageInfo() {
  const sessionID = extractLastSessionID();
  // check if the session has number
  if (Number.isInteger(sessionID) === true) {
    return $.ajax({ // should return to can access from $.when()
      method: "POST",
      cache: false,
      // processData: false,
      // contentType: false,
      timeout: 300000, // 5 minutes
      data: {
        "session_id": sessionID
      },
      url: webSiteUrl + "/dashboard/data/api/fetch-last-page-info",
      // dataType: "json",
      //data: fetchedColumns,
      beforeSend: function (xhr, settings) {
        xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
      },
      /*  success: function (data) {
           for(let c of data){
               columnsList.push(c);
           }

       }, */
      error: function (error) {
        //called when there is an error
        swAlert("Error", error.message, "error");
        //console.log(e.message);
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



}
