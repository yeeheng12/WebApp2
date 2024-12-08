$(document).ready(function() {
    
    // Like Button
    $(document).on('click', '.like-btn', function() {
        var postId = $(this).data('post-id');
        
        $.ajax({
            url: '/like/' + postId,
            type: 'POST',
            success: function(response) {
                var likeCount = $('#like-count-' + postId);
                if (response.liked) {
                    likeCount.text(parseInt(likeCount.text()) + 1);
                    $(this).find('i').removeClass('fa-heart-o').addClass('fa-heart text-danger');
                } else {
                    likeCount.text(parseInt(likeCount.text()) - 1);
                    $(this).find('i').removeClass('fa-heart').addClass('fa-heart-o');
                }
            }
        });
    });

    // Save Button
    $(document).on('click', '.save-btn', function() {
        var postId = $(this).data('post-id');
        
        $.ajax({
            url: '/save_toggle/' + postId,
            type: 'POST',
            success: function(response) {
                var icon = $(this).find('i');
                if (response.saved) {
                    icon.removeClass('fa-bookmark-o').addClass('fa-bookmark');
                } else {
                    icon.removeClass('fa-bookmark').addClass('fa-bookmark-o');
                }
            }
        });
    });

    // Open the Comment Modal
    $(document).on('click', '.comment-btn', function() {
        var postId = $(this).data('post-id');
        var modal = $('#commentModal-' + postId);
        modal.modal('show');
    });

    // Add Comment AJAX (for inline comment submission)
    $(document).on('submit', '.comment-form', function(event) {
        event.preventDefault();
        
        var form = $(this);
        var postId = form.data('post-id');
        var content = form.find('input[name="content"]').val();
        
        if (content) {
            $.ajax({
                url: '/add_comment/' + postId,
                type: 'POST',
                data: { content: content },
                success: function(response) {
                    var commentSection = modal.find('.comments-section');
                    commentSection.append(`
                        <div class="d-flex align-items-start mb-3">
                            <img src="${response.user_avatar}" class="rounded-circle me-3" width="40" height="40">
                            <div>
                                <strong>${response.user}</strong>
                                <p>${response.content}</p>
                                <small class="text-muted">${response.timestamp}</small>
                            </div>
                        </div>
                    `);
                    form.find('input[name="content"]').val(''); // Clear input field
                }
            });
        }
    });
});
