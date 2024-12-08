// Infinite Scroll or Load More for Comments
document.addEventListener('DOMContentLoaded', function () {
    const loadMoreButton = document.getElementById('load-more-comments');
    
    if (loadMoreButton) {
        loadMoreButton.addEventListener('click', function(e) {
            const postId = e.target.dataset.postId;
            
            // Fetch more comments for this post
            fetch(`/load_more_comments/${postId}`)
                .then(response => response.json())
                .then(data => {
                    const commentsContainer = document.getElementById(`comments-container-${postId}`);
                    data.comments.forEach(comment => {
                        const commentElement = document.createElement('div');
                        commentElement.classList.add('d-flex', 'mb-3', 'comment');
                        commentElement.innerHTML = `
                            <img src="${comment.avatar}" class="rounded-circle me-3" width="40" height="40" alt="User Avatar">
                            <div>
                                <strong>${comment.username}</strong>
                                <p>${comment.content}</p>
                                <small class="text-muted">${comment.timestamp}</small>
                            </div>
                        `;
                        commentsContainer.appendChild(commentElement);
                    });

                    // Hide the Load More button if there are no more comments
                    if (data.has_more_comments === false) {
                        e.target.style.display = 'none';
                    }
                });
        });
    }
});
