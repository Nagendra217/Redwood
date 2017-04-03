var Ajax = (function  ( window, undefined) {
    var module = {};
    var init = function  () {
        $.ajaxSetup({
            crossDomain: false, 
            beforeSend: function(xhr, settings) {
                if (!csrfSafeMethod(settings.type)) {
                    xhr.setRequestHeader("X-CSRFToken", module.getCookie('csrftoken'));
                }
            }
        });
    }
    var error = function  (e) {
        console.log(e);
        Alert.warning('Sorry! We are unable to process your request.')
    }
    var success = function  (data) {
        console.log(data);
    }
    var csrfSafeMethod = function  (method) {
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }
    module.getCookie = function  (name) {
        var cookieValue = null;
        if (document.cookie && document.cookie != '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = jQuery.trim(cookies[i]);
                if (cookie.substring(0, name.length + 1) == (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    module.send = function (options,callback) {
        var defaults = {
            url: '',
            type: 'GET',
            cache: true,
            async: true,
            dataType: 'JSON',
            data: {},
            error: error,
            success: function (data) {
                callback(data);
            }
        }
        $.extend(defaults,options);
        if (callback != 'undefined') options.success = callback
        $.ajax(options).done(function(data,textStatus, jqXHR) {
            if (jqXHR.status == 278)
            {
                Alert.warning('Your session has expired. Please login');
                setTimeout(function function_name (argument) {
                    window.location.href = '/accounts/login';
                },2000);
            }
            if (options.scroll_bottom){
                $('html, body').animate({ scrollTop: $(document).height() }, 1500);
            }
                
        });
    }
    init();
    return module;
})( window );