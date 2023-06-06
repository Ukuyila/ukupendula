$(document).ready(function(){
  "use strict";
  var maxLength = 250;
  $('#blog_idea').keyup(function() {
    var curr_textlen = $(this).val().length;

    var textlen = maxLength - curr_textlen;

    $('.title_counter').text(curr_textlen+'/'+maxLength);
  });

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

    if ( $('#blog_idea').val().length > 5 && $('#keywords').val().length > 2 ) {
      $('#btn-generate').prop('disabled', false)
    }

  })

});