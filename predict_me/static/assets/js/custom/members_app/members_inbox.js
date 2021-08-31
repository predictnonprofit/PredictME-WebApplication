"use strict";


const membersSendMsgBtns = document.querySelectorAll('.member-send-msg-btn');

for (const btn of membersSendMsgBtns) {
    btn.addEventListener('click', (event) => {
        alert("Send message btn clicked");
    });
}