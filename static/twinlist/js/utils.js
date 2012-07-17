var utils = function(utils, undefined) {
////// visible ////////////////////////////////////////////////////////////////
    var visible = {};
    
    visible.getStorageItem = function(key) {
        if ($.browser.webkit) {
            return sessionStorage.getItem(key);
        } else {
            return getCookie(key);
        }
    };
    
    visible.setStorageItem = function(key, value, days) {
        if ($.browser.webkit) {
            sessionStorage.setItem(key, value);
        } else {
            setCookie(key, value, days);
        }
    };

    visible.qs = (function(a) {
        if (a == "") return {};
        var b = {};
        for (var i = 0; i < a.length; ++i)
        {
            var p=a[i].split('=');
            if (p.length != 2) continue;
            b[p[0]] = decodeURIComponent(p[1].replace(/\+/g, " "));
        }
        return b;
    })(window.location.search.substr(1).split('&'));
    
////// hidden /////////////////////////////////////////////////////////////////
    function getCookie(name) {
        var cookies = document.cookie.split(";");
        
        for (var i = 0; i < cookies.length; i++) {
            var key = cookies[i].slice(0, cookies[i].indexOf("="));
            var value = cookies[i].slice(cookies[i].indexOf("=") + 1);
            key = key.trim();
            
            if (key === name) {
                return unescape(value);
            }
        }
        return null;
    }
    
    function setCookie(name, value, days) {
        var expires = new Date();
        expires.setDate(expires.getDate() + days);
        value = escape(value) + ((days) ? "" : "; expires=" +
                expires.toUTCString());
        document.cookie = name + "=" + value;
    }
    
    
    // expose interface
    return visible;
}(window.utils = window.utils || {});
