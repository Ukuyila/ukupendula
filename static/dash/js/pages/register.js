/**
 * Custom Js
 */

$(document).ready(function(){
  "use strict";

  let reg_btn_container = $('.register-btn-container')

  let submit_btn = $('#register-btn')

  $('#register-btn').prop('disabled', true)

  // To-do
  // Do spam checker
  $('#spam_filter').keyup( function() {
    let filter_val = $(this).val()

    // console.log(filter_val)
    
    reg_btn_container.prop('hidden', true)
    submit_btn.prop('disabled', true)

    if (filter_val==9 || filter_val.toUpperCase()=='NINE' ) {
      reg_btn_container.prop('hidden', false)
      submit_btn.prop('disabled', false)
    }
  })

  $("body").on('click', '.toggle-password1', function() {
    $(this).toggleClass("bx bx-hide bx bx-show");
    var input = $("#password1");
    if (input.attr("type") === "password") {
      input.attr("type", "text");
    } else {
      input.attr("type", "password");
    }

  });

  $("body").on('click', '.toggle-password2', function() {
    $(this).toggleClass("bx bx-hide bx bx-show");
    var input = $("#password2");
    if (input.attr("type") === "password") {
      input.attr("type", "text");
    } else {
      input.attr("type", "password");
    }

  });

})
// window.onloadTurnstileCallback = function () {
//   turnstile.render('#example-container', {
//       sitekey: '0x4AAAAAAAIHVqQZH0ravSu2',
//       callback: function(token) {
//           console.log(`Challenge Success ${token}`);
//       },
//   });
// };

