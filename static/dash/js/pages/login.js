/**
 * Custom Js
 */

$(document).ready(function(){
  "use strict";

  $("body").on('click', '.toggle-password', function() {
    $(this).toggleClass("bx bx-hide bx bx-show");
    var input = $("#password");
    if (input.attr("type") === "password") {
      input.attr("type", "text");
    } else {
      input.attr("type", "password");
    }

  });


})
