(function ($) {

    var meal = {
        init: function() {

            this.prepareDOM();
            this.bindListeners();

        },
        prepareDOM: function() {

            this.prepareMealDialog();
            this.drawCharts(data_from_django);

        },
        prepareMealDialog: function() {

            $("#edit-meal-dialog").dialog({
                autoOpen: false,
                title: 'Edit a meal'
            });

        },
        bindListeners: function() {

            this.bindOpenMealDialog();

        },
        bindOpenMealDialog: function() {

            $("#edit-meal").on('click', function(e) {
                $("#edit-meal-dialog").dialog("open").removeClass("hidden");
            });

        },
        drawCharts: function(data) {

            var draw = function(chart_id, data, type) {

                var chart_data = [],
                    chart_options = {
                        tooltip: {
                            pointFormat: '{series.name}: <b>{point.percentage:.1f}%</b>'
                        }
                    };

                if (type == 'pie') {
                    
                    var type = 'pie';
                    chart_options['plotOptions'] = {
                        pie: {
                            allowPointSelect: true,
                            cursor: 'pointer',
                            dataLabels: {
                                enabled: false
                            },
                            showInLegend: true
                        }
                    };
                    chart_options['series'] = [{
                        type: type,
                        name: 'Macro Nutrition',
                        data: chart_data
                    }];
                    chart_options['title'] = {
                        text: 'Macro Nutrition (%)'
                    };
                    chart_options['tooltip'] = {
                        pointFormat: '<b>{point.percentage:.1f}%</b>'
                    };

                    for (i in data) {
                        chart_data.push([i, data[i]]);
                    }
                }
                else if (type == 'column') {

                    chart_options['chart'] = {
                        type: type
                    };
                    chart_options['xAxis'] = {
                        gridLineWidth: 0,
                        labels: {
                            enabled: true
                        },
                        categories: [
                            'Fats',
                            'Carbs',
                            'Protein'
                        ]
                    };
                    chart_options['yAxis'] = {
                        gridLineWidth: 0,
                        title: {
                            text: 'Calories'
                        }
                    };
                    chart_options['legend'] = {
                        enabled: false,
                        layout: 'vertical',
                        align: 'right',
                        verticalAlign: 'middle',
                        borderWidth: 0
                    };
                    chart_options['plotOptions'] = {
                        column: {
                            pointPadding: 0.2,
                            borderWidth: 0
                        }
                    };
                    chart_options['title'] = {
                        text: 'Macro Nutrition (kCal)'
                    };
                    chart_options['series'] = [{
                        name: 'Meal Macro Nutrition',
                        data: chart_data
                    }];
                    chart_options['tooltip'] = {
                        pointFormat: '<b>{point.y} kCal</b>'
                    };

                    for (i in data) {
                        chart_data.push(data[i]);
                    }
                }

                // render the chart
                $('#' + chart_id + "-" + type).highcharts(chart_options);

            };

            for (nutrition in data) {
                draw(nutrition, data[nutrition], 'pie');
                draw(nutrition, data[nutrition], 'column');
            }

        }
    };

  /**
   * initialise the exercises page JavaScript once the DOM is ready
   */
   $(function() {
        meal.init();
   });

})(jQuery);