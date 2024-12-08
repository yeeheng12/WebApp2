$('.like-btn').on('click', function() {
    const postId = $(this).data('post-id');
    $.ajax({
        type: 'POST',
        url: '/like/' + postId,
        success: function(response) {
            if (response.liked) {
                $(this).find('i').removeClass('fa-heart-o').addClass('fa-heart text-danger');
            } else {
                $(this).find('i').removeClass('fa-heart').addClass('fa-heart-o');
            }
            $('#like-count-' + postId).text(response.like_count + ' likes');
        }
    });
});
