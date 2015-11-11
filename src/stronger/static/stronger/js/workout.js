(function ($) {

    var workout = {
        init: function() {

            this.prepareDOM();
            this.requestData();
            this.bindListeners();

        },
        prepareDOM: function() {

            this.prepareEditDialog();
            this.prepareDeleteDialog();

        },
        prepareEditDialog: function() {

            $("#edit_workout_dialog").dialog({
                autoOpen: false,
                title: 'Edit A Workout'
            });

        },
        prepareDeleteDialog: function() {

            $("#delete-workout-dialog").dialog({
                autoOpen: false,
                title: 'Delete A Workout'
            });

        },
        bindListeners: function() {

            this.bindOpenEditDialog();
            this.bindOpenDeleteDialog();
            this.bindCancelDelete();

        },
        bindOpenEditDialog: function() {

            // the edit workout dialog
            $("#edit-workout").on('click', function(e) {
                $("#edit_workout_dialog").removeClass("hidden").dialog("open");
            });

        },
        bindOpenDeleteDialog: function() {

            // the delete workout dialog
            $("#delete-workout").on('click', function(e) {
                $("#delete-workout-dialog").removeClass("hidden").dialog("open");
            });

        },
        bindCancelDelete: function() {

            $("#cancel-workout-delete").on('click', function() {
                $("#delete-workout-dialog").dialog("close");
            });

        },
        requestData: function() {

            this.requestWorkoutData();

        },

        requestWorkoutData: function() {

            res = $.ajax({
                method: 'GET',
                url: '/ajax/workout/' + data_from_django['workout_id'],
                cache: false
            });

            res.done(this._drawCharts);

        },
        _drawCharts: function(data) {

            // draw some charts to illistrate workout data
            var draw = function(graph_id, data) {

                var chart_data = [];

                if (['rep-ranges', 'muscle-groups'].indexOf(graph_id) >= 0) {

                    // iterate over the JSON and push to chart_data
                    for (i in data) {
                        chart_data.push([i, data[i]]);
                    }

                    // add chart specific values to the pie_chart template object
                    var chart_options = $.extend({}, pie_chart, {
                        title: {
                            text: (graph_id == 'rep-ranges') ? 'Rep Ranges' : 'Muscle Groups'
                        },
                        tooltip: {
                            pointFormat: '<b>{point.percentage:.1f}% of sets</b>'
                        },
                        legend: {
                            enabled: true
                        },
                        series: [{
                            type: 'pie',
                            name: 'Muscles Hit',
                            data: chart_data
                        }]
                    });

                } else if (['sets'].indexOf(graph_id) >= 0) {

                    // iterate over the JSON and push to chart_data
                    for (i in data) {
                        chart_data.push({
                            y: data[i][1],
                            exercise: data[i][0],
                            weight: data[i][2]
                        });
                    }

                    // add chart specific values to the pie_chart template object
                    var chart_options = $.extend({}, line_chart, {
                        title: {
                            text: 'Sets During Workout'
                        },
                        yAxis: {
                            title: {
                                text: 'Reps in Set'
                            }
                        },
                        tooltip: {
                            formatter: function() {
                                return this.point.exercise + ' - ' + this.y +
                                       'x' + this.point.weight + 'kg';
                            }
                        },
                        series: [{
                            name: 'Reps',
                            data: chart_data
                        }]
                    });

                } else if (['rep-ranges-per-muscle'].indexOf(graph_id) >= 0) {

                    // iterate over the JSON and push to chart_data
                    for (i in data) {
                        if (i !== 'muscles') {
                            var series_data = {
                                name: i,
                                data: data[i]
                            };
                            chart_data.push(series_data);
                        }
                    }

                    // add chart specific values to the pie_chart template object
                    var chart_options = $.extend({}, column_chart, {
                        series: chart_data,
                        title: {
                            text: 'Rep Ranges Per Muscle'
                        },
                        xAxis: {
                            categories: data['muscles']
                        },
                        yAxis: {
                            title: {
                                text: 'Sets in rep range'
                            }
                        }
                    });
                }

                // render the chart passing all our config options
                $('#' + graph_id).highcharts(chart_options);

            };

            for (workout in data) {
                draw(workout, data[workout]);
            }

        }
    };

  /**
   * initialise the exercises page JavaScript once the DOM is ready
   */
   $(function() {
        workout.init();
   });

})(jQuery);