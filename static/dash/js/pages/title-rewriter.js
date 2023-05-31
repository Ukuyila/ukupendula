$(document).ready(function(){
  "use strict";

  const maxLength = 200;

  $('.title_counter').text($('#old_title').val().length+'/'+maxLength);

  $('#old_title').keyup(function() {
    var curr_textlen = $(this).val().length;

    $('#btn-generate').prop('disabled', true)

    if ( curr_textlen > 10 ) {
      $('#btn-generate').prop('disabled', false)
    }

    var textlen = maxLength - curr_textlen;

    $('.title_counter').text(curr_textlen+'/'+maxLength);
  });

});