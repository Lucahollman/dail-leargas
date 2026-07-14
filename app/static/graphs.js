// Shared building blocks for a consistent, branded chart look
const chartFont = { family: 'Inter, sans-serif', size: 13, color: '#1c1c1c' };
const chartConfig = { displayModeBar: false, responsive: true };
const treemapColors = freq.map((_, i) => (i === 0 ? '#1a3d2b' : i < 4 ? '#2e6b47' : '#8fae9c'));

//Probability Distribution graph
Plotly.newPlot('overallprobdist',
    [{
        labels: words,
        values: freq,
        parents: words.map(() => ''),
        type: 'treemap',
        pathbar: { visible: false },
        textfont: { family: 'Inter, sans-serif', size: 14, color: '#ffffff' },
        marker: {
            colors: treemapColors,
            pad: 2,
            line: { color: '#ffffff', width: 2 }
        },
        hoverlabel: { bgcolor: '#1a3d2b', font: { family: 'Inter, sans-serif', color: '#ffffff' } }
    }],
    {
        margin: { l: 0, r: 0, t: 40, b: 0 },
        paper_bgcolor: 'rgba(0,0,0,0)',
        plot_bgcolor: 'rgba(0,0,0,0)',
        font: chartFont,
        xaxis: { title: 'Word', fixedrange: false, showgrid: false },
        yaxis: { title: 'Frequency', fixedrange: true, showgrid: false },
        updatemenus: [{
            direction: 'left',
            type: 'buttons',
            x: 1,
            xanchor: 'right',
            y: 1.15,
            yanchor: 'top',
            bgcolor: '#e8ede9',
            bordercolor: '#cdd8cf',
            font: { family: 'Inter, sans-serif', size: 12, color: '#1a3d2b' },
            buttons: [
                { label: 'Treemap', method: 'restyle', args: [{ type: 'treemap', labels: [words], values: [freq], parents: [words.map(() => '')], x: [undefined], y: [undefined], marker: { colors: [treemapColors] } }] },
                { label: 'Bar Chart', method: 'restyle', args: [{ type: 'bar', x: [words], y: [freq], labels: [undefined], values: [undefined], parents: [undefined], marker: { color: '#2e6b47' } }] }
            ]
        }]
    },
    chartConfig
);

// Language Share graph
Plotly.newPlot('overallirishper',
    [{
        labels: labels,
        values: values,
        type: 'pie',
        hole: 0.7,
        sort: false,
        textinfo: 'none',
        marker: {
            colors: ['#c9a84c', '#2e6b47'], // Irish %, English % — matches the gold/green accent convention used elsewhere on the site
            line: { color: '#ffffff', width: 2 }
        },
        hoverlabel: { bgcolor: '#1a3d2b', font: { family: 'Inter, sans-serif', color: '#ffffff' } }
    }],
    {
        margin: { l: 0, r: 0, t: 20, b: 20 },
        paper_bgcolor: 'rgba(0,0,0,0)',
        plot_bgcolor: 'rgba(0,0,0,0)',
        font: chartFont,
        showlegend: true,
        legend: { orientation: 'h', y: -0.1, font: { family: 'Inter, sans-serif', size: 12 } },
        annotations: [{
            text: (values[1] >= values[0] ? english : irish).toFixed(1) + '%',
            showarrow: false,
            font: { family: 'Playfair Display, serif', size: 24, color: '#1a3d2b' },
            x: 0.5,
            y: 0.5
        }]
    },
    chartConfig
);
