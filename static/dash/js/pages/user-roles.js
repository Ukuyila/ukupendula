$(document).ready(function(){
  "use strict";

  let error_alert = $('#error-alert')
  let success_alert = $('#success-alert')
  $('.alert').prop('hidden', true)

  $('body').on('click', '.edit-role', function () {
    $('#edit-role-id').prop('hidden', true)
    
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

        if ( responses['result'] == 'success' ) {
        
          $('#role-permission option')
            .removeAttr('selected')
            .filter('[value=' + role_perm_id + ']')
            .prop('selected', true);

          $("#role-permission").val(responses['role_perm_name'])

          $("#role-name").val(responses['role_name'])
          $("#role-abbr").val(responses['abbreviation'])

          if (responses['can_write']) {$("#role-can-write").prop('checked', true)} else {$("#role-can-write").prop('checked', false)}
          if (responses['can_edit']) {$("#role-can-edit").prop('checked', true)} else {$("#role-can-edit").prop('checked', false)}
          if (responses['can_delete']) {$("#role-can-delete").prop('checked', true)} else {$("#role-can-delete").prop('checked', false)}

          if (responses['can_create_team']) {$("#can-invite").prop('checked', true)} else {$("#can-invite").prop('checked', false)}
          if (responses['can_edit_team']) {$("#can-edit-team").prop('checked', true)} else {$("#can-edit-team").prop('checked', false)}
          if (responses['can_delete_team']) {$("#can-delete-team").prop('checked', true)} else {$("#can-delete-team").prop('checked', false)}

          setTimeout(() => {
            edit_role_btn.html('Save').prop('disabled', true)
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

})