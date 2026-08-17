const tdSearchInput = document.getElementById('td_word_search');
const tdResultsList = document.getElementById('td_search_results');
let tdDebounceTimer;

tdSearchInput.addEventListener('keyup', function (event) {
  clearTimeout(tdDebounceTimer);

  if (event.key === 'Enter') {
    event.preventDefault();
  }

  tdDebounceTimer = setTimeout(function () {
    const query = tdSearchInput.value;

    fetch(`/tds/${encodeURIComponent(tdName)}/words/search?q=${query}`)
      .then(response => response.json())
      .then(data => {
        tdResultsList.innerHTML = '';

        data.forEach(function (word) {
          const item = document.createElement('li');
          const link = document.createElement('a');
          link.href = '#';
          link.textContent = word;
          link.addEventListener('click', function (e) {
            e.preventDefault();
            loadTdWordChart(word);
          });
          item.appendChild(link);
          tdResultsList.appendChild(item);
        });
      });
  }, 300);
});

const tdSearchForm = document.getElementById('td_word_form');
tdSearchForm.addEventListener('submit', function (event) {
  event.preventDefault();
});

function loadTdWordChart(word) {
    fetch(`/tds/${encodeURIComponent(tdName)}/words/${encodeURIComponent(word)}`)
        .then(res => res.json())
        .then(data => {
            document.getElementById('td_word_chart_wrapper').style.display = 'block';
            renderWordChart(data.dates, data.counts, 'td_word_chart', 'td_word_chart_note');
            document.getElementById('td_word_chart_wrapper').scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        });
}