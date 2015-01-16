(function ($) {

    var dashboard_home = {
        init: function() {

            this.requestData();

        },
        requestData: function() {

            this.requestBigThreeData();
            this.requestRecentCalorieData();

        },
        requestBigThreeData: function() {

            res = $.ajax({
                method: 'GET',
                url: '/ajax/big-three-progress/' + data_from_django['username'],
                cache: false
            });

            res.done(this._drawBigThreeChart);

        },
        requestRecentCalorieData: function() {

            res = $.ajax({
                method: 'GET',
                url: '/ajax/nutrition-summary/',
                cache: false
            });

            res.done(this._drawCalorieChart);

        },
        _drawBigThreeChart: function(data) {

            var data_present = [];

            $.each(data, function(key, value){
                if (!$.isEmptyObject(value)) {
                    data_present.push(key);
                }
            });

            if (data_present.length > 0) {
                var history = [];
                $.each(data, function(key, value){
                    var exercise_sets = [];
                    $.each(value, function(date, weight){
                        var dt =  new Date(date);
                        exercise_sets.push([Date.UTC(dt.getUTCFullYear(),
                                            dt.getUTCMonth(), dt.getUTCDate()),
                                            weight])
                    });
                    history.push({'name': key, 'data': exercise_sets});

                    // sort the data to make sure it is in chronological order
                    for (var i=0; i < history.length; i++) {
                        history[i]["data"].sort(function(a, b) {
                            var valueA = a[0];
                            var valueB = b[0];
                            if (valueA < valueB) {
                                return -1;
                            }
                            else if (valueA > valueB) {
                                return 1;
                            }
                            return 0;
                        });
                    }

                });
            }
            else {
                history = window.defaultLiftData;
                $("#big-four").addClass("opacity");
            }

            $('#big-four').highcharts($.extend({}, line_chart, {
                series: history,
                title: {
                    text: 'Big Three History'
                },
                xAxis: {
                    type: 'datetime'
                },
                yAxis: {
                    title: {
                        text: 'Weight (kg)'
                    }
                },
                legend: {
                    enabled: true,
                    layout: 'horizontal',
                    verticalAlign: 'bottom',
                    borderWidth: 0
                }
            }));

        },
        _drawCalorieChart: function(data) {

            var draw = function(chart_id, data) {

                if ($.isEmptyObject(data)) {
                    data = window.defaultCalorieData;
                    $("#calories-week").addClass("opacity");
                }

                var chart_data = [];
                for (i in data) {
                    var dt = new Date(i);
                    chart_data.push([Date.UTC(dt.getUTCFullYear(),
                                              dt.getUTCMonth(),
                                              dt.getUTCDate()), data[i]]);
                }

                // sort the data to make sure it is in chronological order
                chart_data.sort(function(a, b) {
                    var valueA = a[0];
                    var valueB = b[0];
                    if (valueA < valueB) {
                        return -1;
                    }
                    else if (valueA > valueB) {
                        return 1;
                    }
                    return 0;
                });

                var chart_options = $.extend({}, line_chart_variable_dates, {
                    title: {
                        text: 'Calories - 7 Days'
                    },
                    xAxis: {
                        type: 'datetime'
                    },
                    yAxis: {
                        title: {
                            text: 'Calories Consumed'
                        }
                    },
                    series: [{
                        name: 'Calories consumed',
                        data: chart_data,
                    }]
                });

                // render the chart
                $('#' + chart_id).highcharts(chart_options);
            }

            draw('calories-week', data['weekly-calories'])

        }
    }

  /**
   * initialise the exercises page JavaScript once the DOM is ready
   */
   $(function() {
        dashboard_home.init();
   });

})(jQuery);