// Word usage over time — bar chart with adaptive time binning
//
// Raw daily data becomes unreadable once the date range gets long (hundreds
// of wafer-thin bars, overlapping x-axis labels), so we aggregate into
// weekly or monthly totals once the span crosses a threshold, and add a
// range slider so people can still zoom into a specific period.

function daySpan(dateStrings) {
    const timestamps = dateStrings.map(d => new Date(d).getTime());
    return (Math.max(...timestamps) - Math.min(...timestamps)) / 86400000;
}

function startOfWeek(date) {
    // Monday-start week
    const d = new Date(Date.UTC(date.getUTCFullYear(), date.getUTCMonth(), date.getUTCDate()));
    const day = d.getUTCDay();
    const diff = (day === 0 ? -6 : 1) - day;
    d.setUTCDate(d.getUTCDate() + diff);
    return d;
}

function startOfMonth(date) {
    return new Date(Date.UTC(date.getUTCFullYear(), date.getUTCMonth(), 1));
}

function aggregate(dateStrings, counts, granularity) {
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

const span = daySpan(dates);
let granularity = 'day';
if (span > 730) {
    granularity = 'month';
} else if (span > 120) {
    granularity = 'week';
}

const { x, y } = aggregate(dates, counts, granularity);

const hoverPrefix = { day: '', week: 'Week of ', month: 'Month of ' }[granularity];
const hovertemplate = `${hoverPrefix}%{x}<br>%{y} mention%{y=1?"":"s"}<extra></extra>`;

// Let people know when they're looking at aggregated data, since the
// hero's "Total mentions" figure always covers the raw underlying total.
const noteEl = document.getElementById('word_chart_note');
if (noteEl) {
    noteEl.textContent = granularity === 'day'
        ? ''
        : `Showing ${granularity}ly totals — drag the slider below to zoom in.`;
}

Plotly.newPlot('word_chart', [{
    x: x,
    y: y,
    type: 'bar',
    marker: {
        color: '#2e6b47',
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
        linecolor: '#cdd8cf',
        rangeslider: { visible: span > 90, thickness: 0.08, bgcolor: '#e8ede9' }
    },
    yaxis: {
        title: 'Mentions',
        showgrid: true,
        gridcolor: '#e8ede9',
        zeroline: false,
        tickfont: { size: 11, color: '#5a6b60' }
    },
    hoverlabel: {
        bgcolor: '#1a3d2b',
        font: { family: 'Inter, sans-serif', color: '#ffffff' }
    }
}, {
    responsive: true,
    displayModeBar: false
});