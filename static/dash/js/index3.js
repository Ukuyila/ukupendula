function dataanalytics() {

var chartdata4 = [
	{
	  name: 'data',
	  type: 'line',
	  data: [20, 20, 36, 18, 15, 20, 25]
	}
];
var option7 = {
	grid: {
	  top: '6',
	  right: '0',
	  bottom: '17',
	  left: '25',
	},
	xAxis: {
	  data: [ 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat','Sun'],
	  axisLine: {
		lineStyle: {
		  color: 'rgba(227, 237, 252,0.5)'
		}
	  },
	  axisLabel: {
		fontSize: 10,
		color: 'rgba(146, 163, 185, 0.9)'
	  }
	},
	yAxis: {
	  splitLine: {
		lineStyle: {
		  color: 'rgba(227, 237, 252,0.5)'
		}
	  },
	  axisLine: {
		lineStyle: {
		  color: 'rgba(227, 237, 252,0.5)'
		}
	  },
	  axisLabel: {
		fontSize: 10,
		color: 'rgba(146, 163, 185, 0.9)'
	  }
	},
	series: chartdata4,
	color:[ myVarVal ]
};
var chart7 = document.getElementById('dataanalytics');
var lineChart = echarts.init(chart7);
lineChart.setOption(option7);
window.addEventListener('resize',function(){
	lineChart.resize();
})
};	
	

function purchase() {	
	/* chartjs (#purchase) */
	var myCanvas = document.getElementById("purchase");
	myCanvas.height="370";

	var myCanvasContext = myCanvas.getContext("2d");
	var gradientStroke1 = myCanvasContext.createLinearGradient(0, 0, 0, 380);
	gradientStroke1.addColorStop(0, hexToRgba(myVarVal, 0.3));

	var gradientStroke2 = myCanvasContext.createLinearGradient(0, 0, 0, 280);
	gradientStroke2.addColorStop(0, hexToRgba(myVarVal1, 0.3));

    var myChart = new Chart( myCanvas, {
		type: 'line',
		data: {
            labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
            type: 'line',
            datasets: [ {
				label: 'Properties Sold',
				data: [16, 32, 18, 26, 42, 33, 44],
				backgroundColor: gradientStroke1,
				borderColor: myVarVal,
				pointBackgroundColor:'#ed5151',
				pointHoverBackgroundColor:gradientStroke1,
				pointBorderColor :'#ed5151',
				pointHoverBorderColor :gradientStroke1,
				pointBorderWidth :3,
				pointRadius :3,
				pointHoverRadius :2,
				borderWidth: 2
            }, {
				label: "Properties Rent",
				data: [ 22, 44, 67, 43, 76, 45, 50],
				backgroundColor: gradientStroke2,
				borderColor: myVarVal1,
				pointBackgroundColor:'#df9431',
				pointHoverBackgroundColor:gradientStroke2,
				pointBorderColor :'#9c31df',
				pointHoverBorderColor :gradientStroke2,
				pointBorderWidth :3,
				pointRadius :3,
				pointHoverRadius :2,
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
						color:'rgba(96, 94, 126, 0.1)',
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
						color:'rgba(96, 94, 126, 0.1)',
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

};	
	
function dailyfeedback() {

	var chartdata3 = [
    {
      name: 'Good',
      type: 'bar',
      stack: 'Stack',
      data: [20, 56, 18, 75, 65, 74, 78, 67, 84]
    },
    {
      name: 'Bad',
      type: 'bar',
      stack: 'Stack',
      data: [12, 14, 15, 50, 24, 24, 10, 20 ,30]
    }
  ];

  var option5 = {
    grid: {
      top: '6',
      right: '0',
      bottom: '17',
      left: '25',
    },
	tooltip: {
		show: true,
		showContent: true,
		alwaysShowContent: true,
		triggerOn: 'mousemove',
		trigger: 'axis',
		axisPointer:
			{
				label: {
					show: false,
				}
			}

	},
    xAxis: {
      data: ['Mon', 'Tues', 'Wed', 'Thurs', 'Fri', 'Sat'],
      axisLine: {
        lineStyle: {
          color: 'rgba(227, 237, 252,0.5)'
        }
      },
      axisLabel: {
        fontSize: 10,
        color: '#a7b4c9'
      }
    },
    yAxis: {
      splitLine: {
        lineStyle: {
          color: 'rgba(227, 237, 252,0.5)'
        }
      },
      axisLine: {
        lineStyle: {
          color: 'rgba(227, 237, 252,0.5)'
        }
      },
      axisLabel: {
        fontSize: 10,
        color: '#a7b4c9'
      }
    },
    series: chartdata3,
	color:[ myVarVal,myVarVal1 ],
	barMaxWidth: 10
  };

  var chart5 = document.getElementById('dailyfeedback');
  var barChart5 = echarts.init(chart5);
  barChart5.setOption(option5);
  window.addEventListener('resize',function(){
	barChart5.resize();
})
	
};

