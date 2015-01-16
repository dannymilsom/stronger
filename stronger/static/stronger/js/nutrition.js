(function ($) {

    var nutrition = {
        init: function() {

            this.prepareDOM();
            this.requestData();
            this.bindListeners();

        },
        prepareDOM: function() {

          this.prepareMealDialog();
          this.prepareBodyweightDialog();

        },
        prepareMealDialog: function() {

            $("#meal_record_dialog").dialog({
                autoOpen: false,
                title: 'Record Nutritonal Data'
            });

        },
        prepareBodyweightDialog: function() {

            $("#bodyweight_dialog").dialog({
                autoOpen: false,
                title: 'Record Your Body Weight'
            });

        },
        bindListeners: function() {

          this.bindOpenMealDialog();
          this.bindOpenBodyweight();
          this.bindSubmitBodyweight();
          this.bindSubmitNutrition();
          this.bindCalorieDateSelect();

        },
        bindOpenMealDialog: function() {

            $("#log-nutrition").on('click', function(e) {
                $("#meal_record_dialog").removeClass("hidden").dialog("open");
            });

        },
        bindOpenBodyweight: function() {

            $("#log-bodyweight").on('click', function(e) {
                $("#bodyweight_dialog").removeClass("hidden").dialog("open");
            });

        },
        bindSubmitNutrition: function() {
          $("#meal_record_dialog").submit(function(e){
                $(this).validate({
                  rules: {
                    date: {
                      required: true
                    },
                    calories: {
                      required: true
                    },
                    protein: {
                      required: true
                    },
                    carbs: {
                      required: true
                    },
                    fats: {
                      required: true
                    }
                  }
                });

                if (!$(this).valid()) {
                  e.preventDefault()
                }
          });
        },
        bindSubmitBodyweight: function() {
            $("#bodyweight_dialog").submit(function(e){

                $(this).validate({
                  rules: {
                    bodyweight: {
                      required: true
                    },
                    date: {
                      required: true
                    }
                  }
                });

                if (!$(this).valid()) {
                  e.preventDefault()
                }
                else {
                  // show spinner as we process the request
                  $("#bodyweight_submit").attr('disabled', true);
                  $("#bodyweight_dialog").append('<div class="loading-spinner col-xs-12 \
                              text-center"><i class="fa fa-spinner fa-spin"></i></div>');

                  res = $.ajax({
                      method: 'POST',
                      url: '/api/bodyweight',
                      data: $("#bodyweight_dialog").serialize() + "&user=1"
                  });

                  res.done(this._logBodyweight)
                }
              });
        },
        bindCalorieDateSelect: function() {

            self = this;
            $("#filter-calorie-dates").change(function() {
                self.requestNutritionData($("#filter-calorie-dates")
                    .find(":selected")
                     .val());
            });

        },
        requestData: function() {

            this.requestBodyweight();
            this.requestNutritionData();

        },
        requestBodyweight: function() {

            res = $.ajax({
                method: 'GET',
                url: '/api/bodyweight?user=' + data_from_django['user_id'],
                cache: false
            });

            res.done(this._drawBodyweightChart);

        },
        requestNutritionData: function(days) {

            days = days || 14;

            res = $.ajax({
                method: 'GET',
                url: '/ajax/nutrition-summary?days-back=' + days,
                cache: false
            });

            res.done(this._drawHighchart);

        },
        _logBodyweight: function(data) {

          $("#bodyweight_submit").attr('disabled', false);
          $(".loading-spinner").remove();
          $(".ajax-message").remove();
          $("#bodyweight_dialog").append('<div class="ajax-message \
                                          col-xs-12 green text-center"> \
                                          <i class="fa fa-check"></i> \
                                          <p class="text-center"> \
                                          Bodyweight logged</div>')
                                  .dialog("close");

        },
        _drawBodyweightChart: function(data){

            // parse and sort the data
            bw_chart_data = [];
            for (var i=0; i < data.length; i++) {
                var dt = new Date(data[i]['date']);
                bw_chart_data.push([Date.UTC(dt.getUTCFullYear(), dt.getUTCMonth(),
                                    dt.getUTCDate()), data[i]['bodyweight']]);
            }

            // render the chart
            $('#bw-chart').highcharts($.extend({}, line_chart_variable_dates, {
                chart: {
                    type: 'line',
                },
                title: {
                    text: 'Bodyweight History'
                },
                yAxis: {
                    title: 'Kg'
                },
                tooltip: {
                    headerFormat: '<b>{series.name}</b><br>',
                    pointFormat: '{point.x:%e. %b}: {point.y:.2f} m'
                },
                series: [{
                    name: 'Bodyweight',
                    data: bw_chart_data
                }]
            }));

        },
        _drawHighcharts: function(data) {

            var draw = function(chart_id, data) {
                var chart_data = [];

                if (['macros'].indexOf(chart_id) >= 0) {

                    for (i in data) {
                        chart_data.push([i, data[i]]);
                    }

                    var chart_options = $.extend({}, pie_chart, {
                        series: [{
                            type: 'pie',
                            name: 'Macro Nutrition',
                            data: chart_data
                        }],
                        legend: {
                            enabled: true
                        },
                        title: {
                            text: 'Average Macros'
                        }
                    });

                }
                else if (['calorie-tracker'].indexOf(chart_id) >= 0) {

                    var chart_options = $.extend({}, line_chart_variable_dates, {
                        title: {
                            text: 'Calories Consumed'
                        },
                        yAxis: {
                            title: {
                                text: 'kCal'
                            }
                        },
                        series: [{
                            name: 'kCal consumed',
                            data: chart_data,
                        }]
                    });

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
                }
                else if (['macro-breakdown'].indexOf(chart_id) >= 0) {
                    // iterate over the JSON and push to chart_data
                    for (m in data) {
                        chart_data.push({
                            name: m,
                            data: data[m]
                        })
                    }

                    var chart_options = $.extend({}, column_chart, {
                        series: chart_data,
                        title: {
                            text: 'Workout Macros vs Rest Macros'
                        },
                        xAxis: {
                            categories: ['Protein', 'Carbs', 'Fats']
                        },
                        yAxis: {
                            title: {
                                text: 'Grams'
                            }
                        },
                        legend: {
                            enabled: true,
                            layout: 'horizontal',
                            verticalAlign: 'bottom',
                            borderWidth: 0
                        }
                    });
                }

                // render the chart
                $('#' + chart_id).highcharts(chart_options);
            }

            // loop over the chart data from the server
            for (workout in data) {
                draw(workout, data[workout]);
            }
        }
    };

  /**
   * initialise the exercises page JavaScript once the DOM is ready
   */
   $(function() {
        nutrition.init();
   });

})(jQuery);