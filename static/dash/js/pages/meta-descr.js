
$(document).ready(function(){
  "use strict";
  const maxLength = 200;
  
  $('.counter').text($('#article_title').val().length+'/'+maxLength);

  if ( $('#article_title').val().length > 10 ) {
    $('#btn-generate').prop('disabled', false)
  }

  $('#article_title').keyup(function() {
    var curr_textlen = $(this).val().length;

    $('#btn-generate').prop('disabled', true)

    if ( curr_textlen > 10 ) {
      $('#btn-generate').prop('disabled', false)
    }

    var textlen = maxLength - $(this).val().length;

    $('.counter').text(curr_textlen+'/'+maxLength);
  });

});