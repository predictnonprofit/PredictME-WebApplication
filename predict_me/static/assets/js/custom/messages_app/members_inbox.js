"use strict";

const subjectInput = document.querySelector("#member_compose_subject");
const otherSubjectInput = document.querySelector("#other_member_compose_subject"); // other subject input
const msgFileAttachment = document.querySelector("#msg_attachment");
const attachmentFileName = document.querySelector("#msg_attachmen_file_name");
const memberMsgComposeBoxControl = document.querySelectorAll(".member-msg-compose-box-control");
const memberInboxTrashBtn = document.querySelector("#member-inbox-trash-btn");
const memberInboxAllMsgCheckbox = document.querySelector("#memberInboxAllMsgCheckbox");


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
const memberMsgEditor = new Quill('#member_compose_text_msg', {
    theme: 'snow',
    modules: {
        toolbar: toolbarOptions
    }
});

// members messages form
const composeForm = document.querySelector("#members_inbox_compose_form");
composeForm.addEventListener('submit', async (event) => {
    try {
        event.preventDefault();
        const editor = document.querySelector("#member_compose_text_msg"); // the message editor
        // const editor = document.querySelector(".ql-editor");  // the message editor
        const msgSubject = document.querySelector("#member_compose_subject");
        const msgBody = memberMsgEditor.root.innerHTML;
        const otherSubjectStatus = window.getComputedStyle(otherSubjectInput).display;
        const formData = new FormData();

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
        const sendRequest = await requestSendMemberMessage(formData);
        // check if there is any error
        if (sendRequest['is_error'] == true) {
            Swal.fire("Error", sendRequest['msg'], "error");
            addOrRemoveCssClassForNodeList(memberMsgComposeBoxControl, ["disabled", "progress-cursor"], "remove");
            memberMsgEditor.enable();
            msgFileAttachment.disabled = false;
        } else {
            displayTopNotification("Message sent successfully", 'success');
            addOrRemoveCssClassForNodeList(memberMsgComposeBoxControl, ["disabled", "progress-cursor"], "remove");
            msgFileAttachment.disabled = false;
            memberMsgEditor.enable();
            memberMsgEditor.setText("");
            attachmentFileName.innerText = "";
            emptyValuesNodelist(memberMsgComposeBoxControl);
            otherSubjectInput.classList.add("d-none");
            $('#kt_inbox_compose').modal('hide');
        }


    } catch (error) {
        console.error(error.message);
        // Swal.fire('Error', error.message, 'error');
        displayTopNotification(error.message, 'danger');
    }
});


// trash btn event
memberInboxTrashBtn.addEventListener("click", event => {
    const allMsgs = document.querySelectorAll(".member-inbox-msg-checkbox:checked");
    // check if there is messages selected
    if (allMsgs.length <= 0) {
        displayTopNotification("You have to select message to delete", 'danger');
    } else {
        displayTopNotification("Message(s) deleted successfully!", 'success');
    }
});

// check box for check all messages in member inbox
memberInboxAllMsgCheckbox.addEventListener("change", event => {
    const checked = event.currentTarget.checked;
    const allMemberMsgs = document.querySelectorAll(".member-inbox-msg-checkbox");
    if (checked === true) {
        allMemberMsgs.forEach(item => {
            item.checked = true;
        });
    } else {
        allMemberMsgs.forEach(item => {
            item.checked = false;
        });
    }
});