$(function() {

    // add group dialog
    $("#create_group_dialog").dialog({autoOpen: false, title: 'Create a new group'});
    $("#create-group").on('click', function(e) {
        $("#create_group_dialog").removeClass("hidden");
        $("#create_group_dialog").dialog("open");
    });

    // edit group dialog
    $("#edit_group_dialog").dialog({autoOpen: false, title: 'Edit Group'});
    $("#edit-group").on('click', function(e) {
        $("#edit_group_dialog").removeClass("hidden");
        $("#edit_group_dialog").dialog("open");
    });

    // join group dialog
    $("#join-group").on('click', function(e) {
        $.ajax({
            method: 'POST',
            url: '/api/groupmembers/',
            data: {
                'user': 1,
                'group': $("#group-name").text(),
                'joined': "2014-08-07"
            }
        });
    });
});