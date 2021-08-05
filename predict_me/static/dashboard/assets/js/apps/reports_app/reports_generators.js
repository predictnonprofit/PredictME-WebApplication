'use strict';
const reportsSpinner = $("#reportsLoaderSpinner");


// this function will return all cookies
function fetchAllCookies(){
    let allCookies = getAllCookies();

    if(allCookies){
        return allCookies;
    }else { 
        return 'No cookies!!!';
    }

    
}



// revenue report generator
function revenueGenerator(displayedColumns){
    runGenerateReportFunc('revenue', displayedColumns);

}


// data-usage report generator
function dataUsageGenerator(displayedColumns){
    runGenerateReportFunc('data_usage', displayedColumns);
}

// extra-records report generator
function extraRecordsGenerator(displayedColumns){
    runGenerateReportFunc('extra_records', displayedColumns);
}

// profit-share report generator
function profitShareGenerator(displayedColumns){
    runGenerateReportFunc('profit_share', displayedColumns);
}

// users reports generator
function usersReportsGenerator(displayedColumns){
    runGenerateReportFunc('users', displayedColumns);
}

// this function will run for all reports it is wrapper for the common ops
function runGenerateReportFunc(reportSectionName, columnsArray){
    let parentWrapper = '';
    let urlName = "";
    if(reportSectionName === "revenue"){
        parentWrapper = $("#revenue-reports-wrapper");
        urlName = "revenue";

    }else if(reportSectionName === "data_usage"){
        parentWrapper = $("#data-usage-reports-wrapper");
        urlName = "data_usage";

    }else if(reportSectionName === "extra_records"){
        parentWrapper = $("#extra-records-reports-wrapper");
        urlName = "extra_records";

    }else if(reportSectionName === "profit_share"){
        parentWrapper = $("#profit-share-reports-wrapper");
        urlName = "profit_share";

    }else if(reportSectionName === "users"){
        parentWrapper = $("#users-reports-wrapper");
        urlName = "users";

    }
    const reportTable = parentWrapper.find('table');
    reportTable.hide()
    reportsSpinner.show();
    setTimeout(function (){
        reportsSpinner.hide();
        reportTable.show();
    }, 2000);
    
    const fetchReportResponse = fetchReportRequest(urlName, columnsArray, fetchAllCookies());
    $.when(fetchReportResponse).done(function (data, textStatus, jqXHR){
        if((textStatus === 'success') && (jqXHR.status === 200)){
            drawReportTable(data, urlName);
        }
    });
}