$(document).ready(function(){
  "use strict";

  let error_alert = $('#error-alert')
  let success_alert = $('#success-alert')
  $('.alert').prop('hidden', true)

  $("#member-modal-form").on('submit', function (event){
    
    if (event.isDefaultPrevented()) {
      error_alert.html('<button type="button" class="btn-close btn-close-white" data-bs-dismiss="alert" aria-hidden="true"></button><i class="fa fa-frown-o me-2" aria-hidden="true"></i> Please fill in all required form fields?')
      error_alert.prop('hidden', false)
    } else {
      event.preventDefault();

      if ($('#password1').val() == $('#password2').val()) {
        $('.alert').prop('hidden', true)
        $.ajax({
          type: 'POST',
          url: 'add-new-member',
          data: {
            first_name: $('#user-fname').val(),
            last_name: $('#user-lname').val(),
            user_email: $('#user-email').val(),
            password1: $('#password1').val(),
            password2: $('#password2').val(),
            email_notify: $('#email-notify').val(),
            user_language: $('#user-language').val(),
            user_role: $('#user-role').val(),
            csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val()
          },
          success: function (data) {
            if ( data.includes('success') ) {
              success_alert.html(data)
              success_alert.prop('hidden', false)
              setTimeout(() => {
                $("#member-modal-form")[0].reset()
                window.location.href="team-manager"
              }, 3000)
              $('invite_new_member').modal('hide')
            }
            else {
              error_alert.html(data).prop('hidden', false)
            }
          }
        })
      }
      else {
        error_alert.html('<button type="button" class="btn-close btn-close-white" data-bs-dismiss="alert" aria-hidden="true"></button><i class="fa fa-frown-o me-2" aria-hidden="true"></i> Password does not match!')
        error_alert.prop('hidden', false)
      }
      

    }
  })

  var maxLength = 200;
  var emailMaxLength = 100;
  var addrMaxLength = 300;
  var descMaxLength = 300;

  $('.title_counter').text($('#biz_name').val().length+'/'+maxLength);
  $('.industry_counter').text($('#industry').val().length+'/'+maxLength);
  $('.email_counter').text($('#biz_email').val().length+'/'+emailMaxLength);
  $('.address_counter').text($('#biz_address').val().length+'/'+addrMaxLength);
  $('.descr_counter').text($('#biz_description').val().length+'/'+descMaxLength);


  $('#biz_name').keyup(function() {
    var curr_textlen = $(this).val().length;

    var textlen = maxLength - curr_textlen;

    $('.title_counter').text(curr_textlen+'/'+maxLength);
  });

  $('#industry').keyup(function() {
    var curr_textlen = $(this).val().length;

    var textlen = maxLength - curr_textlen;

    $('.industry_counter').text(curr_textlen+'/'+maxLength);
  });

  $('#biz_email').keyup(function() {
    var curr_textlen = $(this).val().length;

    var textlen = emailMaxLength - curr_textlen;

    $('.email_counter').text(curr_textlen+'/'+emailMaxLength);
  });

  $('#biz_address').keyup(function() {
    
    var curr_textlen = $(this).val().length;

    var textlen = addrMaxLength - curr_textlen;

    $('.address_counter').text(curr_textlen+'/'+addrMaxLength);
  });

  $('#biz_description').keyup(function() {

    var curr_textlen = $(this).val().length;

    var textlen = descMaxLength - curr_textlen;

    $('.descr_counter').text(curr_textlen+'/'+descMaxLength);
  });

});