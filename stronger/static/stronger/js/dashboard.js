// set the default high chart styling and options

Highcharts.theme = {
    // http://colorschemedesigner.com/

    colors: ['#4E7AC7', '#7FB2F0', '#ADD5F7'],
    chart: {
        height: '200',
        borderRadius: 3,
        plotBackgroundColor: null,
        plotBorderWidth: null,
        plotShadow: false
    },
    xAxis: {
        tickLength: 0,
    },
    yAxis: {
        min: 0
        // gridLineWidth: 0
    },
    title: {
        style: {
            fontSize: '16px'
        }
    },
    legend: {
        enabled: false
    },
    credits: {
        enabled: false
    },
    exporting: {
        enabled: false
    }
};

// apply the theme to all highcharts

Highcharts.setOptions(Highcharts.theme);

// options for different charts we show on multiple pages

var pie_chart = {
    plotOptions: {
        pie: {
            allowPointSelect: true,
            cursor: 'pointer',
            dataLabels: {
                enabled: false
            },
            showInLegend: true
        }
    },
    series: {
        type: 'pie'
    }
}

var line_chart = {
    'xAxis': {
        gridLineWidth: 0,
        labels: {
            enabled: false
        }
    },
    'yAxis': {
        gridLineWidth: 0
    }
}

var line_chart_variable_dates = $.extend({}, line_chart, {
    xAxis: {
        type: 'datetime',
        dateTimeLabelFormats: { // don't display the dummy year
            month: '%e %b',
            year: '%b'
        }
    }
})

var column_chart = {
    chart: {
        type: 'column'
    },
    xAxis: {
        gridLineWidth: 0,
    },
    yAxis: {
      gridLineWidth: 0,
      minorGridLineWidth: 0,
        gridLineColor: 'transparent',
        gridLineWidth: 0,
        min: 0
    },
    plotOptions: {
        column: {
            pointPadding: 0.2,
            borderWidth: 0
        }
    },
    legend: {
        enabled: true,
        layout: 'horizontal',
        verticalAlign: 'bottom',
        borderWidth: 0
    }
}

var sevenDays = ['Mon', 'Tues', 'Wed', 'Thur', 'Fri', 'Sat', 'Sun'];
var twelveMonths = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                    'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
var defaultCalorieData = {
    "2014-09-02": 3800,
    "2014-09-03": 2500,
    "2014-09-04": 3500,
    "2014-09-05": 3500,
    "2014-09-06": 3100
};
var defaultBodyweightData = [
    {"bodyweight": 70, "date": "2014-01-01"},
    {"bodyweight": 74, "date": "2014-03-01"},
    {"bodyweight": 77, "date": "2014-06-01"},
    {"bodyweight": 80, "date": "2014-09-01"},
    {"bodyweight": 82, "date": "2014-12-01"},
]
var defaultLiftData = [
    {
        name: 'Deadlift',
        data: [140, 150, 155, 162.5, 170, 175, 180, 182.5, 185, 187.5, 190, 200]
    },
    {
        name: 'Squat',
        data: [150, 160, 170, 175, 175, 180, 182.5, 185, 187.5, 190, 190, 195]
    },
    {
        name: 'Bench',
        data: [80, 85, 87.5, 92.5, 95, 97.5, 102.5, 105, 107.5, 110, 110, 115]
    }
]