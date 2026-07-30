// Shared building blocks for a consistent, branded chart look
const chartFont = { family: 'Inter, sans-serif', size: 13, color: '#1c1c1c' };
const chartConfig = { displayModeBar: false, responsive: true };

// --- Gradient treemap colours: darkest at highest frequency, lightening as frequency drops ---
function hexToRgb(hex) {
    const n = parseInt(hex.replace('#', ''), 16);
    return { r: (n >> 16) & 255, g: (n >> 8) & 255, b: n & 255 };
}
function rgbToHex(r, g, b) {
    return '#' + [r, g, b].map(v => Math.round(v).toString(16).padStart(2, '0')).join('');
}
function interpolateColor(hexA, hexB, t) {
    const a = hexToRgb(hexA), b = hexToRgb(hexB);
    return rgbToHex(a.r + (b.r - a.r) * t, a.g + (b.g - a.g) * t, a.b + (b.b - a.b) * t);
}

const DARK_GREEN = '#1a3d2b';
const LIGHT_GREEN = '#7fae91'; // lightest shade for the lowest-frequency word

const treemapColors = freq.map((_, i) => {
    const t = freq.length > 1 ? i / (freq.length - 1) : 0; // 0 = highest freq, 1 = lowest
    return interpolateColor(DARK_GREEN, LIGHT_GREEN, t);
});

// Probability Distribution graph
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
        xaxis: { visible: false, fixedrange: false, showgrid: false },
        yaxis: { visible: false, fixedrange: true, showgrid: false },
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
                {
                    label: 'Treemap',
                    method: 'update',
                    args: [
                        {
                            type: 'treemap',
                            labels: [words],
                            values: [freq],
                            parents: [words.map(() => '')],
                            x: [undefined],
                            y: [undefined],
                            'marker.colors': [treemapColors],
                            'marker.color': [undefined]
                        },
                        {
                            xaxis: { visible: false, showgrid: false },
                            yaxis: { visible: false, showgrid: false }
                        }
                    ]
                },
                {
                    label: 'Bar Chart',
                    method: 'update',
                    args: [
                        {
                            type: 'bar',
                            x: [words],
                            y: [freq],
                            labels: [undefined],
                            values: [undefined],
                            parents: [undefined],
                            'marker.color': ['#2e6b47'],
                            'marker.colors': [undefined]
                        },
                        {
                            xaxis: { visible: true, title: 'Word', showgrid: true },
                            yaxis: { visible: true, title: 'Frequency', showgrid: true }
                        }
                    ]
                }
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
