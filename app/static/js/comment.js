$('#comment-form').on('submit', function(event) {
    event.preventDefault();

    var form = $(this);
    var content = form.find('textarea[name="content"]').val();
    var postId = form.data('post-id');

    $.ajax({
        url: '/add_comment/' + postId,
        method: 'POST',
        contentType: 'application/json',
        headers: {
            'X-CSRFToken': form.find('input[name="csrf_token"]').val()
        },
        data: JSON.stringify({ content: content }),
        success: function(response) {
            $('#comments-container').append(
                `<div class="comment">
                    <strong>${response.user}</strong>
                    <p>${response.content}</p>
                    <small>${response.timestamp}</small>
                </div>`
            );
            form.find('textarea[name="content"]').val(''); // Clear input field

            // Update the comment count on the page
            $('#comment-count-' + postId).text(response.comment_count);  // Update the comment count
        },
        error: function(error) {
            console.error("Error posting comment: ", error);
        }
    });
});
