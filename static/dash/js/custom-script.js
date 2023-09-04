/**
 * Custom Js
 */

$(document).ready(function(){
  "use strict";

  // To-do
  $('#btn-generate').prop('disabled', true)
  
  if ( $('.ideas').html().length > 0 ) {
    $('#btn-generate').html('Re-Generate Paragraph')
    $('#btn-generate').prop('disabled', false)
  }

})

/* Paulse effect */
$(function blink() {
  $('.blink_me').fadeOut(500).fadeIn(700, blink)
})

// $('.generate-btn').click( function() {
//   console.log('Loading')
//   $("#bg-spinner").fadeOut("slow");
// })

jQuery(function ($) {
/* Ajax calls backend spinner */
  // $(document).ajaxSend(function () {
  //   $('#bg-spinner').fadeIn(500);
  // });

  /* button click backend spinner */
  $('.btn-generate').click(function() {
    $.ajax({
      type: 'GET',
      success: function(data) {
        var d = $.parseJSON(data);
        alert(d.Test);
      }

    }).done(function () {
      setTimeout(function () {
        $("#bg-spinner").fadeOut("slow");
      }, 700);
    });
  });
});

function copyToClipboard(element) {
  var $temp = $("<input>");
  $("body").append($temp);
  $temp.val($(element).text().trim()).select();
  document.execCommand("copy");
  $temp.remove();
  alert('Text copied successfully!')
}

function startTyping(txt, speed=10) {
  var i=0;

  typeWriter()

  function typeWriter() {
    console.log(txt.length)
    if (i < txt.length) {
      document.getElementById("ai-response-text").innerHTML += txt.charAt(i);
      i++;
      setTimeout(typeWriter(), speed);
    }
  }
}