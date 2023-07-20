$(document).ready(function(){
  "use strict";

  const maxLength = 300;
  const maxKwLength = 250;
  const maxOcpLength = 2000;

  $('.title_counter').text($('#content_title').val().length+'/'+maxLength);
  $('.ocb_counter').text($('#content_body_old').val().length+'/'+maxOcpLength);
  $('.keywords_counter').text($('#keywords').val().length+'/'+maxKwLength);

  $('#content_title').keyup(function() {
    var curr_textlen = $(this).val().length;

    $('#btn-generate').prop('disabled', true)

    if ( curr_textlen > 10 ) {
      $('#btn-generate').prop('disabled', false)
    }

    var textlen = maxLength - curr_textlen;

    $('.title_counter').text(curr_textlen+'/'+maxLength);
  });

  $('#content_body_old').keyup(function() {
    var curr_textlen = $(this).val().length;

    $('#btn-generate').prop('disabled', true)

    if ( curr_textlen > 10 ) {
      $('#btn-generate').prop('disabled', false)
    }

    var textlen = maxOcpLength - curr_textlen;

    $('.ocb_counter').text(curr_textlen+'/'+maxOcpLength);
  });

  $('#keywords').keyup(function() {

    var curr_textlen = $(this).val().length;

    var textlen = maxKwLength - curr_textlen;

    $('.keywords_counter').text(curr_textlen+'/'+maxKwLength);
  });

  $('.prompt-input').keyup( function () {

    $('#btn-generate').prop('disabled', true)

    if ( $('#content_title').val().length > 5 && $('#content_body_old').val().length > 100 ) {
      
      $('#btn-generate').prop('disabled', false)
    }

  })

  let error_alert = $('#error-alert')
  let success_alert = $('#success-alert')
  $('.alert').prop('hidden', true)

  var content_title = $('#content_title')
  var content_body_old = $('#content_body_old')
  var keywords = $('#keywords')
  var generate_button = $('#btn-generate')
  var generated_text = $('#ai-response-text')

// submited
  $("#content-impr-form").on('submit', function (event) {
    
    if (event.isDefaultPrevented()) {
      
      success_alert.prop('hidden', true).html('')
      error_alert.html('<button type="button" class="btn-close btn-close-white" data-bs-dismiss="alert" aria-hidden="true"></button><i class="fa fa-frown-o me-2" aria-hidden="true"></i> Please fill in all required form fields?')
      error_alert.prop('hidden', false)
      $("#bg-spinner").fadeOut("slow");

    }
    else {

      event.preventDefault();
      error_alert.prop('hidden', true).html('')
      success_alert.prop('hidden', true).html('')

      if ( content_title.val().length < 5 || content_title.val().length > 300 ) {

        error_alert.html('<button type="button" class="btn-close btn-close-white" data-bs-dismiss="alert" aria-hidden="true"></button><i class="fa fa-frown-o me-2" aria-hidden="true"></i> Content title is supposed to be between 5 and 300 chars long!')
        error_alert.prop('hidden', false)
        $("#bg-spinner").fadeOut("slow");
      }
      else if ( content_body_old.val().length < 100 || content_body_old.val().length > 2000 ) {

        error_alert.html('<button type="button" class="btn-close btn-close-white" data-bs-dismiss="alert" aria-hidden="true"></button><i class="fa fa-frown-o me-2" aria-hidden="true"></i> Content body is supposed to be between 100 and 2000 chars long!')
        error_alert.prop('hidden', false)
        $("#bg-spinner").fadeOut("slow");
        
      }
      else if ( keywords.val().length > maxKwLength ) {

        error_alert.html('<button type="button" class="btn-close btn-close-white" data-bs-dismiss="alert" aria-hidden="true"></button><i class="fa fa-frown-o me-2" aria-hidden="true"></i> Keywords field is supposed to be max 255 chars long!')
        error_alert.prop('hidden', false)
        $("#bg-spinner").fadeOut("slow");
      }
      else {
        let form_data = {
          content_title: content_title.val(),
          content_body_old: content_body_old.val(),
          content_category: $('#category').val(),
          tone_of_voice: $('#tone_of_voice').val(),
          max_words: $('#max_words').val(),
          keywords: $('#keywords').val(),
          csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val()

        }
        // console.log(form_data)
        // debugger;
        // ajax
        $.ajax({
          type: 'POST',
          url: 'improve-content',
          data: form_data,
          beforeSend: function () {
            generate_button.html('Generating&nbsp;&nbsp;<i class="fa fa-spinner fa-pulse"></i>')
            // $('.prompt-input').prop(disabled)
            error_alert.prop('hidden', true).html('')
            success_alert.prop('hidden', true).html('')
          },
          success: function (data) {
            $("#bg-spinner").fadeOut("slow")
            generate_button.html('Generate content')
            console.log(data['result'])
            console.log(data['message'])
            // let json_data = JSON.parse(data)

            if ( data['result'] === 'success' ) {
              success_alert.html(data['message'])
              success_alert.prop('hidden', false)
              console.log(data['contentBody'])

              setTimeout(() => {
                typeWriter(0, data['contentBody'], 10)
                // generated_text.html(data['contentBody'])
              }, 2000)
            }
            else {
              error_alert.html(data['message']).prop('hidden', false)
              
            }
          }
        })
      }
    }
  })

});