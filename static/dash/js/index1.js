function sales() {
    'use strict'

    /* chartjs (#sales-status) */
    var ctx = $('#sales-status');
    ctx.height(285);
    var myChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: ["Jan", "Feb", "Mar", "Apr", "May", "June", "July", "Aug", "Sep", "Oct", "Nov", "Dec"],
            datasets: [{
                label: 'Selling',
                data: [100, 420, 210, 420, 210, 320, 150, 420, 210, 420, 210, 320],
                borderWidth: 2,
                backgroundColor: 'transparent',
                borderColor: myVarVal,
                borderWidth: 3,
                pointBackgroundColor: '#ffffff',
                pointRadius: 2
            }, {
                label: 'Buying',
                data: [450, 200, 350, 250, 480, 200, 450, 200, 350, 250, 480, 200],
                borderWidth: 2,
                backgroundColor: 'transparent',
                borderColor: myVarVal1,
                borderWidth: 3,
                pointBackgroundColor: '#ffffff',
                pointRadius: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,

            scales: {
                xAxes: [{
                    ticks: {
                        fontColor: "#9ba6b5",
                    },
                    display: true,
                    gridLines: {
                        color: 'rgba(119, 119, 142, 0.2)'
                    }
                }],
                yAxes: [{
                    ticks: {
                        fontColor: "#9ba6b5",
                    },
                    display: true,
                    gridLines: {
                        color: 'rgba(119, 119, 142, 0.2)'
                    },
                    scaleLabel: {
                        display: false,
                        labelString: 'Thousands',
                        fontColor: 'rgba(119, 119, 142, 0.2)'
                    }
                }]
            },
            legend: {
                labels: {
                    fontColor: "#9ba6b5"
                },
            },
        }
    });
    /* chartjs (#sales-status) closed */

};