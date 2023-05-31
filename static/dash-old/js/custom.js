/**
 * Custom Js
 */

$(document).ready(function(){
  "use strict";

  // To-do
  // Do word counters for all inputs


})

// function successToast() {

// }

function copyToClipboard(element) {
  var $temp = $("<input>");
  $("body").append($temp);
  $temp.val($(element).text()).select();
  document.execCommand("copy");
  $temp.remove();
  alert('Text copied successfully!')
}