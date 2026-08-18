// Word search scoped to a single TD's speeches, with an inline usage chart
const tdWordSearchInput = document.getElementById('td_word_search');
const tdWordResultsList = document.getElementById('td_word_search_results');
const tdWordChartWrapper = document.getElementById('td_word_chart_wrapper');
const tdWordChartTitle = document.getElementById('td_word_chart_title');
const tdWordChartTotalValue = document.getElementById('td_word_chart_total_value');
const tdWordChartNote = document.getElementById('td_word_chart_note');
let tdWordDebounceTimer;

// --------------------------------------------------
// Search-as-you-type
// --------------------------------------------------

if (tdWordSearchInput && tdWordResultsList) {

    tdWordSearchInput.addEventListener('keyup', function (event) {
        clearTimeout(tdWordDebounceTimer);

        if (event.key === 'Enter') {
            event.preventDefault();
        }

        tdWordDebounceTimer = setTimeout(function () {
            const query = tdWordSearchInput.value;

            fetch(`/tds/words/search?td=${encodeURIComponent(tdName)}&q=${encodeURIComponent(query)}`)
                .then(response => response.json())
                .then(data => {
                    tdWordResultsList.innerHTML = '';

                    data.forEach(function (word) {
                        const item = document.createElement('li');
                        const link = document.createElement('a');
                        link.href = '#';
                        link.textContent = word;

                        link.addEventListener('click', function (event) {
                            event.preventDefault();
                            tdWordResultsList.innerHTML = '';
                            loadTdWordChart(word);
                        });

                        item.appendChild(link);
                        tdWordResultsList.appendChild(item);
                    });
                });
        }, 300);
    });

    const tdWordSearchForm = document.getElementById('td_word_search_form');

    if (tdWordSearchForm) {
        tdWordSearchForm.addEventListener('submit', function (event) {
            event.preventDefault();
        });
    }
}

// --------------------------------------------------
// Usage-over-time chart for the selected word
// (same adaptive day / week / month binning as wordgraphs.js)
// --------------------------------------------------

function daySpan(dateStrings) {
    const timestamps = dateStrings.map(d => new Date(d).getTime());
    return (Math.max(...timestamps) - Math.min(...timestamps)) / 86400000;
}

function startOfWeek(date) {
    const d = new Date(Date.UTC(date.getUTCFullYear(), date.getUTCMonth(), date.getUTCDate()));
    const day = d.getUTCDay();
    const diff = (day === 0 ? -6 : 1) - day;
    d.setUTCDate(d.getUTCDate() + diff);
    return d;
}

function startOfMonth(date) {
    return new Date(Date.UTC(date.getUTCFullYear(), date.getUTCMonth(), 1));
}

function aggregateTdWord(dateStrings, counts, granularity) {
    const totals = new Map();

    dateStrings.forEach((dateStr, i) => {
        const date = new Date(dateStr);
        let bucket;
        if (granularity === 'day') {
            bucket = date.toISOString().slice(0, 10);
        } else if (granularity === 'week') {
            bucket = startOfWeek(date).toISOString().slice(0, 10);
        } else {
            bucket = startOfMonth(date).toISOString().slice(0, 10);
        }
        totals.set(bucket, (totals.get(bucket) || 0) + counts[i]);
    });

    const keys = Array.from(totals.keys()).sort();
    return { x: keys, y: keys.map(k => totals.get(k)) };
}

function loadTdWordChart(word) {
    fetch(`/tds/words/${encodeURIComponent(word)}?td=${encodeURIComponent(tdName)}`)
        .then(response => response.json())
        .then(data => {
            tdWordChartWrapper.hidden = false;
            tdWordChartTitle.textContent = `${tdName}'s usage of "${word}"`;
            tdWordChartWrapper.scrollIntoView({ behavior: 'smooth', block: 'start' });

            const total = data.counts.reduce((sum, n) => sum + n, 0);
            tdWordChartTotalValue.textContent = total.toLocaleString();

            if (!data.dates.length) {
                tdWordChartNote.textContent = `${tdName} hasn't used this word in any recorded contributions.`;
                Plotly.purge('td_word_chart');
                return;
            }

            const span = daySpan(data.dates);
            let granularity = 'day';
            if (span > 730) {
                granularity = 'month';
            } else if (span > 120) {
                granularity = 'week';
            }

            const { x, y } = aggregateTdWord(data.dates, data.counts, granularity);
            const hoverPrefix = { day: '', week: 'Week of ', month: 'Month of ' }[granularity];
            const hovertemplate = `${hoverPrefix}%{x}<br>%{y} mention%{y=1?"":"s"}<extra></extra>`;

            tdWordChartNote.textContent = granularity !== 'day'
                ? `Showing ${granularity}ly totals.`
                : '';

            Plotly.newPlot('td_word_chart', [{
                x: x,
                y: y,
                type: 'bar',
                marker: {
                    color: '#0B6E4F',
                    line: { color: '#ffffff', width: 1 }
                },
                hovertemplate: hovertemplate
            }], {
                paper_bgcolor: 'rgba(0,0,0,0)',
                plot_bgcolor: 'rgba(0,0,0,0)',
                font: { family: 'Inter, sans-serif', size: 13, color: '#1c1c1c' },
                margin: { t: 20, r: 20, b: 50, l: 55 },
                bargap: granularity === 'day' ? 0.15 : 0.35,
                xaxis: {
                    title: 'Date',
                    type: 'date',
                    showgrid: false,
                    tickfont: { size: 11, color: '#5a6b60' },
                    linecolor: '#cdd8cf'
                },
                yaxis: {
                    title: 'Mentions',
                    showgrid: true,
                    gridcolor: '#e8ede9',
                    zeroline: false,
                    tickfont: { size: 11, color: '#5a6b60' }
                },
                hoverlabel: {
                    bgcolor: '#173d2b',
                    font: { family: 'Inter, sans-serif', color: '#ffffff' }
                }
            }, {
                responsive: true,
                displayModeBar: false
            });
        });
}