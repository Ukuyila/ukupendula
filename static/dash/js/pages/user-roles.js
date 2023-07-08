$(document).ready(function(){
  "use strict";

  let error_alert = $('#error-alert')
  let success_alert = $('#success-alert')
  $('.alert').prop('hidden', true)

  $('body').on('click', '.edit-role', function () {
    $('#edit-role-id').prop('hidden', true)
    $("#role-team-id").prop('hidden', true)
    
    var edit_role_btn = $("#edit-role-btn")
    edit_role_btn.prop("disabled", true)

    let $tr = $(this).closest('tr');

    var data = $tr.children("td").map(function ()  {
      return $(this).text();
    }).get();

    let role_id = data[8]
    let role_perm_id = data[9]

    // find user role details
    $.ajax({
      type: 'POST',
      url: 'get-role-details',
      data: {
        role_id: role_id,
        role_perm_id: role_perm_id,
        csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val()
      },
      beforeSend: function () {
        edit_role_btn.html('Loading&nbsp;&nbsp;<i class="fa fa-spinner fa-pulse"></i>')
      },
      success: function (resp) {
        let responses = JSON.parse(resp)

        // console.log(responses)
        if ( responses['result'] == 'success' ) {

          // console.log(role_perm_id)
        
          $('#role-permission option')
            .removeAttr('selected')
            .filter('[value=' + role_perm_id + ']')
            .prop('selected', true);

          // $("#role-permission").val(responses['role_perm_name'])

          $("#role-name").val(responses['role_name'])
          $("#role-abbr").val(responses['abbreviation'])

          $("#edit-role-id").val(role_id)
          $("#role-team-id").val(responses['role_team_id'])

          if (responses['can_write']) {$("#role-can-write").prop('checked', true)} else {$("#role-can-write").prop('checked', false)}
          if (responses['can_edit']) {$("#role-can-edit").prop('checked', true)} else {$("#role-can-edit").prop('checked', false)}
          if (responses['can_delete']) {$("#role-can-delete").prop('checked', true)} else {$("#role-can-delete").prop('checked', false)}

          if (responses['can_create_team']) {$("#can-invite").prop('checked', true)} else {$("#can-invite").prop('checked', false)}
          if (responses['can_edit_team']) {$("#can-edit-team").prop('checked', true)} else {$("#can-edit-team").prop('checked', false)}
          if (responses['can_delete_team']) {$("#can-delete-team").prop('checked', true)} else {$("#can-delete-team").prop('checked', false)}

          setTimeout(() => {
            edit_role_btn.html('Save').prop('disabled', false)
            $("#bg-spinner").fadeOut("slow");
            $('#edit_user_role').modal('toggle')
          }, 2000);

        }
        else {
          error_alert.html(`<strong>` + responses['result'] + `</strong>
          <hr class="message-inner-separator">
          <p>` + responses['message'] + `</p>`)

          error_alert.prop('disabled', true)
        }
      }
    })
  })

  $('#edit-role-form').on('submit', function(event) {
		if(event.isDefaultPrevented()) {
			// handle the invalid form
			edit_error_alert.html("Please fill in all the fields?").prop('hidden', false)
		}
		else {
			event.preventDefault();
			submit_edit_role()
		}
	})

  function submit_edit_role() {
    let edit_error_alert = $('#edit-error-alert')
    let edit_success_alert = $('#edit-success-alert')
    $('.alert').prop('hidden', true)

    var role_form = $('#edit-role-form')[0]

    var edit_role_btn = $("#edit-role-btn")
    edit_role_btn.prop("disabled", true)

    edit_error_alert.prop('hidden', true)
    edit_success_alert.prop('hidden', true)

    var role_edit_id = $("#edit-role-id").val()

    var role_team_id = $("#role-team-id").val()

    $.ajax({
      type: 'POST',
      url: 'edit-user-role/' + role_team_id + '/' + role_edit_id + '/',
      data: {
        role_name: $("#role-name").val(),
        role_permission: $('#role-permission').val(),
        role_abbr: $('#role-abbr').val(),
        role_can_write: $('#role-can-write').val() == 'on' ? true : false,
        role_can_edit: $('#role-can-edit').val() == 'on' ? true : false,
        role_can_delete: $('#role-can-delete').val() == 'on' ? true : false,
        can_invite: $('#can-invite').val() == 'on' ? true : false,
        can_edit_team: $('#can-edit-team').val() == 'on' ? true : false,
        can_delete_team: $('#can-delete-team').val() == 'on' ? true : false,

        csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val()
      },
      beforeSend: function () {
        edit_role_btn.html('Saving&nbsp;&nbsp;<i class="fa fa-spinner fa-pulse"></i>')
      },
      success: function (resp) {
        $("#bg-spinner").fadeOut("slow");
        edit_role_btn.html('Save').prop("disabled", false)
        if ( resp.includes('success') ) {
          edit_success_alert.html(resp)
          edit_success_alert.prop('hidden', false)

          role_form.reset()
          $('#edit_member_modal').modal('hide')
          setTimeout(() => {
            window.location.href="user-roles"
          }, 3000)
        }
        else {
          edit_error_alert.html(resp).prop('hidden', false)
        }
      }
    })

  }

})