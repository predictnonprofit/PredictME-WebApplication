// Class definition
var GeneriReportTagify = function () {
    // Private functions
    var userStatusInputTags = function () {
        var input = document.getElementById('gen-filter-users-status'),
            // init Tagify script on the above inputs
            tagify = new Tagify(input, {
                enforceWhitelist: true,
                whitelist: ["All", "Active", "Pending", 'Canceled'],
                dropdown: {
                    position: "input",
                    enabled: 0, // always opens dropdown when input gets focus
                    closeOnSelect: false,

                },
                callbacks: {
                    add: console.log, // callback when adding a tag
                    remove: console.log // callback when removing a tag
                }
                //blacklist: [".NET", "PHP"], // <-- passed as an attribute in this demo
            })


        // "remove all tags" button event listener
        // document.getElementById('kt_tagify_1_remove').addEventListener('click', tagify.removeAllTags.bind(tagify));

    }
    var orgTypeInputTags = function () {
        var input = document.getElementById('gen-filter-users-org-type'),
            // init Tagify script on the above inputs
            tagify = new Tagify(input, {
                dropdown: {
                    position: "input",
                    enabled: 0 // always opens dropdown when input gets focus
                },
                whitelist: ["All", "Higher Education", "Other Education", 'Health related', 'Hospitals and Primary Care', 'Human and Social Services', 'Environment', 'Animal', 'International', 'Religion related', 'Other'],
                //blacklist: [".NET", "PHP"], // <-- passed as an attribute in this demo
            })


        // "remove all tags" button event listener
        // document.getElementById('kt_tagify_1_remove').addEventListener('click', tagify.removeAllTags.bind(tagify));

        // Chainable event listeners
        tagify.on('add', onAddTag)
            .on('remove', onRemoveTag)
            .on('input', onInput)
            .on('edit', onTagEdit)
            .on('invalid', onInvalidTag)
            .on('click', onTagClick)
            .on('dropdown:show', onDropdownShow)
            .on('dropdown:hide', onDropdownHide)

        // tag added callback
        function onAddTag(e) {
            const addedValue = JSON.parse(input.value)[0]['value'];
            if (addedValue === "Other") {
                $("#gen-filter-other-org-type").toggleClass('disabled').removeAttr('disabled').removeClass("not-allowed-cursor");
            }
            // console.log("onAddTag: ", e.detail);
            // console.log("original input value: ", input.value)
            tagify.off('add', onAddTag) // exmaple of removing a custom Tagify event
        }

        // tag remvoed callback
        function onRemoveTag(e) {
            // console.log(e.detail);
            // console.log("tagify instance value:", tagify.value);
            const removedVal = e.detail['data']['value'];
            if (removedVal === "Other") {
                $("#gen-filter-other-org-type").addClass('disabled not-allowed-cursor').attr("disabled", "disabled");
            }

        }

        // on character(s) added/removed (user is typing/deleting)
        function onInput(e) {
            /*  console.log(e.detail);
              console.log("onInput: ", e.detail);*/
        }

        function onTagEdit(e) {
            console.log("onTagEdit: ", e.detail);
        }

        // invalid tag added callback
        function onInvalidTag(e) {
            console.log("onInvalidTag: ", e.detail);
        }

        // invalid tag added callback
        function onTagClick(e) {
            console.log(e.detail);
            console.log("onTagClick: ", e.detail);
        }

        function onDropdownShow(e) {
            console.log("onDropdownShow: ", e.detail)
        }

        function onDropdownHide(e) {
            console.log("onDropdownHide: ", e.detail)
        }
    }



    return {
        // public functions
        init: function () {
            userStatusInputTags();
            orgTypeInputTags();

        }
    };
}();

jQuery(document).ready(function () {
    GeneriReportTagify.init();
});
