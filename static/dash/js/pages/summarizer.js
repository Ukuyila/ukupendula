$(document).ready(function(){
  "use strict";
  const lcMaxLength = 14000;
  const stMaxLength = 160;

  $('.prompt_counter').text($('#long_content').val().length+'/'+lcMaxLength);

  $('#long_content').keyup(function() {
    var curr_textlen = $(this).val().length;

    var textlen = lcMaxLength - curr_textlen;

    $('.prompt_counter').text(curr_textlen+'/'+lcMaxLength);
  });

  $('.title_counter').text($('#summary_title').val().length+'/'+stMaxLength);

  $('#summary_title').keyup(function() {
    
    var curr_textlen = $(this).val().length;

    $('#btn-generate').prop('disabled', true)

    if ( curr_textlen > 10 ) {
      $('#btn-generate').prop('disabled', false)
    }

    var textlen = stMaxLength - curr_textlen;

    $('.title_counter').text(curr_textlen+'/'+stMaxLength);
  });


});