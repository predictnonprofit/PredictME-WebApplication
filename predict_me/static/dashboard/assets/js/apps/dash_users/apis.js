"use strict";

// this function to get the details of data handler table overview
function fetchMemberDetails(memberID, controllerSignal) {
  const url = `${webSiteUrl}/dashboard/users/api/fetch-member-details`;

  // check if sessionID exists
  try {
    return fetch(url, {
        method: "POST",
        signal: controllerSignal,
        headers: {
          "Content-Type": "application/json;charset=utf-8",
          "X-CSRFToken": getCookie('csrftoken')
        },
        body: JSON.stringify({
          "memberID": parseInt(memberID)
        })
      })
      .then(response => {
        // check the response status
        if ((response.ok === true) && (response.status === 200)) {
          return response.json();
        } else {
          fetchMemberDetails();
        }
      })
      .catch(error => {
        if (error.name === 'AbortError'){
          console.error('Fetch aborted');
        }
        if (error instanceof TypeError) {
          console.info('Error in connection!!, please wait...');
        } else {
          console.error(error);
        }
      });
  } catch (error) {

    if (error instanceof TypeError) {
      console.info('Error in connection!!, please wait...');
    }else {
      console.error(error);
    }
  }

}
