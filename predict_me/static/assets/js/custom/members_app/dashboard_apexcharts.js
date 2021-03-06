"use strict";

// Shared Colors Definition
const primary = '#6993FF';
const success = '#1BC5BD';
const info = '#8950FC';
const warning = '#FFA800';
const danger = '#F64E60';

// Class definition
function generateBubbleData(baseval, count, yrange) {
    var i = 0;
    var series = [];
    while (i < count) {
        var x = Math.floor(Math.random() * (750 - 1 + 1)) + 1;;
        var y = Math.floor(Math.random() * (yrange.max - yrange.min + 1)) + yrange.min;
        var z = Math.floor(Math.random() * (75 - 15 + 1)) + 15;

        series.push([x, y, z]);
        baseval += 86400000;
        i++;
    }
    return series;
}

function generateData(count, yrange) {
    var i = 0;
    var series = [];
    while (i < count) {
        var x = 'w' + (i + 1).toString();
        var y = Math.floor(Math.random() * (yrange.max - yrange.min + 1)) + yrange.min;

        series.push({
            x: x,
            y: y
        });
        i++;
    }
    return series;
}

var KTApexChartsDemo = function () {
    // Private functions

    var _trainingTestingChart = async function () {
        const trainingAndTestingFullWrapper = document.querySelector('#training-and-testing-full-wrapper');
        const wrapperLoaderIcon = trainingAndTestingFullWrapper.querySelector('div.dashboard-loader');
        const wrapperCardElement = trainingAndTestingFullWrapper.querySelector('div.card-custom');
        const wrapper = document.querySelector("#trainAndTestWrapper");
        const noWrapper = document.querySelector("#noTrainingAndTestingWrapper");
        const body = document.querySelector('#noTrainingAndTestingBody');
        const trainTestRequest = await fetchDataToSessionDashboard('training_testing');
        const trainingData = trainTestRequest['data']['training'];
        const testingData = trainTestRequest['data']['testing'];
        const apexChart = "#session_dashboard_training_testing_chart";
        // check if the training and testing data not null
        if ((trainingData !== false) && (testingData !== false)) {
            // remove the d-none class from the wrapper
            wrapper.classList.remove("d-none");
            // hide the loader icon
            wrapperLoaderIcon.classList.add('d-none');
            const options = {
                dataLabels: {
                    enabled: true,
                    formatter: function (val) {
                        const newVal = Math.round(val);
                        return newVal.toString() + "%";
                    },

                },
                series: [trainingData, testingData],
                labels: ["Train", "Test"],
                chart: {
                    width: 380,
                    type: 'donut',
                },
                responsive: [{
                    breakpoint: 480,
                    options: {
                        chart: {
                            width: 200
                        },
                        legend: {
                            position: 'bottom'
                        }
                    }
                }],
                colors: [primary, success, warning, danger, info]
            };

            const chart = new ApexCharts(document.querySelector(apexChart), options);
            chart.render();
        } else {
            // hide the loader icon
            wrapperLoaderIcon.classList.add('d-none');
            // hide the wrapper first
            wrapper.classList.add('d-none');
            // remove the d-none class from the wrapper
            noWrapper.classList.remove("d-none");
            body.classList.add("h5");
            body.innerHTML = trainTestRequest['data']['donation_columns'];
        }

    }

    var _sessionDashboardImportantFeaturesChart = async function () {
        const importantFeaturesFullWrapper = document.querySelector("#important-features-full-wrapper");
        const wrapperLoaderIcon = importantFeaturesFullWrapper.querySelector('div.dashboard-loader');
        const wrapperCardElement = importantFeaturesFullWrapper.querySelector('div.card-custom');
        const wrapper = document.querySelector("#importantFeaturesWrapper");
        const noWrapper = document.querySelector("#noImportantFeaturesWrapper");
        const body = document.querySelector("#noImportantFeaturesBody");
        const fetchDataRequest = await fetchDataToSessionDashboard('important_features');
        const featureImportanceLabels = fetchDataRequest['data']['labels'];
        const featureImportanceValues = fetchDataRequest['data']['values'];
        const apexChart = "#session_dashboard_important_features_chart";
        // check if the values are array contain values
        if (Array.isArray(featureImportanceValues) === true) {

            // remove the d-none class from the wrapper
            wrapper.classList.remove("d-none");
            // hide the loader icon
            wrapperLoaderIcon.classList.add('d-none');
            const options = {

                series: [{
                    data: featureImportanceValues.reverse()
                }],
                chart: {
                    type: 'bar',
                    height: 350,
                    /*  events: {
                         beforeMount: function (chartContext, options) {
                             console.log('beforeMount');
                         },
                         mounted: function (chartContext, options) {
                             console.log('mounted');
                         },
                     }, */
                },
                plotOptions: {
                    bar: {
                        borderRadius: 4,
                        horizontal: true,
                    }
                },
                dataLabels: {
                    enabled: false
                },
                legend: {
                    show: true,
                    position: 'bottom'
                },
                xaxis: {
                    categories: featureImportanceLabels.reverse(),
                }
            };

            const chart = new ApexCharts(document.querySelector(apexChart), options);
            chart.render();
        } else {
            // colors array
            const warningColors = ['bg-diagonal', 'bg-diagonal-light-warning'];
            // change the color of the card
            wrapperCardElement.classList.add(...warningColors);
            // hide the loader icon
            wrapperLoaderIcon.classList.add('d-none');
            // hide the wrapper first
            wrapper.classList.add('d-none');
            // remove the d-none class from the wrapper
            noWrapper.classList.remove("d-none");
            body.classList.add("h5");
            body.innerHTML = featureImportanceValues;
        }

    }

    return {
        // public functions
        init: function () {
            _trainingTestingChart();
            _sessionDashboardImportantFeaturesChart();
        }
    };
}();

jQuery(document).ready(function () {
    KTApexChartsDemo.init();
});