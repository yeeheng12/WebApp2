$(document).ready(function () {
    // Like button click handler
    $('.like-btn').click(function () {
        var postId = $(this).data('post-id');
        var icon = $(this).find('i');
        $.ajax({
            url: '/like/' + postId,  // Adjust to your endpoint
            method: 'POST',
            success: function (data) {
                // Toggle the heart icon based on whether it's liked or not
                if (data.is_liked) {
                    icon.removeClass('fa-heart-o').addClass('fa-heart text-danger');
                } else {
                    icon.removeClass('fa-heart text-danger').addClass('fa-heart-o');
                }

                // Update the like count
                $('#like-count-' + postId).text(data.like_count + " likes");
            },
            error: function () {
                alert("There was an error with the like request.");
            }
        });
    });
});
