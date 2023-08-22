$(document).ready(function(){
  "use strict";
  var maxLength = 250;
  var topicMaxLength = 300;

  $('.title_counter').text($('#post_title').val().length+'/'+maxLength);
  $('.topic_counter').text($('#prompt_text').val().length+'/'+topicMaxLength);
  $('.audience_counter').text($('#audience').val().length+'/'+maxLength);
  $('.keywords_counter').text($('#keywords').val().length+'/'+maxLength);
  

  $('#post_title').keyup(function() {
    var curr_textlen = $(this).val().length;

    var textlen = maxLength - curr_textlen;

    $('.title_counter').text(curr_textlen+'/'+maxLength);
  });

  $('#prompt_text').keyup(function() {
    var curr_textlen = $(this).val().length;

    var textlen = topicMaxLength - curr_textlen;

    $('.topic_counter').text(curr_textlen+'/'+topicMaxLength);
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

  if ( $('#audience').val().length > 1 && $('#keywords').val().length > 2 ) {
    $('#btn-generate').prop('disabled', false)
  }

  $('input').keyup( function () {

    $('#btn-generate').prop('disabled', true)

    if ( $('#audience').val().length > 1 && $('#keywords').val().length > 2 ) {
      $('#btn-generate').prop('disabled', false)
    }

  })

  $('#blog_post').change( function(){
    console.log('Selected Blog: ' + $(this).val())
  });


});

let error_alert = $('#error-alert')
error_alert.prop('hidden', true)

function regeneratePostSocial(postType, postId, url) {
  console.log(postId)

  var post_submit_btn = $("#btn-generate")

  post_submit_btn.prop("disabled", true)

  error_alert.prop('hidden', true)
  success_alert.prop('hidden', true)

  $.ajax({
    type: 'POST',
    url: url,
    data: {
      post_title: $('#post_title').val(),
      soc_post_type: postType,
      prompt_text: $('#prompt_text').val(),
      keywords: $('#keywords').val(),
      audience: $('#audience').val(),
      category: $('#category').val(),
      tone_of_voice: $('#tone_of_voice').val(),
      csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val()
    },
    beforeSend: function () {
      post_submit_btn.html('Generating&nbsp;&nbsp;<i class="fa fa-spinner fa-pulse"></i>')
    },
    success: function (resp) {
      console.log(resp)
      // if ( resp.includes('success') ) {
      //   window.location.href=''
      // }
      // else {
      //   error_alert.html(resp).prop('hidden', false)
      // }
    }
  })
}