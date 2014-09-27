(function ($) {

    var recordWorkout = {
        init: function() {

            this.prepareDOM();
            this.bindListeners();

        },
        prepareDOM: function() {

            this.hideInputs();

        },
        hideInputs: function() {

            $(".workout-exercise").not(":eq(0)")
                                  .not(":nth-child(5n+1)")
                                  .addClass("hidden");

        },
        bindListeners: function() {

            this.submitWorkout();

        },
        submitWorkout: function() {

            // add the missing exercise values to hidden inputs on form submit event
            $("#workout-form").submit(function() {
                $(".workout-exercise.hidden").each(function() {
                    // only append the exercise name if the set has a set/rep input
                    if ($(this).next().val()) {
                        $(this).val($(this).prevAll(".workout-exercise")
                                           .not(".hidden")
                                           .first().val());
                    }
                });
                return true
            });

        }
    }

    $(function() {
        recordWorkout.init();
    });

})(jQuery);