$(document).ready(function() {
    $('#comment-form').on('submit', function(event) {
        event.preventDefault();  // Prevent the page from refreshing

        var form = $(this);
        var content = form.find('textarea[name="content"]').val();
        var postId = form.data('post-id');

        $.ajax({
            url: '/post/' + postId,
            method: 'POST',
            data: {
                content: content,
                post_id: postId,
                csrf_token: form.find('input[name="csrf_token"]').val() // CSRF Token
            },
            success: function(response) {
                // Append the new comment to the comment container
                $('#comments-container').append(
                    '<div class="comment"><strong>' + response.user + '</strong><p>' + response.content + '</p><small>' + response.timestamp + '</small></div>'
                );
                form.find('textarea[name="content"]').val('');  // Clear the comment input
            }
        });
    });
});

