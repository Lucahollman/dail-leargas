// Shared chart styling
const chartFont = {
    family: 'Inter, sans-serif',
    size: 13,
    color: '#1c1c1c'
};

const chartConfig = {
    displayModeBar: false,
    responsive: true
};

// Colours 
const DARK_GREEN = '#173d2b';   // --green-deep
const MID_GREEN = '#0B6E4F';    // --green-mid
const LIGHT_GREEN = '#8fbfa4';

const GOLD = '#c9a84c';         // --gold

const PAPER = '#F8F8F8';
const RULE = '#e8e5de';
const INK = '#1c1c1c';          // --text-dark
const INK_SOFT = '#667169';     // --text-muted


// --------------------------------------------------
// Colour interpolation for treemap
// --------------------------------------------------

function hexToRgb(hex) {
    const n = parseInt(hex.replace('#', ''), 16);

    return {
        r: (n >> 16) & 255,
        g: (n >> 8) & 255,
        b: n & 255
    };
}


function rgbToHex(r, g, b) {
    return '#' + [r, g, b]
        .map(value =>
            Math.round(value)
                .toString(16)
                .padStart(2, '0')
        )
        .join('');
}


function interpolateColor(hexA, hexB, t) {
    const a = hexToRgb(hexA);
    const b = hexToRgb(hexB);

    return rgbToHex(
        a.r + (b.r - a.r) * t,
        a.g + (b.g - a.g) * t,
        a.b + (b.b - a.b) * t
    );
}


// --------------------------------------------------
// Word frequency
// --------------------------------------------------

if (
    document.getElementById('overallprobdist') &&
    typeof words !== 'undefined' &&
    typeof freq !== 'undefined'
) {

    const treemapColors = freq.map((_, i) => {
        const t = freq.length > 1
            ? i / (freq.length - 1)
            : 0;

        return interpolateColor(
            DARK_GREEN,
            LIGHT_GREEN,
            t
        );
    });


    const wordData = [{
        labels: words,
        values: freq,
        parents: words.map(() => ''),
        type: 'treemap',

        pathbar: {
            visible: false
        },

        textfont: {
            family: 'Inter, sans-serif',
            size: 14,
            color: '#ffffff'
        },

        marker: {
            colors: treemapColors,
            pad: 3,

            line: {
                color: PAPER,
                width: 3
            }
        },

        hovertemplate:
            '<b>%{label}</b><br>' +
            '%{value:,} mentions' +
            '<extra></extra>',

        hoverlabel: {
            bgcolor: DARK_GREEN,
            bordercolor: DARK_GREEN,

            font: {
                family: 'Inter, sans-serif',
                size: 12,
                color: '#ffffff'
            }
        }
    }];


    const wordLayout = {

        margin: {
            l: 0,
            r: 0,
            t: 44,
            b: 0
        },

        paper_bgcolor: PAPER,
        plot_bgcolor: PAPER,

        font: chartFont,

        xaxis: {
            visible: false,
            fixedrange: false,
            showgrid: false,
            zeroline: false
        },

        yaxis: {
            visible: false,
            fixedrange: true,
            showgrid: false,
            zeroline: false
        },


        // Treemap / bar chart switch
        updatemenus: [{
            direction: 'left',
            type: 'buttons',

            x: 1,
            xanchor: 'right',

            y: 1.1,
            yanchor: 'bottom',

            pad: {
                r: 0,
                t: 0
            },

            bgcolor: PAPER,
            bordercolor: RULE,
            borderwidth: 1,

            font: {
                family: 'Inter, sans-serif',
                size: 11,
                color: MID_GREEN
            },

            active: 0,

            buttons: [

                {
                    label: 'Treemap',

                    method: 'update',

                    args: [

                        {
                            type: 'treemap',

                            labels: [words],
                            values: [freq],

                            parents: [
                                words.map(() => '')
                            ],

                            x: [undefined],
                            y: [undefined],

                            'marker.colors': [
                                treemapColors
                            ],

                            'marker.color': [
                                undefined
                            ],

                            'marker.line.color': [
                                PAPER
                            ],

                            'marker.line.width': [
                                3
                            ]
                        },

                        {
                            xaxis: {
                                visible: false,
                                showgrid: false,
                                zeroline: false
                            },

                            yaxis: {
                                visible: false,
                                showgrid: false,
                                zeroline: false
                            },

                            margin: {
                                l: 0,
                                r: 0,
                                t: 44,
                                b: 0
                            }
                        }
                    ]
                },


                {
                    label: 'Bar chart',

                    method: 'update',

                    args: [

                        {
                            type: 'bar',

                            x: [words],
                            y: [freq],

                            labels: [undefined],
                            values: [undefined],
                            parents: [undefined],

                            'marker.color': [
                                MID_GREEN
                            ],

                            'marker.colors': [
                                undefined
                            ]
                        },

                        {
                            xaxis: {
                                visible: true,

                                title: '',

                                showgrid: false,
                                zeroline: false,

                                tickfont: {
                                    family: 'Inter, sans-serif',
                                    size: 10,
                                    color: INK_SOFT
                                },

                                tickangle: -35,

                                linecolor: RULE,

                                fixedrange: true
                            },

                            yaxis: {
                                visible: true,

                                title: '',

                                showgrid: true,
                                gridcolor: RULE,
                                gridwidth: 1,

                                zeroline: false,

                                tickfont: {
                                    family: 'Inter, sans-serif',
                                    size: 10,
                                    color: INK_SOFT
                                },

                                linecolor: RULE,

                                fixedrange: true
                            },

                            margin: {
                                l: 48,
                                r: 10,
                                t: 44,
                                b: 85
                            }
                        }
                    ]
                }
            ]
        }]
    };


    Plotly.newPlot(
        'overallprobdist',
        wordData,
        wordLayout,
        chartConfig
    );
}


// --------------------------------------------------
// Language share
// --------------------------------------------------

if (
    document.getElementById('overallirishper') &&
    typeof labels !== 'undefined' &&
    typeof values !== 'undefined'
) {

    const languageData = [{
        labels: labels,
        values: values,

        type: 'pie',

        hole: 0.74,

        sort: false,

        direction: 'clockwise',

        textinfo: 'none',

        marker: {

            colors: [
                GOLD,
                MID_GREEN
            ],

            line: {
                color: PAPER,
                width: 3
            }
        },

        hovertemplate:
            '<b>%{label}</b><br>' +
            '%{value:.1f}%' +
            '<extra></extra>',

        hoverlabel: {
            bgcolor: DARK_GREEN,
            bordercolor: DARK_GREEN,

            font: {
                family: 'Inter, sans-serif',
                size: 12,
                color: '#ffffff'
            }
        }
    }];


    const languageLayout = {

        margin: {
            l: 8,
            r: 8,
            t: 20,
            b: 58
        },

        paper_bgcolor: PAPER,
        plot_bgcolor: PAPER,

        font: chartFont,

        showlegend: true,

        legend: {
            orientation: 'h',

            x: 0.5,
            xanchor: 'center',

            y: -0.08,
            yanchor: 'top',

            bgcolor: 'rgba(0,0,0,0)',

            font: {
                family: 'Inter, sans-serif',
                size: 11,
                color: INK_SOFT
            }
        },

        annotations: [{
            text:
                '<span style="font-size:26px; font-weight:600">' +
                irish.toFixed(1) +
                '%</span>' +
                '<br>' +
                '<span style="font-size:10px; letter-spacing:1px">' +
                'GAEILGE' +
                '</span>',

            showarrow: false,

            align: 'center',

            font: {
                family: 'Poppins, Inter, sans-serif',
                color: INK
            },

            x: 0.5,
            y: 0.5
        }]
    };


    Plotly.newPlot(
        'overallirishper',
        languageData,
        languageLayout,
        chartConfig
    );
}