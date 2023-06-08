$(document).ready(function(){
  "use strict";
  var maxLength = 250;

  $('.audience_counter').text($('#audience').val().length+'/'+maxLength);
  $('.keywords_counter').text($('#keywords').val().length+'/'+maxLength);


  $('#audience').keyup(function() {
    var curr_textlen = $(this).val().length;

    var textlen = maxLength - curr_textlen;

    $('.audience_counter').text(curr_textlen+'/'+maxLength);
  });

  $('#keywords').keyup(function() {
    var maxLength = 250;
    var curr_textlen = $(this).val().length;

    var textlen = maxLength - curr_textlen;

    $('.keywords_counter').text(curr_textlen+'/'+maxLength);
  });

  $('input').keyup( function () {

    $('#btn-generate').prop('disabled', true)

    if ( $('#audience').val().length > 5 && $('#keywords').val().length > 2 ) {
      $('#btn-generate').prop('disabled', false)
    }

  })

  $('#blog_post').change( function(){
    console.log('Selected Blog: ' + $(this).val())
  })

});