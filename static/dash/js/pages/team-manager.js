$(document).ready(function(){
  "use strict";
  var maxLength = 200;
  var emailMaxLength = 100;
  var addrMaxLength = 300;
  var descMaxLength = 300;

  $('.title_counter').text($('#biz_name').val().length+'/'+maxLength);
  $('.industry_counter').text($('#industry').val().length+'/'+maxLength);
  $('.email_counter').text($('#biz_email').val().length+'/'+emailMaxLength);
  $('.address_counter').text($('#biz_address').val().length+'/'+addrMaxLength);
  $('.descr_counter').text($('#biz_description').val().length+'/'+descMaxLength);


  $('#biz_name').keyup(function() {
    var curr_textlen = $(this).val().length;

    var textlen = maxLength - curr_textlen;

    $('.title_counter').text(curr_textlen+'/'+maxLength);
  });

  $('#industry').keyup(function() {
    var curr_textlen = $(this).val().length;

    var textlen = maxLength - curr_textlen;

    $('.industry_counter').text(curr_textlen+'/'+maxLength);
  });

  $('#biz_email').keyup(function() {
    var curr_textlen = $(this).val().length;

    var textlen = emailMaxLength - curr_textlen;

    $('.email_counter').text(curr_textlen+'/'+emailMaxLength);
  });

  $('#biz_address').keyup(function() {
    
    var curr_textlen = $(this).val().length;

    var textlen = addrMaxLength - curr_textlen;

    $('.address_counter').text(curr_textlen+'/'+addrMaxLength);
  });

  $('#biz_description').keyup(function() {

    var curr_textlen = $(this).val().length;

    var textlen = descMaxLength - curr_textlen;

    $('.descr_counter').text(curr_textlen+'/'+descMaxLength);
  });

});