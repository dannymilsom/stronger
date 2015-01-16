(function ($) {

    var exercises = {
        init: function() {

            this.prepareDOM();
            this.requestData();
            this.bindListeners();

        },
        prepareDOM: function() {

            this.prepareExerciseDialog();

        },
        prepareExerciseDialog: function() {

            $("#exercise-dialog").dialog({
                autoOpen: false,
                title: 'Add A New Exercise'
            });

        },
        requestData: function() {

            this.requestBigThree();
            this.requestPopularExercises();

        },
        requestBigThree: function() {

            res = $.ajax({
                method: 'GET',
                url: '/ajax/big-three-progress/' + data_from_django['username'],
                cache: false
            });

            res.done(this._drawBigThree);

        },
        requestPopularExercises: function() {

            // we want to show the popular exercises
            res = $.ajax({
                method: 'GET',
                url: '/ajax/popular-exercises',
                cache: false
            });

            res.done(this._drawPopularExercises);

        },
        bindListeners: function() {

            this.bindExerciseDialog();

        },
        bindExerciseDialog: function() {

            $("#log-exercise").on('click', function(e) {
                $("#exercise-dialog").dialog("open").removeClass("hidden");
            });

        },
        _drawBigThree: function(data) {

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
            });

            $('#big-three').highcharts($.extend({}, line_chart, {
                series: history,
                title: {
                    text: 'Big Three History'
                },
                xAxis: {
                    type: 'datetime',
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
        _drawPopularExercises: function(data) {

            var categories = [];
            var chart_data = [];
            for (k in data) {
                for (exercise in data[k]) {
                    categories.push(exercise);
                    chart_data.push(data[k][exercise])
                }
            }

            $('#popular-exercises').highcharts($.extend({}, column_chart, {
                title: {
                    text: 'Popular Exercises (All Users)'
                },
                xAxis: {
                    categories: categories
                },
                yAxis: {
                    title: {
                        text: 'Sets'
                    }
                },
                series: [{
                    name: 'Popular Exercises',
                    data: chart_data
                }]
            }));
        }

    }

  /**
   * initialise the exercises page JavaScript once the DOM is ready
   */
   $(function() {
        exercises.init();
   })

})(jQuery);