/**
 * Custom Js
 */

$(document).ready(function(){
  "use strict";

  // To-do
  $('#btn-generate').prop('disabled', true)

  // notifcations listener
  setTimeout(() => {
    notificationListener
  }, 5000);
})

function notificationListener() {
  let curr_notifcs_cnt = $('.notifications-count')
  $.ajax({
    type: 'POST',
    url: 'get-notifications',
    data: {
      curr_notifcs_cnt: curr_notifcs_cnt.html(),
      notic_type: 'general',
    },
    success: function (resp) {
      if ( resp.includes('success') ) {
        let responses = JSON.parse(resp)
        console.log(responses)
        
      }
      else {
        error_alert.html(resp).prop('hidden', false)
      }
    }
  })
}

/* Paulse effect */
$(function blink() {
  $('.blink_me').fadeOut(500).fadeIn(700, blink)
})

// $('.generate-btn').click( function() {
//   console.log('Loading')
//   $("#bg-spinner").fadeOut("slow");
// })

/* Ajax calls backend spinner */
jQuery(function ($) {
  $(document).ajaxSend(function () {
    $('#bg-spinner').fadeIn(500);
  });

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
  $temp.val($(element).text()).select();
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