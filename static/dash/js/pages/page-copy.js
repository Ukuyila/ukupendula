$(document).ready(function(){
  "use strict";
  const cnMaxLength = 200;
  const cpMaxLength = 200;
  const titleLength = 200;

  $('.title_counter').text($('#copy_title').val().length+'/'+titleLength);

  $('.comp_counter').text($('#company_name').val().length+'/'+cnMaxLength);

  $('.purpose_counter').text($('#company_purpose').val().length+'/'+cpMaxLength);

  $('.sects_counter').text($('#page_sections').val().length+'/'+cpMaxLength);

  $('#copy_title').keyup(function() {

    var curr_textlen = $(this).val().length;

    var textlen = titleLength - curr_textlen;

    $('.title_counter').text(curr_textlen+'/'+titleLength);
  });

  $('#company_name').keyup(function() {
    var curr_textlen = $(this).val().length;

    var textlen = cnMaxLength - curr_textlen;

    $('.comp_counter').text(curr_textlen+'/'+cnMaxLength);
  });

  $('#company_purpose').keyup(function() {

    var curr_textlen = $(this).val().length;

    var textlen = cpMaxLength - curr_textlen;

    $('.purpose_counter').text(curr_textlen+'/'+cpMaxLength);
  });

  $('#page_sections').keyup(function() {

    var curr_textlen = $(this).val().length;

    var textlen = cpMaxLength - curr_textlen;

    $('.sects_counter').text(curr_textlen+'/'+cpMaxLength);
  });

  $('.prompt-command').keyup( function () {

    $('#btn-generate').prop('disabled', true)

    if ( $('#company_name').val().length > 10 && $('#company_purpose').val().length > 10 ) {
      $('#btn-generate').prop('disabled', false)
    }

  })


});