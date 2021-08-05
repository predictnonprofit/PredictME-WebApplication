'use strict';

// Class definition
let KTDualListbox = function () {
    let genericFiltersDualBox = function () {
        // Dual Listbox
        var $this = $('#generic_filters_dual_listbox');

        // get options
        var options = [];
        $this.children('option').each(function () {
            var value = $(this).val();
            var label = $(this).text();
            options.push({
                text: label,
                value: value
            });
        });

        // init dual listbox
        var dualListBox = new DualListbox($this.get(0), {
            addEvent: function (value) {
                console.log(value);
            },
            removeEvent: function (value) {
                console.log(value);
            },
            availableTitle: "Generic Filters Options",
            selectedTitle: "Selected Filters",
            addButtonText: "<i class='flaticon2-next'></i>",
            removeButtonText: "<i class='flaticon2-back'></i>",
            addAllButtonText: "<i class='flaticon2-fast-next'></i>",
            removeAllButtonText: "<i class='flaticon2-fast-back'></i>",
            options: options,
        });
    };
    let revenuReportsDualBox = function () {
        // Dual Listbox
        var $this = $('#revenu_filters_dual_listbox');

        // get options
        var options = [];
        $this.children('option').each(function () {
            var value = $(this).val();
            var label = $(this).text();
            options.push({
                text: label,
                value: value
            });
        });

        // init dual listbox
        var dualListBox = new DualListbox($this.get(0), {
            addEvent: function (value) {
                console.log(value);
            },
            removeEvent: function (value) {
                console.log(value);
            },
            availableTitle: "Revenue Custom Filters",
            selectedTitle: "Selected Filters",
            addButtonText: "<i class='flaticon2-next'></i>",
            removeButtonText: "<i class='flaticon2-back'></i>",
            addAllButtonText: "<i class='flaticon2-fast-next'></i>",
            removeAllButtonText: "<i class='flaticon2-fast-back'></i>",
            options: options,
        });
    };





    return {
        // public functions
        init: function () {
            genericFiltersDualBox();
            revenuReportsDualBox();

        },
    };
}();

jQuery(document).ready(function () {
    KTDualListbox.init();
});
