(function ($) {

    var exercise = {
        init: function() {

            this.prepareDOM();
            this.requestData();
            this.bindListeners();

        },
        prepareDOM: function() {

            this.prepareExerciseDialog();

        },
        prepareExerciseDialog: function() {

            $("#edit-exercise-dialog").dialog({
                autoOpen: false,
                title: 'Edit A Workout'
            });

        },
        bindListeners: function() {

            this.bindExerciseDialog();

        },
        bindExerciseDialog: function() {

            $("#edit-exercise").on('click', function(e) {
                $("#edit-exercise-dialog").dialog("open").removeClass("hidden");
            });

        },
        requestData: function() {

            this.requestExerciseData();

        },
        requestExerciseData: function() {

            $.ajax({
                method: 'GET',
                url: '/ajax/exercises/' + $("#exercise-name").data('cleanName'),
                cache: false,
                success: this._drawCharts
            });

        },
        _drawCharts: function(data) {

            var parseAndDraw = function(chart_id, data) {

                var chart_data = [];

                if (['exercise-history'].indexOf(chart_id) >= 0) {

                    // sort the chart data
                    for (i in data) {
                        var series = {
                            name: i,
                            data: data[i]
                        }
                        chart_data.push(series);
                    }

                    var chart_options = $.extend({}, line_chart, {
                        title: {
                            text: 'Exercise History'
                        },
                        yAxis: {
                            title: {
                                text: 'Weight (kg)'
                            }
                        },
                        series: chart_data
                    });

                }
                else if ((['exercise-records'].indexOf(chart_id) >= 0)) {

                    // sort the chart data
                    personal_records = [];
                    for (i in data['personal_records']) {
                        personal_records.push(data['personal_records'][i][0]);
                    }

                    site_records = [];
                    for (i in data['site_records']) {
                        site_records.push(data['site_records'][i][0]);
                    }

                    var chart_options = $.extend({}, column_chart, {
                        title: {
                            text: 'Rep Records'
                        },
                        xAxis: {
                            min: 1,
                            tickInterval: 1,
                            title: {
                                text: 'Reps'
                            },
                            categories: ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11']
                        },
                        yAxis: {
                            title: {
                                text: 'Weight (kg)'
                            }
                        },
                        tooltip: {
                            formatter: function() {
                                return this.series.name + ' - <b>' + this.x + 
                                       'RM</b> is <b>' + this.y + '</b>';
                            }
                        },
                        series: [{
                            name: 'Personal Records',
                            data: personal_records
                        },
                        {
                            name: 'Site Records',
                            data: site_records
                        }]
                    });
                }

                // render the chart
                $('#' + chart_id).highcharts(chart_options);

            };

            for (workout in data) {
                parseAndDraw(workout, data[workout]);
            }
        }
    };

  /**
   * initialise the exercises page JavaScript once the DOM is ready
   */
   $(function() {
        exercise.init();
   });

})(jQuery);