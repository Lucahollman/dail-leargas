//Probability Distribution graph 
Plotly.newPlot('overallprobdist',
    [{ labels: words, values: freq, parents: words.map(() => ''), type: 'treemap', pathbar: { visible: false }, marker: { colorscale: 'Greens', pad: 0, line: { color: 'white', width: 1 } } }],
    {
        title: 'Word Frequency',
        paper_bgcolor: 'white',
        plot_bgcolor: 'white',
        xaxis: { title: 'Word', fixedrange: false },
        yaxis: { title: 'Frequency', fixedrange: true },
        updatemenus: [{ direction: 'left', type: 'buttons', buttons: [
            { label: 'Treemap', method: 'restyle', args: [{ type: 'treemap', labels: [words], values: [freq], parents: [words.map(() => '')], x: [undefined], y: [undefined], marker: { colorscale: 'Greens' } }] },
            { label: 'Bar Chart', method: 'restyle', args: [{ type: 'bar', x: [words], y: [freq], labels: [undefined], values: [undefined], parents: [undefined], marker: { color: 'lightgreen' } }] }
        ]}]
    },
    { responsive: true }
);

Plotly.newPlot('overallirishper',
    [{ labels: labels, values: values, type: 'pie', marker: { colors: ['#2e6b47', '#c9a84c']}}])

