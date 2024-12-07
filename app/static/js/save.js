$(document).on('click', '.save-btn', function() {
    var postId = $(this).data('post-id');
    var button = $(this);

    $.ajax({
        url: '/save_toggle/' + postId,
        method: 'POST',
        headers: {
            'X-CSRFToken': $('meta[name="csrf-token"]').attr('content')
        },
        success: function(data) {
            if (data.saved) {
                button.addClass('saved').find('i').removeClass('fa-bookmark-o').addClass('fa-bookmark');
            } else {
                button.removeClass('saved').find('i').removeClass('fa-bookmark').addClass('fa-bookmark-o');
            }
        },
        error: function(error) {
            console.error("Error saving post: ", error);
        }
    });
});
