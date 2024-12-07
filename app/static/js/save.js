$(document).on('click', '.save-btn', function() {
    var post_id = $(this).data('post-id');
    var button = $(this);

    $.post('/save_toggle/' + post_id, function(data) {
        if (data.saved) {
            button.addClass('saved').find('i').removeClass('fa-bookmark-o').addClass('fa-bookmark');
        } else {
            button.removeClass('saved').find('i').removeClass('fa-bookmark').addClass('fa-bookmark-o');
        }
    });
});
