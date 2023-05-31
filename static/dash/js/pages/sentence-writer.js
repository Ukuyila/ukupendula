$(document).ready(function(){
  "use strict";

  const maxLength = 200;

  $('.title_counter').text($('#old_sentence').val().length+'/'+maxLength);

  $('#old_sentence').keyup(function() {
    var curr_textlen = $(this).val().length;

    $('#btn-generate').prop('disabled', true)
    if ( curr_textlen > 10 ) {
      $('#btn-generate').prop('disabled', false)
      console.log('btn enabled')
    }

    var textlen = maxLength - curr_textlen;

    $('.title_counter').text(curr_textlen+'/'+maxLength);
  });

});