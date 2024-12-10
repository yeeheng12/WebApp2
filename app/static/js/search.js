document.getElementById('search-input').addEventListener('input', function () {
  const query = this.value.trim();
  const searchPopup = document.getElementById('search-popup');
  const popupResults = document.getElementById('popup-results');

  // If the query is empty, close the popup and clear results
  if (!query) {
    searchPopup.classList.remove('active'); // Hide the popup
    popupResults.innerHTML = ''; // Clear results
    return;
  }

  // Fetch search results from the backend
  fetch(`/search?q=${encodeURIComponent(query)}`)
    .then(response => response.json())
    .then(data => {
      popupResults.innerHTML = ''; // Clear previous results

      // If no results are found, display a "No results found" message
      if (data.length === 0) {
        popupResults.innerHTML = '<p class="text-muted p-2">No results found</p>';
        return;
      }

      // Populate the results in the popup
      data.forEach(item => {
        const resultItem = document.createElement('a');
        resultItem.className = 'd-block p-2 text-decoration-none text-dark';

        if (item.type === 'user') {
          resultItem.href = item.profile_link;
          resultItem.innerHTML = `
            <div class="d-flex align-items-center">
              <img src="${item.avatar}" alt="${item.username}" class="rounded-circle me-2" width="40" height="40">
              <span>${item.username}</span>
            </div>
          `;
        } else if (item.type === 'hashtag') {
          resultItem.href = item.post_link;
          resultItem.innerHTML = `
            <div class="d-flex align-items-center">
              <i class="fas fa-hashtag me-2"></i>
              <span>${item.content}</span>
            </div>
          `;
        }
        popupResults.appendChild(resultItem);
      });

      // Show the popup once results are populated
      searchPopup.classList.add('active');
    })
    .catch(error => {
      console.error('Error fetching search results:', error);
    });
});

// Optional: Close the popup when the user clicks outside or presses Escape
document.addEventListener('click', function (event) {
  const searchPopup = document.getElementById('search-popup');
  const searchInput = document.getElementById('search-input');
  if (!searchPopup.contains(event.target) && event.target !== searchInput) {
    searchPopup.classList.remove('active');
  }
});

document.addEventListener('keydown', function (event) {
  const searchPopup = document.getElementById('search-popup');
  if (event.key === 'Escape') {
    searchPopup.classList.remove('active');
  }
});
