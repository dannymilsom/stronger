(function ($) {

    var profile = {
        init: function() {

            this.requestData();
            this.bindListeners();

        },
        bindListeners: function() {

            this.bindAddFriend();
            this.bindRemoveFriend();

        },
        bindAddFriend: function() {

            // send a friend request
            $("#add-friend").on("click", function() {
                $.ajax({
                    method: 'POST',
                    url: '/api/friends',
                    cache: false,
                    dataType: 'application/json',
                    data: {
                        'user': data_from_django['user'],
                        'friend': data_from_django['friend']
                    },
                    // success, json and 201 don't place nicely together
                    // http://stackoverflow.com/questions/2233553/
                    complete: function(xhr) {
                        if (xhr.status = 201) {
                            $("#add-friend").removeClass('btn-success')
                                            .addClass('btn-danger')
                                            .text("Unfollow");
                            $("#add-friend").attr("id", "remove-friend");
                        }
                    }
                });
            });

        },
        bindRemoveFriend: function() {

            // remove a friend instance
            if (data_from_django['friendship_id']) {
                $("#remove-friend").on("click", function() {
                    $.ajax({
                        method: 'DELETE',
                        url: '/api/friends/' + data_from_django['friendship_id'],
                        cache: false,
                        dataType: 'application/json',
                        data: {
                            'user': data_from_django['user'],
                            'friend': data_from_django['friend']
                        },
                        success: function(data) {
                            $("#remove-friend").removeClass('btn-danger')
                                               .addClass('btn-success')
                                               .text("Follow");
                            $("#remove-friend").attr("id", "add-friend");
                        }
                    });
                });
            }

        },
        requestData: function() {

            this.requestBodyweightData();
            this.requestBigThreeData();

        },
        requestBodyweightData: function() {

            $.ajax({
                method: 'GET',
                url: '/api/' + data_from_django['friend_username'] + '/bodyweight',
                cache: false,
                success: this._drawBodyweightChart
            });

        },
        requestBigThreeData: function() {

            $.ajax({
                method: 'GET',
                url: '/ajax/big-three-progress/' + data_from_django['friend_username'],
                cache: false,
                success: this._drawBigThreeChart
            });

        },
        _drawBodyweightChart: function(data) {

            var draw = function (data) {
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
                        data: data
                    }]
                }));
            }

            if (!data.length > 0) {
                data = window.defaultBodyweightData;
                // add an explanation about the default data
                $("#bw-chart").addClass("opacity");
            }

            var bw_data = []
            for (bw in data) {
                var dt = new Date(data[bw]['date']);
                bw_data.push([Date.UTC(dt.getUTCFullYear(), dt.getUTCMonth(), 
                                dt.getUTCDate()), data[bw]['bodyweight']])
            }

            draw(bw_data);

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
                        console.log(history[i])
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

        }
    }

  /**
   * initialise the exercises page JavaScript once the DOM is ready
   */
   $(function() {
        profile.init();
   });

})(jQuery);