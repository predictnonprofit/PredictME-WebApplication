"use strict";
const subjectInput = document.querySelector("#member_reply_subject");
const otherSubjectInput = document.querySelector("#other_member_reply_subject"); // other subject input
const msgFileAttachment = document.querySelector("#reply_attachment");
const attachmentFileName = document.querySelector("#reply_attachmen_file_name");
const memberMsgComposeBoxControl = document.querySelectorAll(".member-msg-compose-box-control");
const memberInboxTrashBtn = document.querySelector("#member-inbox-trash-btn");
const memberInboxAllMsgCheckbox = document.querySelector("#memberInboxAllMsgCheckbox");
const memberInboxListViewItems = document.querySelectorAll(".member-inbox-list-view-item");
const composeForm = document.querySelector("#members_inbox_reply_form");

const toolbarOptions = [
    [{
        'header': [1, 2, 3, 4, 5, 6, false]
    }],
    // [{ 'size': ['small', false, 'large', 'huge'] }],  // custom dropdown
    ['bold', 'italic', 'underline', 'link'], // toggled buttons
    [{
        'direction': 'rtl'
    }], // text direction
    ['blockquote', 'code-block'],
    [{
        'list': 'ordered'
    }, {
        'list': 'bullet'
    }],

    ['clean'] // remove formatting button
];
const memberMsgEditor = new Quill('#member_reply_text_msg', {
    theme: 'snow',
    modules: {
        toolbar: toolbarOptions
    }
});

// hide and show the other subject input
subjectInput.addEventListener('change', event => {
    const selectedValue = event.target.value;
    const input = event.target;
    if (selectedValue === "other") {
        otherSubjectInput.classList.remove("d-none");
    } else {
        otherSubjectInput.classList.add("d-none");
    }
});

msgFileAttachment.addEventListener("change", event => {
    const fileInput = event.target.files[0];
    attachmentFileName.innerText = fileInput.name;
});

composeForm.addEventListener('submit', async (event) => {
    try {
        event.preventDefault();
        const url = composeForm.action;
        const editor = document.querySelector("#member_reply_text_msg"); // the message editor
        // const editor = document.querySelector(".ql-editor");  // the message editor
        const msgSubject = document.querySelector("#member_reply_subject");
        const msgBody = memberMsgEditor.root.innerHTML;
        const msgId = document.querySelector('#msg_id');
        const otherSubjectStatus = window.getComputedStyle(otherSubjectInput).display;

        const formData = new FormData();

        formData.append("reply", msgId.value);

        // check if the message subject is empty or not
        if (!msgSubject.value) { // if msg subject is empty
            msgSubject.classList.remove('border-0', "is-valid");
            msgSubject.classList.add('is-invalid', "in-valid-placeholder");
            throw new Error("Message subject is required!");
        } else {
            msgSubject.classList.add("border-0", "is-valid");
            msgSubject.classList.remove('is-invalid', "in-valid-placeholder");
            formData.append("subject", msgSubject.value);
        }

        // check if the message is empty 
        if (memberMsgEditor.getLength() === 1) {
            editor.classList.add("is-invalid", "in-valid-placeholder", "border-1", "border-danger");
            throw new Error("Message content is required!");

        } else {
            editor.classList.remove("is-invalid", "in-valid-placeholder", "border-1", "border-danger");
            formData.append("message", msgBody);
        }

        // check if the user upload file attachment
        if (msgFileAttachment.files.length > 0) {
            const tmpFile = msgFileAttachment.files[0];
            formData.append("attachment", tmpFile);
        }

        // check if the other subject input is enabled
        if (otherSubjectStatus !== "none") {
            // validate it the input empty
            if (!otherSubjectInput.value) {
                otherSubjectInput.classList.remove('border-0', "is-valid");
                otherSubjectInput.classList.add('is-invalid', "in-valid-placeholder");
                throw new Error("Subject is required!");
            } else {
                otherSubjectInput.classList.add("border-0", "is-valid");
                otherSubjectInput.classList.remove('is-invalid', "in-valid-placeholder");
                formData.delete("subject");
                formData.append("other_subject", otherSubjectInput.value);
            }

        }
        // disable all message inputs before send the message
        memberMsgEditor.disable();
        msgFileAttachment.disabled = true;
        addOrRemoveCssClassForNodeList(memberMsgComposeBoxControl, ["disabled", "progress-cursor"], "add");
        const sendRequest = await requestSendMemberMessage(formData, url);
        // check if there is any error
        if (sendRequest['is_error'] == true) {
            Swal.fire("Error", sendRequest['msg'], "error");
            addOrRemoveCssClassForNodeList(memberMsgComposeBoxControl, ["disabled", "progress-cursor"], "remove");
            memberMsgEditor.enable();
            msgFileAttachment.disabled = false;
        } else {
            displayTopNotification("Reply sent successfully", 'success');
            addOrRemoveCssClassForNodeList(memberMsgComposeBoxControl, ["disabled", "progress-cursor"], "remove");
            msgFileAttachment.disabled = false;
            memberMsgEditor.enable();
            memberMsgEditor.setText("");
            attachmentFileName.innerText = "";
            emptyValuesNodeList(memberMsgComposeBoxControl);
            otherSubjectInput.classList.add("d-none");
            setTimeout(() => {location.reload();}, 1000);
        }


    } catch (error) {
        console.error(error.message);
        // Swal.fire('Error', error.message, 'error');
        displayTopNotification(error.message, 'danger');
    }
});