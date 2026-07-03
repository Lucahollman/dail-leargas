//Word Search Engine 
const searchInput = document.getElementById('word_search');
const resultsList = document.getElementById('search_results');
let debounceTimer;

searchInput.addEventListener('keyup', function(event) {
  clearTimeout(debounceTimer);

  if (event.key === 'Enter') {
    event.preventDefault();
  }

  debounceTimer = setTimeout(function() {
    const query = searchInput.value;

    fetch(`/words/search?q=${query}`)
      .then(response => response.json())
      .then(data => {
        resultsList.innerHTML = '';

        data.forEach(function(word) {
          const item = document.createElement('li');
          const link = document.createElement('a');
          link.href = `/words/${word}`;
          link.textContent = word;
          item.appendChild(link);
          resultsList.appendChild(item);
        });
      });
  }, 300);
});

const searchForm = document.querySelector('form');

searchForm.addEventListener('submit', function(event) {
  event.preventDefault();
});