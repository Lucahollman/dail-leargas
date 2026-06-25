var ctx = document.getElementById("overallprobdist").getContext("2d");
var LineChart = new Chart(ctx, {
    type: "bar",
    data: { 
        labels: words,
        datasets: [
            {
                label: "Frequency",
                data: freq
            }
        ]    
    }
});