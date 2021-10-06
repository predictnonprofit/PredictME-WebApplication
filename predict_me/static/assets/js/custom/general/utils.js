/*
    This is utility file for general usage
*/

var webSiteUrl = window.location.origin;
const disableAndWaitCursorCssClasses = new Array("disabled", "wait-cursor");

function swAlert(alertTitle, alertMsg, alertType) {
  swal.fire(`${alertTitle}`, `${alertMsg}`, `${alertType}`);
}

// this function will detect the session id, in url or session storage
function extractLastSessionID() {
  let lastSessionID;
  let sessionID;
  const href = window.location.href;
  const hrefArray = href.split("/");
  const urlSessionID = parseInt(hrefArray[hrefArray.length - 2]);
  const sessionStorageID = parseInt(window.sessionStorage.getItem("lastSessionID"));
  // console.log('url session id  ', urlSessionID);
  // console.log('storage session id  ', sessionStorageID);
  // check if the session id in the url or in the sessionStorage
  if (Number.isInteger(urlSessionID) === true) {
    sessionID = urlSessionID;
    window.sessionStorage.clear();
  } else if (Number.isInteger(sessionStorageID) === true) {
    sessionID = sessionStorageID;
  }
  // console.log('final session id  ', sessionID);
  // console.log('#######################################');
  return sessionID;
}

// to print all methods of object
function getMethods(obj) {
  let result = [];
  for (let id in obj) {
    try {
      if (typeof (obj[id]) == "function") {
        result.push(id + ": " + obj[id].toString());
      }
    } catch (err) {
      result.push(id + ": inaccessible");
    }
  }
  return result;
}

// this function to capitalize first letter of string
function capitalizeFirstLetter(string) {
  return string.charAt(0).toUpperCase() + string.slice(1);
}

// this function will send any request to any url, to avoid duplicate codes
function sendRequests(url, name) {
  /**
   * url: request url
   * name: request name, (optional)
   */
  const fullUrl = webSiteUrl + url;
  // check if the session has id
  const sessionID = extractLastSessionID();
  // check if the session in numeric
  if (Number.isInteger(sessionID) === true) {
    return $.ajax({ // should return to can access from $.when()
      method: "POST",
      cache: false,
      // processData: false,
      // contentType: 'application/json',
      timeout: 300000, // 5 minutes
      url: fullUrl,
      dataType: "json",
      data: {
        'session_id': parseInt(sessionID),
        "request_name": name,
      },
      beforeSend: function (xhr, settings) {
        xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
      },
      /* success: function (response) {
        console.log(response);
        console.warn("Connection Success!!");

      }, */
      error: function (jqXHR, textStatus, throwError) {
        console.error(jqXHR);
        //called when there is an error
        swAlert("Error", textStatus, "error");
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

// generate crash report url btn
const generateCrashReportUrlBtn = $("#generateCrashReportUrlBtn");
generateCrashReportUrlBtn.on('click', (event) => {
  const crashUrlInput = $('#id_url');
  crashUrlInput.val(location.href);
});
