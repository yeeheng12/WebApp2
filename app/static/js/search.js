document.getElementById('search-input').addEventListener('input', function () {
  const query = this.value.trim();
  const resultsContainer = document.getElementById('search-results');

  if (!query) {
    resultsContainer.innerHTML = ''; // Clear results if query is empty
    return;
  }

  // Fetch search results from the backend
  fetch(`/search?q=${encodeURIComponent(query)}`)
    .then(response => response.json())
    .then(data => {
      resultsContainer.innerHTML = ''; // Clear previous results

      if (data.length === 0) {
        resultsContainer.innerHTML = '<p class="text-white p-2">No results found</p>';
        return;
      }

      // Add each result to the results container
      data.forEach(item => {
        const resultItem = document.createElement('a');
        if (item.type === 'user') {
          resultItem.href = item.profile_link;
          resultItem.innerHTML = `
            <img src="${item.avatar}" alt="${item.username}">
            <span>${item.username}</span>
          `;
        } else if (item.type === 'hashtag') {
          resultItem.href = item.post_link;
          resultItem.innerHTML = `
            <i class="fas fa-hashtag"></i>
            <span>${item.content}</span>
          `;
        }
        resultsContainer.appendChild(resultItem);
      });
    })
    .catch(error => {
      console.error('Error fetching search results:', error);
    });
});
