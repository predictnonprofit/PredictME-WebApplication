// let webSiteUrl = window.location.origin;


// this is the function fetch all information about the current session
function fetchMemberInvoicesRequest(startDate, endDate, invoiceOrTrans) {
  let url;
  if (invoiceOrTrans === "trans") {
    url = webSiteUrl + "/profile/invoices/members/api/grab-member-transactions";
  } else {
    url = webSiteUrl + "/profile/invoices/members/api/grab-member-invoices";
  }
  let data = {
    startDate: startDate,
    endDate: endDate
  };
  return $.ajax({
    url: url,
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


// this function will fetch the train and test for data handler session
function fetchDataToSessionDashboard(dataKeyName) {
  const href = location.href;
  const historyID = href.split("/").pop();
  const url = `${webSiteUrl}/dashboard/data/api/fetch-session-dashboard-session`;
  try {
    return fetch(url, {
        method: "POST",
        headers: {
          "Content-Type": "application/json;charset=utf-8",
          "X-CSRFToken": getCookie('csrftoken')
        },
        body: JSON.stringify({
          historyID: parseInt(historyID),
          "keyName": dataKeyName
        })
      })
      .then(response => {
        // check the response status
        if ((response.statusText === 'OK') && (response.status === 200)) {
          return response.json();
        }
        /* else {
          fetchTrainAndTest();
        } */
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


// this function will upgrade to new membership
async function requestUpgradeToNewMembership(newCreditCardData, url) {
  try {
    // console.log(arguments);

    const requestPromise = await axios.post(url, newCreditCardData, {
      headers: {
        "Content-Type": "application/json;charset=utf-8",
        "X-CSRFToken": getCookie('csrftoken')
      }
    });
    // const promiseData = requestPromise.then(response => response['data']);
    return requestPromise['data'];
    /* return fetch(url, {
        method: "POST",
        headers: headers,
        body: JSON.stringify({
          "membershipName": membershipSlug
        })
      })
      .then(response => {
        // check the response status
        if (response.ok) {
          return response.json();
        }
      })
      .catch(error => {
        console.error(error);
      }); */
  } catch (error) {
    console.error(error);
  }

}


// this function will send message request api
async function requestSendMemberMessage(formData, url) {
  try {
    // "Content-Type": "application/json;charset=utf-8",
    // "Content-Type": "multipart/form-data;charset=utf-8",
    // "Content-Type": "multipart/form-data; boundary=blob",
    // "Content-Type": 'application/x-www-form-urlencoded',
    const headers = new Headers({
      "X-CSRFToken": getCookie('csrftoken'),
      'Accept': 'application/json',
      'X-Requested-With': 'XMLHttpRequest'
    });

    return await fetch(url, {
        method: "POST",
        headers: headers,
        body: formData
      })
      .then(response => {
        // check the response status
        if (response.ok) {
          return response.json();
        }
      })
      .catch(error => {
        console.error(error);
      });
  } catch (error) {
    console.error(error);
  }

}