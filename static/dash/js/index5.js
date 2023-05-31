function lineChart() {
		'use strict'

		var myCanvas = document.getElementById("lineChart");
		myCanvas.height = "320";
	
		var myCanvasContext = myCanvas.getContext("2d");
		var gradientStroke1 = myCanvasContext.createLinearGradient(0, 0, 0, 380);
		gradientStroke1.addColorStop(0, hexToRgba(myVarVal, 0.3));
	
		var gradientStroke2 = myCanvasContext.createLinearGradient(0, 0, 0, 280);
		gradientStroke2.addColorStop(0, hexToRgba(myVarVal1, 0.3));
	
		var myChart = new Chart(myCanvas, {
			type: 'line',
			data: {
				labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
				type: 'line',
				datasets: [{
					label: 'Total Listings',
					data: [0, 50, 40, 80, 40, 79, 50],
					backgroundColor: gradientStroke1,
					borderColor: myVarVal,
					pointBackgroundColor: myVarVal,
					pointHoverBackgroundColor: gradientStroke1,
					pointBorderColor: myVarVal,
					pointHoverBorderColor: gradientStroke1,
					pointBorderWidth: 3,
					pointRadius: 3,
					pointHoverRadius: 2,
					borderWidth: 2
				}, {
					label: "Total Visitors",
					data: [0, 70, 75, 120, 94, 141, 60],
					backgroundColor: gradientStroke2,
					borderColor: myVarVal1,
					pointBackgroundColor: myVarVal1,
					pointHoverBackgroundColor: gradientStroke2,
					pointBorderColor: myVarVal1,
					pointHoverBorderColor: gradientStroke2,
					pointBorderWidth: 3,
					pointRadius: 3,
					pointHoverRadius: 2,
					borderWidth: 2
				}
				]
			},
			options: {
				responsive: true,
				maintainAspectRatio: false,
				tooltips: {
					mode: 'index',
					titleFontSize: 12,
					titleFontColor: '#000',
					bodyFontColor: '#000',
					backgroundColor: '#fff',
					cornerRadius: 3,
					intersect: false,
				},
				legend: {
					display: true,
					labels: {
						usePointStyle: false,
					},
				},
				scales: {
					xAxes: [{
						ticks: {
							fontColor: "#c6c9d3",
						},
						display: true,
						gridLines: {
							display: true,
							color: 'rgba(96, 94, 126, 0.1)',
							drawBorder: false
						},
						scaleLabel: {
							display: false,
							labelString: 'Month',
							fontColor: 'transparent'
						}
					}],
					yAxes: [{
						ticks: {
							fontColor: "#c6c9d3",
						},
						display: true,
						gridLines: {
							display: true,
							color: 'rgba(96, 94, 126, 0.1)',
							drawBorder: false
						},
						scaleLabel: {
							display: false,
							labelString: 'sales',
							fontColor: 'transparent'
						}
					}]
				},
				title: {
					display: false,
					text: 'Normal Legend'
				}
			}
		});
	/* line chart end */
};

function sparkline_bar2() {
				'use strict'
	$(".sparkline_bar-2").sparkline([6,2,8,4,3,8,1,3,6,5,7], {
		type: 'bar',
		height: 130,
		colorMap: {
			'9': '#a1a1a1'
		},
		barColor: myVarVal,
		barSpacing: 7,
		barWidth: 6,
	});
	/* sparkline_bar end */

};