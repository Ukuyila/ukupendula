$(document).ready(function(){
  "use strict";

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
      },
      beforeSend: function () {
        edit_role_btn.html('Loading&nbsp;&nbsp;<i class="fa fa-spinner fa-pulse"></i>')
      },
      success: function (resp) {
        let responses = JSON.parse(resp)
        console.log(responses)
        $("#role-permission").val()
      }
    })
  })

})