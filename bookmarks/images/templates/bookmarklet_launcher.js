(function () {
    if (!window.bookmarklet) {
        bookmarklet_js = document.body.appendChild(document.createElement('script'));
        bookmarklet_js.src = '//127.0.0.1:8000/static/js/bookmarklet.js?r=' + Math.floor(Math.random() * 9999999999999999);
        window.bookmarklet = true;
    } else {
        bookmarkletLaunch();
    }
})();

// Приведенный выше скрипт проверяет, не был ли букмарклет уже загружен,
// проверяя значение переменной окна bookmarklet с по мощью булева выраже-
// ния if(!window.bookmarklet):