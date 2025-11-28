// Blog search and filter functionality

document.addEventListener('DOMContentLoaded', function () {
    const searchInput = document.getElementById('search-input');
    const tagButtons = document.querySelectorAll('.tag-btn');
    const postItems = document.querySelectorAll('.post-item');

    let currentTag = 'all';
    let searchTerm = '';

    // Search functionality
    if (searchInput) {
        searchInput.addEventListener('input', function (e) {
            searchTerm = e.target.value.toLowerCase();
            filterPosts();
        });
    }

    // Tag filter functionality
    tagButtons.forEach(button => {
        button.addEventListener('click', function () {
            // Update active button
            tagButtons.forEach(btn => btn.classList.remove('active'));
            this.classList.add('active');

            currentTag = this.dataset.tag;
            filterPosts();
        });
    });

    function filterPosts() {
        postItems.forEach(item => {
            const title = item.textContent.toLowerCase();
            const tags = item.dataset.tags ? item.dataset.tags.split(',') : [];

            const matchesSearch = searchTerm === '' || title.includes(searchTerm);
            const matchesTag = currentTag === 'all' || tags.includes(currentTag);

            if (matchesSearch && matchesTag) {
                item.style.display = '';
            } else {
                item.style.display = 'none';
            }
        });
    }
});
