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
            this.bindRepRangeFilter();

        },
        bindExerciseDialog: function() {

            $("#edit-exercise").on('click', function(e) {
                $("#edit-exercise-dialog").dialog("open").removeClass("hidden");
            });

        },
        bindRepRangeFilter: function() {

            self = this;
            $("#filter-rep-range").change(function() {
                self.requestExerciseData($("#filter-rep-range")
                    .find(":selected")
                    .val());
            });

        },
        requestData: function() {

            this.requestExerciseData();

        },
        requestExerciseData: function(reps) {

            var exercise = $("#exercise-name").data('cleanName'),
                rep_range = reps ? reps : '1';

            res = $.ajax({
                method: 'GET',
                url: '/ajax/exercises/' + exercise + '?reps=' + rep_range,
                cache: false
            });

            res.done(this._drawCharts);

        },
        _drawCharts: function(data) {

            var parseAndDraw = function(chart_id, data) {

                var chart_data = [];

                if (['exercise-progress'].indexOf(chart_id) >= 0) {

                    // sort the chart data
                    for (i in data) {
                        var dt = new Date(i);
                        chart_data.push([Date.UTC(dt.getUTCFullYear(), dt.getUTCMonth(),
                                         dt.getUTCDate()), data[i]]);
                    }

                    var chart_options = $.extend({}, line_chart, {
                        title: {
                            text: 'Exercise History'
                        },
                        xAxis: {
                            type: 'datetime'
                        },
                        yAxis: {
                            title: {
                                text: 'Weight (kg)'
                            }
                        },
                        series: [{
                            name: 'Rep History',
                            data: chart_data.sort()
                        }]
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