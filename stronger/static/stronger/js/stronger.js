(function ($) {

    var stronger = {
        init: function() {

            this.prepareDOM();
            this.bindListeners();

        },
        prepareDOM: function() {

            this.changeBackground();
            this.prepareRegistrationDialog();
            this.prepareLoginDialog();
            this.prepareAjax();

        },
        changeBackground: function() {
        /*
            Change the HTML element background colour depending on the page
        */

            if ($("#welcome-message").length) {
                $("html").addClass("blue3-background");
            }
            else if ($("#login").length) {
                $("html").addClass("blue1-background");
            }
            else if ($("#signup").length) {
                $("html").addClass("blue1-background");
            }

        },
        prepareRegistrationDialog: function() {

            $("#registration-dialog").dialog({
                autoOpen: false, 
            });

        },
        prepareLoginDialog: function() {

            $("#login-dialog").dialog({
                autoOpen: false,
            });

        },
        prepareAjax: function() {

            // django CSRF patch for ajax requests
            // https://docs.djangoproject.com/en/dev/ref/contrib/csrf/
            function getCookie(name) {
                var cookieValue = null;
                if (document.cookie && document.cookie != '') {
                    var cookies = document.cookie.split(';');
                    for (var i = 0; i < cookies.length; i++) {
                        var cookie = jQuery.trim(cookies[i]);
                        // Does this cookie string begin with the name we want?
                        if (cookie.substring(0, name.length + 1) == (name + '=')) {
                            cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                            break;
                        }
                    }
                }
                return cookieValue;
            }
            var csrftoken = getCookie('csrftoken');

            function csrfSafeMethod(method) {
                // these HTTP methods do not require CSRF protection
                return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
            }
            $.ajaxSetup({
                beforeSend: function(xhr, settings) {
                    if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                        xhr.setRequestHeader("X-CSRFToken", csrftoken);
                    }
                }
            });

        },
        bindListeners: function() {

            this.openRegistrationDialog();
            this.openLoginDialog();
            this.submitLogin();
            this.submitRegistration();

        },
        openRegistrationDialog: function() {

            $(".register").on('click', function(e) {
                if ($(window).width() > 796) {
                    e.preventDefault();
                    $("#registration-dialog").dialog("open");
                }
            });

        },
        openLoginDialog: function() {

            $("#nav-login, #home-login").on('click', function(e) {
                if ($(window).width() > 796) {
                    e.preventDefault();
                    $("#login-dialog").dialog("open");
                }
            });

        },
        submitLogin: function() {

            $("#login-dialog").submit(function(e) {

                e.preventDefault();

                $(this).validate({
                  rules: {
                    username: {
                      required: true
                    },
                    password: {
                        required: true
                    }
                  }
                });

                if ($(this).valid() ){

                    $(".error-message").remove();
                    $(this).append('<div class="col-xs-12 text-center">' + 
                                   '<i class="fa fa-spinner fa-spin"></i></div>');

                    $.ajax({
                        method: 'POST',
                        url: '/login',
                        data: $(this).serialize(),
                        cache: false,
                        success: function(data) {
                            if (data['authenticated']) {
                                $('#login-dialog').dialog('close');
                                window.location.reload();
                            }
                            else {
                                $(".fa-spin").remove();
                                $('#login-dialog').append('<span class="col-xs-12 ' +
                                    'text-center error-message">Unable to authenticate ' +
                                    'using those credentials. Please try again.</span>');
                            }
                        }
                    });
                }
            });
        },
        submitRegistration: function() {

            $("#registration-dialog").submit(function(e) {

                e.preventDefault();

                $(this).validate({
                  rules: {
                    username: {
                      required: true
                    },
                    email: {
                        required: true,
                        email: true,
                    },
                    password: {
                        required: true
                    }
                  }
                });

                if ($(this).valid() ){
                    $(".error-message").remove();
                    $(this).append('<div class="col-xs-12 text-center">' + 
                                   '<i class="center-block fa fa-spinner fa-spin"></i></div>');

                    $.ajax({
                        method: 'POST',
                        url: '/signup',
                        data: $(this).serialize(),
                        cache: false,
                        success: function(data) {
                            if (!data['authenticated']) {
                                $('#registration-dialog').dialog('close');
                                window.location.reload()
                            }
                            else {
                                $(".fa-spin").remove();
                                $('#registration-dialog').append('<span class="col-xs-12 ' +
                                    'text-center error-message">Unable to create an ' +
                                    'account with those details. Please try again.</span>');
                            }
                        },
                    });
                }
            });

        }
    }

  /**
   * initialise the exercises page JavaScript once the DOM is ready
   */
   $(function() {
        stronger.init();
   });

})(jQuery);