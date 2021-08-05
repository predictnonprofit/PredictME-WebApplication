"use strict";

var KTTreeview = function () {


    var _demo4 = function() {
        $("#kt_tree_4").jstree({
            "core" : {
                "themes" : {
                    "responsive": false
                },
                // so that create works
                "check_callback" : true,
                'data': [{
                        "text": "Your Files",
                        "children": [
                             {
                            "text": "Data.pdf",
                            "icon": "icon-xl la la-file-pdf text-danger"
                        }, 
                        {
                            "text": "Data.csv",
                            "icon": "icon-xl la la-file-csv text-success"
                        }, 
                        {
                            "text": "Data.xlsx",
                            "icon": "icon-xl la la-file-pdf text-danger"
                        }, 
                    
                    ]
                    },
                    
                ]
            },
            "types" : {
                "default" : {
                    "icon" : "fa fa-folder text-primary"
                },
                "file" : {
                    "icon" : "fa fa-file  text-primary"
                }
            },
            "state" : { "key" : "demo2" },
            "plugins" : [ "contextmenu", "state", "types" ],
            "contextmenu": {
                "items": function ($node) {
                    return {
                        "Create": {
                            "label": "Download Data",
                            "icon": "fa fa-file-download kt-font-success",
                            "action": function (obj) {
                                alert("Download " + obj);
                            }
                        },
                        "Delete": {
                            "label": "Delete Your File Data",
                            "icon": "fa fa-trash-alt kt-font-danger",
                            "_class": "kt-font-danger",
                            "action": function (obj) {
                                alert("Delete " + obj);
                            }
                        }
                    };
                }
            }
        });
    }



    return {
        //main function to initiate the module
        init: function () {

            _demo4();
  
        }
    };
}();

jQuery(document).ready(function() {
    KTTreeview.init();
});
