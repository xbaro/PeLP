'use strict';

document.addEventListener("DOMContentLoaded", function () {
    // Initialize Bootstrap Toasts
    var toastElList = [].slice.call(document.querySelectorAll('.toast'))
    var toastList = toastElList.map(function(toastEl) {
      return new bootstrap.Toast(toastEl)
    });
});
