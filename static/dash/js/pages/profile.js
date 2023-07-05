$(function () {
  'use strict'

  let error_alert = $('#error-alert')
  error_alert.prop('hidden', true)

  let success_alert = $('#success-alert')
  success_alert.prop('hidden', true)

  $('#settings-form').on('submit', function(event) {
		if(event.isDefaultPrevented()) {
			// handle the invalid form
			error_alert.html("Please fill in all the fields?").prop('hidden', false)
		}
		else {
			event.preventDefault();
			submit_edit_settings()
		}
	})

  function submit_edit_settings() {
    let save_btn = $('#save-settings-btn')
    var settings_form = $('#settings-form')[0]

    save_btn.prop("disabled", true)

    error_alert.prop('hidden', true)
    success_alert.prop('hidden', true)

    var me_notify = $('#multiple-email-notify').val()

    console.log('me_notify: ' + me_notify)

    $.ajax({
      type: 'POST',
      url: 'edit-settings',
      data: {
        user_lang: $('#user-lang').val(),
        user_website: $('#user-website').val(),
        user_twitter: $('#user-twitter').val(),
        user_facebook: $('#user-facebook').val(),
        user_instagram: $('#user-instagram').val(),
        user_linkedin: $('#user-linkedin').val(),
        email_notify: $('#email-notify').val(),
        multi_email_notify: $('#multiple-email-notify').val(),
        csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val()
      },
      beforeSend: function () {
        save_btn.html('Saving&nbsp;&nbsp;<i class="fa fa-spinner fa-pulse"></i>')
      },
      success: function (resp) {
        if ( resp.includes('success') ) {
          success_alert.html(resp)
          success_alert.prop('hidden', false)

          setTimeout(() => {
            window.location.href="profile"
          }, 3000)

        }
        else {
          error_alert.html(resp).prop('hidden', false)
        }
      }
    })
  }
})