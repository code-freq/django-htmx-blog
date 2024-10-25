// Script for making 'read more' button appear when overflow for each post using dynamic post id
document.addEventListener('DOMContentLoaded', function() {
    const postContents = document.querySelectorAll('.post-content');

    postContents.forEach(function(post) {
        // Check if content is more than 390px (380px + 10px padding)
        if (post.scrollHeight > 390) {
            const postId = post.getAttribute('id');
            if (postId) {
                // If post id exists, get 'read more' button by id
                const readMoreButton = document.getElementById('read-more-' + postId.split('-')[1]);
                if (readMoreButton) {
                    readMoreButton.classList.add('show');  // Make 'read more' visible
                }
            }
        }
    });
});
