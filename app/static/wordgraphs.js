//Word line chart
Plotly.newPlot('word_chart', [{
  x: dates,
  y: counts,
  type: 'scatter',
  mode: 'lines+markers',
  line: { color: 'green', 'shape': 'spline', 'smoothing': 0.1 },
}], {
  title: `Use of "${word}" over time`,
  xaxis: { title: 'Date' },
  yaxis: { title: 'Count' }
});
