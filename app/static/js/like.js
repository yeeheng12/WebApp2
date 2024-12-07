$(document).ready(function() {
  $('.like-btn').click(function() {
    var postId = $(this).data('post-id');
    var likeCountSpan = $('#like-count-' + postId);
    
    // Send AJAX request to like/unlike the post
    $.ajax({
      url: '/like/' + postId,
      method: 'POST',
      data: { _csrf_token: $('meta[name="csrf-token"]').attr('content') },
      success: function(response) {
        // Update the like button state
        if (response.liked) {
          $(this).addClass('liked');
          $(this).find('i').removeClass('fa-heart-o').addClass('fa-heart');
        } else {
          $(this).removeClass('liked');
          $(this).find('i').removeClass('fa-heart').addClass('fa-heart-o');
        }
        // Update the like count
        likeCountSpan.text(response.like_count);
      },
      error: function(error) {
        console.error("Error in liking post: ", error);
      }
    });
  });
});

