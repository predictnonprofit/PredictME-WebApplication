"use strict";

const scrollElement = document.querySelector(".dh-wrapper");


const nextBtn = document.querySelector("#nextBtn");
const ulElement = document.querySelector(".StepProgress");
nextBtn.addEventListener("click", (event) => {
  setInterval(() => {
    // document.querySelector("#dhModalPleaseWait").className = "d-none";
    drawClassifiers("CCDDDDD")
  }, 2000);

});


// this function will draw the Classifiers names
function drawClassifiers(classifierName) {
  if (ulElement.lastElementChild === null) {
    const newChild = document.createElement("li");
    newChild.className = "StepProgress-item current animate__animated";
    newChild.innerHTML = `<strong> ${classifierName} </strong>`;
    // newChild.appendChild(childText);
    ulElement.appendChild(newChild);
  } else {
    // if there are items already
    // get the last child
    const lastChild = ulElement.lastElementChild;
    // check if the item contain current class
    if (lastChild.className.includes("current")) {
      lastChild.className = "StepProgress-item is-done animate__animated animate__fadeInUp";
    } else {
      console.log("not include");
    }
    const newChild = document.createElement("li");
    newChild.className = "StepProgress-item current";
    newChild.innerHTML = `<strong> ${classifierName} </strong>`;
    // newChild.appendChild(childText);
    ulElement.appendChild(newChild);
  }
  scrollElement.scrollTop = scrollElement.scrollHeight; // to fix the scrollbar to bottom
}

// this function will connect using webSocket
function runSocket() {
  const sessionID = extractLastSessionID();
  let socket = null;
  // validate session id
  if (Number.isInteger(sessionID) === true) {
    try {
      // document.querySelector('#runModalResults').innerHTML = "";
      $("#runModelModal").modal("show");
      $('#runModelModal').modal('handleUpdate');
      let replacedUrl;
      const locOrigin = location.origin;
      const urlObj = new URL(locOrigin);
      // check if the connection protocol is http or https
      if (urlObj.protocol === 'https:') {
        replacedUrl = urlObj.origin.replace("https", "wss").concat("/dashboard/data/ws/run-model");
      } else if (urlObj.protocol === "http:") {
        replacedUrl = urlObj.origin.replace("http", "ws").concat("/dashboard/data/ws/run-model");
      }
      // const replacedUrl = locOrigin.replace(/http|https/gi, "ws").concat("/dashboard/data/ws/run-model");
      // const url = webSiteUrl.replace("http", "ws") + "/dashboard/data/ws/run-model";
      if (!window.WebSocket) alert("WebSocket not supported by this browser");
      // const url = webSiteUrl + "/dashboard/data/api/socket";
      // console.info(replacedUrl)
      socket = new WebSocket(replacedUrl);
      // if (socket.readyState == WebSocket.OPEN) {
      //   console.log("oelsadfi")
      // }
      socket.onopen = function open() {
        // console.log('WebSockets connection established.');
        socket.send(JSON.stringify({
          "message": 'RUN_THE_MODEL',
          "sessionID": sessionID
        }));
      };


      // when get message from the server
      socket.onmessage = function (event) {
        // donorPredictedStatsVal, f1ScoreVal, thresholdVal
        const socketData = JSON.parse(event.data);
        if (socketData['is_reserved'] === false) {
          drawClassifiers(socketData['msg']);
        } else {
          if (socketData['key_value'] === 'threshold') {
            $("#thresholdVal").html(socketData['msg']);
          } else if (socketData['key_value'] === 'f1_score') {
            $("#f1ScoreVal").html(socketData['msg']);
          } else if (socketData['key_value'] === 'donor_predicted_states') {
            $("#donorPredictedStatsVal").html(socketData['msg']);
          }
        }

        if (socketData['msg'] === "Complete Successfully!") {
          // console.log(event);
          socket.close();
          console.info("Delete all session ids saved..."); // for developments only
          window.sessionStorage.clear();
          $("#dhRunModelAlert").fadeIn();
          setTimeout(function () {
            window.location.href = webSiteUrl + "/profile/history";
          }, 2000);
        }
      };

      // onclose connection
      socket.onclose = function (event) {
        if (event.wasClean === true) {
          // console.log(event)
          socket.close();
          // alert(`[close] Connection closed cleanly, code=${event.code} reason=${event.reason}`);
          // console.log(event);
          // swAlert("Info", `[close] Connection closed cleanly, code=${event.code} reason=${event.reason}`, "info");
          // $("#runModelModal").modal("hide");
        } else {
          // e.g. server process killed or network down
          // event.code is usually 1006 in this case
          // console.info(event);
          socket.close();
          // alert('[close] Connection died');
          swAlert("Error", "There is problem(s) with the connection!!!", "error");
          // document.querySelector('#runModalResults').innerHTML = "";
          // $("#runModelModal").modal("hide");
        }

      };

      // onerror
      socket.onerror = function (error) {
        // alert(`[error] ${error.message}`);
        console.error(error);
        swAlert("Error", `[error] ${error.message}`, "error");
        socket.close();
      };

      // close
      //socket.close();
    } catch (error) {
      // console.error(error);
      console.error(error);
      socket.close();
    }
  }

}