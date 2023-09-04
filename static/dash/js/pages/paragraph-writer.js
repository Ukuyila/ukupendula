$(document).ready(function(){
  "use strict";

  const maxLength = 300;

  $('.title_counter').text($('#paragraph_topic').val().length+'/'+maxLength);

  $('#paragraph_topic').keyup(function() {
    var curr_textlen = $(this).val().length;

    $('#btn-generate').prop('disabled', true)

    if ( curr_textlen > 10 ) {
      $('#btn-generate').prop('disabled', false)
    }

    var textlen = maxLength - curr_textlen;

    $('.title_counter').text(curr_textlen+'/'+maxLength);
  });


});