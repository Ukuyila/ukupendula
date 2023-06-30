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
              $("#member-modal-form")[0].reset()
              $('#invite_new_member').modal('hide')
              setTimeout(() => {
                window.location.href="team-manager"
              }, 3000)
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

  $('body').on('click', '.edit-member', function () {
    
    // $('#client-modal-title').html('Update Client')

    $('#edit-unique-id').prop('hidden', true)
    // $('.a7301e7fd').prop('hidden', true)

    let $ul = $(this).parent().find("ul")

    var data = $ul.children("li").map(function () {
      return $(this).text()
    })

    console.log(data[0])

    $('#edit-unique-id').val(data[0])
    $('#edit-user-fname').val(data[1])
    $('#edit-user-lname').val(data[2])
    $('#edit-user-email').val(data[3])
    $('#edit-user-language').val(data[4])
    $('#edit-user-role').val(data[5])

    $('#edit_member_modal').modal('toggle')

  });

  let edit_error_alert = $('#edit-error-alert')
  let edit_success_alert = $('#edit-success-alert')
  $('.alert').prop('hidden', true)

  $('#edit-member-modal-form').on('submit', function(event) {
		if(event.isDefaultPrevented()) {
			// handle the invalid form
			edit_error_alert.html("Please fill in all the fields?").prop('hidden', false)
		}
		else {
			event.preventDefault();
			submit_edit_member()
		}
	})

  function submit_edit_member() {
    var member_btn = $("#edit-member-btn")
    var member_form = $('#edit-member-modal-form')[0]

    member_btn.prop("disabled", true)

    edit_error_alert.prop('hidden', true)
    edit_success_alert.prop('hidden', true)

    $.ajax({
      type: 'POST',
      url: 'edit-member',
      data: {
        user_fname: $('#edit-user-fname').val(),
        user_lname: $('#edit-user-lname').val(),
        user_email: $('#edit-user-email').val(),
        user_language: $('#edit-user-language').val(),
        user_role: $('#edit-user-role').val(),
      },
      beforeSend: function () {
        member_btn.html('Saving&nbsp;&nbsp;<i class="fa fa-spinner fa-pulse"></i>')
      },
      success: function (resp) {
        if ( resp.includes('success') ) {
          success_alert.html(resp)
          success_alert.prop('hidden', false)

          member_form.reset()
          $('#edit_member_modal').modal('hide')
          setTimeout(() => {
            window.location.href="team-manager"
          }, 3000)
        }
        else {
          error_alert.html(resp).prop('hidden', false)
        }
      }
    })
  }

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