document.addEventListener('DOMContentLoaded', function () {
  const followButtons = document.querySelectorAll('.follow-button');

  followButtons.forEach(button => {
    button.addEventListener('click', function () {
      const userId = button.getAttribute('data-user-id');
      const isFollowing = button.textContent.trim() === 'Unfollow'; // Check if currently following

      console.log(`Button clicked for userId: ${userId}, isFollowing: ${isFollowing}`); // Debugging

      // Send an AJAX POST request to toggle follow/unfollow state
      fetch(`/follow_toggle/${userId}`, {
        method: 'POST',
        headers: {
          'X-CSRFToken': document.querySelector('meta[name="csrf-token"]').getAttribute('content'),
        },
        body: new FormData(),
      })
      .then(response => response.json())
      .then(data => {
        console.log('Response:', data); // Debugging

        // Update button state and counts based on the response
        if (data.follow_state === 'follow') {
          button.textContent = 'Follow';
          button.classList.remove('btn-danger');
          button.classList.add('btn-primary');

          // Update the follower/following counts in the DOM
          document.getElementById('followers-count').textContent = data.followers_count;
          document.getElementById('following-count').textContent = data.following_count;

          alert('You have unfollowed this user.');
        } else {
          button.textContent = 'Unfollow';
          button.classList.remove('btn-primary');
          button.classList.add('btn-danger');

          // Update the follower/following counts in the DOM
          document.getElementById('followers-count').textContent = data.followers_count;
          document.getElementById('following-count').textContent = data.following_count;

          alert('You are now following this user!');
        }
      })
      .catch(error => {
        console.error('Error:', error);
      });
    });
  });
});

