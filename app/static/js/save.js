$(document).ready(function () {
    // Save button click handler
    $('.save-btn').click(function () {
        var postId = $(this).data('post-id');
        var icon = $(this).find('i');
        $.ajax({
            url: '/save/' + postId,  // Adjust to your endpoint
            method: 'POST',
            success: function (data) {
                // Toggle the bookmark icon based on saved status
                if (data.is_saved) {
                    icon.removeClass('fa-bookmark-o').addClass('fa-bookmark');
                } else {
                    icon.removeClass('fa-bookmark').addClass('fa-bookmark-o');
                }
            },
            error: function () {
                alert("There was an error with the save request.");
            }
        });
    });
});
