(function ($) {

    var workouts = {
        init: function() {

            this.requestData();
            this.bindListeners();

        },
        requestData: function() {

            this.requestWorkoutsData();

        },
        requestWorkoutsData: function(daysBack) {

            daysBack = daysBack || 14;

            res = $.ajax({
                method: 'GET',
                url: '/ajax/workouts?days-back=' + daysBack,
                data: { user: data_from_django["username"] },
                cache: false
            });

            res.done(this._drawCharts);

        },
        _drawCharts: function(data) {

            var draw = function (graph_id, data) {

                if (['average-workout-count'].indexOf(graph_id) >= 0) {
                    // iterate over the json data

                    var chart_options = $.extend({}, line_chart, {
                        title: {
                            text: 'Workout Count'
                        },
                        xAxis: {
                            categories: ['Jan', 'Feb', 'Mar', 'Apr', 'May',
                                         'Jun', 'Jul', 'Aug', 'Sep', 'Oct',
                                         'Nov', 'Dec'],
                            tickInterval: 1
                        },
                        legend: {
                            enabled: true
                        },
                        series: [{
                            name: 'Personal - Workouts in Month',
                            data: data['user_average']
                        },
                        {
                            name: 'Site - Workouts in Month',
                            data: data['site_average']
                        }]
                    });
                }
                else if(['week-muscle-groups'].indexOf(graph_id) >= 0) {

                    var chart_data = [];
                    var chart_categories = [];

                    for (muscle in data) {
                        if (data.hasOwnProperty(muscle)) {
                        chart_data.push(data[muscle]);
                        chart_categories.push(muscle);
                        }
                    }

                    var chart_options = $.extend({}, column_chart, {
                        title: {
                            text: 'Muscle Groups'
                        },
                        xAxis: {
                            categories: chart_categories
                        },
                        series: [{
                            name: 'Sets Per Muscle Group',
                            data: chart_data
                        }]
                    });

                }
                else {
                    // iterate over the JSON and push to chart_data
                    var chart_data = [];
                    for (i in data) {
                        chart_data.push([i, data[i]]);
                    }

                    var chart_options = $.extend({}, pie_chart, {
                        title: {
                            text: 'Rep Rages'
                        },
                        tooltip: {
                            pointFormat: '<b>{point.percentage:.1f}%</b>'
                        },
                        legend: {
                            enabled: true,
                        },
                        series: [{
                            type: 'pie',
                            data: chart_data
                        }]
                    });
                }

                // and finally render the graph
                $('#' + graph_id).highcharts(chart_options);
            };

            for (workout in data) {
                draw(workout, data[workout]);
            }

        },
        bindListeners: function() {
            self = this;
            $("#filter-workout-dates").change(function() {
                self.requestWorkoutsData($("#filter-workout-dates")
                    .find(":selected")
                     .val());
            });
        }
    };

  /**
   * initialise the exercises page JavaScript once the DOM is ready
   */
   $(function() {
        workouts.init();
   });

})(jQuery);