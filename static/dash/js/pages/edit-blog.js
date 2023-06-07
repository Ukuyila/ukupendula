$(document).ready(function(){
  "use strict";
  var maxLength = 250;

  $('#blog-title').keyup(function() {
    var curr_textlen = $(this).val().length;

    var textlen = maxLength - curr_textlen;

    $('.title_counter').text(curr_textlen+'/'+maxLength);
  });

  $('#keywords').keyup(function() {
    var maxLength = 250;
    var curr_textlen = $(this).val().length;

    var textlen = maxLength - curr_textlen;

    $('.keywords_counter').text(curr_textlen+'/'+maxLength);
  });

  $('input').keyup( function () {

    $('#btn-save').prop('disabled', true)

    if ( $('#blog-title').val().length > 5 && $('#keywords').val().length > 2 ) {
      $('#btn-save').prop('disabled', false)
    }
  })

})
