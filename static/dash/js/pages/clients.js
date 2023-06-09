$(function () {
  'use strict'

  $('body').on('click', '.edit-client', function () {
    
    $('#client-modal-title').html('Update Client')

    $('#client-code').prop('hidden', true)
    $('#a7301e7fd').prop('hidden', true)

    // let $tr = $(this).closest('tr');

    // var data = $tr.children("td").map(function ()  {
    // return $(this).text();
    // }).get();
    let $ul = $(this).parent().find("ul")

    var data = $ul.children("li").map(function () {
      return $(this).text()
    })

    // console.log(data[0])

    $('#client-code').val(data[0])
    $('#client-name').val(data[1])
    $('#contact-name').val(data[2])
    $('#contact-email').val(data[3])
    $('#industry').val(data[4])
    $('#address').val(data[5])
    $('#client-descr').val(data[6])

    $('#updateClientModal').modal('toggle')

  });

  let error_alert = $('#error-alert')
  error_alert.prop('hidden', true)

  let success_alert = $('#success-alert')
  success_alert.prop('hidden', true)

  $('#client-editor-form').on('submit', function(event) {
		if(event.isDefaultPrevented()) {
			// handle the invalid form
			error_alert.html("Please fill in all the fields?").prop('hidden', false)
		}
		else {
			event.preventDefault();
			submit_edit_client()
		}
	})

  function submit_edit_client() {
    var client_btn = $("#client-submit-btn")

    var client_form = $('#client-editor-form')[0]

    client_btn.prop("disabled", true)

    error_alert.prop('hidden', true)
    success_alert.prop('hidden', true)

    $.ajax({
      type: 'POST',
      url: 'edit-client',
      data: {
        client_code: $('#client-code').val(),
        client_name: $('#client-name').val(),
        contact_name: $('#contact-name').val(),
        contact_email: $('#contact-email').val(),
        industry: $('#industry').val(),
        address: $('#address').val(),
        client_descr: $('#client-descr').val(),
        csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val()
      },
      beforeSend: function () {
        client_btn.html('Saving&nbsp;&nbsp;<i class="fa fa-spinner fa-pulse"></i>')
      },
      success: function (resp) {
        if ( resp.includes('success') ) {
          success_alert.html(resp)
          success_alert.prop('hidden', false)

          client_form.reset()
          $('#updateClientModal').modal('hide')
          setTimeout(() => {
            window.location.href="clients"
          }, 3000)
        }
        else {
          error_alert.html(resp).prop('hidden', false)
        }
      }
    })
  }
})