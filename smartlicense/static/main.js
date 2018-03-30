'use strict';

var obligationChanger = document.querySelectorAll('.obligation-changer');
var linkChanger = document.querySelectorAll('.link-changer');

var adaptElem = document.getElementById('adapt');
var shareElem = document.getElementById('share');
var resaleElem = document.getElementById('resale');
var noncommercialElem = document.getElementById('noncommercial');

var titleElem = document.getElementById('title-obligations');
var indicateElem = document.getElementById('indicate-adaptions');
var attributionElem = document.getElementById('attribution');

var resultElem = document.getElementById('result-link');

obligationChanger.forEach(function (element) {
    element.addEventListener('change', function () {
        if (adaptElem.checked || shareElem.checked || resaleElem.checked) {
            titleElem.style.display = "block";
            attributionElem.style.display = "flex";
            indicateElem.style.display = adaptElem.checked ? "flex" : "none";
        } else {
            titleElem.style.display = "none";
            attributionElem.style.display = "none";
            indicateElem.style.display = "none";
        }
    });
});

linkChanger.forEach(function (element) {
    element.addEventListener('change', function () {
        var link = 'rights-profile/RP-';
        if (adaptElem.checked)
            link += 'AD-';
        if (shareElem.checked)
            link += 'SH-';
        if (resaleElem.checked)
            link += 'RS-';
        link += 'IP';
        if (noncommercialElem.checked)
            link += '-NC';
        resultElem.href = link;
        resultElem.innerHTML = link;
    });
});
