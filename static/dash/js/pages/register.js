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


})
