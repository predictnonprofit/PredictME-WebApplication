"use strict";

// Class definition
const KTjQVMapDemo = function () {

    const sample_data = {
        "ru": "23",
        "us": "20",
        // "us": "14624.18",
    };
    // Private functions

    const setupMap = async function (name) {
        // colors array
        const warningColors = ['bg-diagonal', 'bg-diagonal-light-warning'];
        const mapFullWrapper = document.querySelector('#map-full-wrapper');
        const wrapperLoaderIcon = mapFullWrapper.querySelector('div.dashboard-loader');
        const wrapperCardElement = mapFullWrapper.querySelector('div.card-custom');
        const wrapper = document.querySelector("#map-wrapper");
        const noWrapper = document.querySelector('#no-map-wrapper');
        const body = document.querySelector("#noMapBody");
        const fetchDataRequest = await fetchDataToSessionDashboard('geo_location_fields');
        const geoLocationData = fetchDataRequest['data']['geo_location_data'];

        // check if there geo-location data
        if (geoLocationData !== null) {
            // remove the d-none class from the wrapper
            wrapper.classList.remove("d-none");
            // hide the loader icon
            wrapperLoaderIcon.classList.add('d-none');
            const data = {
                map: 'world_en',
                // map: 'iraq',
                backgroundColor: '#a5bfdd',
                // backgroundColor: null,
                color: '#ffffff',
                hoverOpacity: 0.7,
                selectedColor: '#666666',
                enableZoom: true,
                showTooltip: true,
                values: sample_data,
                scaleColors: ['#C8EEFF', '#006491'],
                normalizeFunction: 'polynomial',
                onRegionOver: function (event, code) {
                    //sample to interact with map
                    if (code == 'ca') {
                        event.preventDefault();
                    }
                },
                onRegionClick: function (element, code, region) {
                    //sample to interact with map
                    const message = 'You clicked "' + region + '" which has the code: ' + code.toUpperCase();
                    const d = sample_data[code];
                    console.log(d);;
                    alert(message);
                }
            };

            // data.map = name + '_en';

            const map = jQuery('#data_session_dashboard_jqvmap');

            map.width(map.parent().width());
            map.vectorMap(data);
        } else {
            // change the color of the card
            wrapperCardElement.classList.add(...warningColors);
            // hide the loader icon
            wrapperLoaderIcon.classList.add('d-none');
            // hide the wrapper first
            wrapper.classList.add('d-none');
            // remove the d-none class from the wrapper
            noWrapper.classList.remove("d-none");
            body.classList.add("h5");
            body.innerHTML = "No Geo location Data";
        }
    }

    const setupMaps = function () {
        setupMap("world");
        // setupMap("usa");
        // setupMap("europe");
        // setupMap("russia");
        // setupMap("germany");
    }

    return {
        // public functions
        init: function () {
            // default charts
            setupMaps();

            KTUtil.addResizeHandler(function () {
                setupMaps();
            });
        }
    };
}();

jQuery(document).ready(function () {
    KTjQVMapDemo.init();
});