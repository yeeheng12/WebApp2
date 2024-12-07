$(document).ready(function() {
    $('.like-btn').click(function() {
        var postId = $(this).data('post-id');
        var likeButton = $(this); // Cache the button reference

        $.ajax({
            url: '/like/' + postId,
            method: 'POST',
            headers: {
                'X-CSRFToken': $('meta[name="csrf-token"]').attr('content')
            },
            success: function(response) {
                if (response.liked) {
                    likeButton.addClass('liked').find('i').removeClass('fa-heart-o').addClass('fa-heart');
                } else {
                    likeButton.removeClass('liked').find('i').removeClass('fa-heart').addClass('fa-heart-o');
                }
                // Update like count on the page
                $('#like-count-' + postId).text(response.like_count);  // Update the like count
            },
            error: function(error) {
                console.error("Error in liking post: ", error);
            }
        });
    });
});
