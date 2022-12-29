function nav_init() {
    let state = get_nav_state(true);
    set_nav_state(state, false);
    adjust_nav_menu();
}

function nav_toggle() {
    let state = get_nav_state(false);
    set_nav_state((state == 'visible') ? 'hidden' : 'visible', true);
}

function adjust_nav_menu() {
    let menu = $('#menu');
    menu.height(get_menu_height());
}

function get_nav_state(set) {
    let state = Cookies.get('nav-state');

    if (state == null) {
        state = 'hidden';
        if (set) {
            Cookies.set('nav_state', state, { expires: 7 });
        }
    }

    return state;
}

function set_nav_state(state, animate) {

    let button = $('#nav-toggle');
    let menu = $('#menu');

    let transition = animate ? 'width 0.2s' : 'width 0.0s';
    menu.css('transition', transition);

    if (state == 'visible') {
        if (!button.hasClass('is-active')) {
            button.addClass('is-active');
        }

        menu.width(get_menu_width());
    }
    else if (state == 'hidden') {
        if (button.hasClass('is-active')) {
            button.removeClass('is-active');
        }

        menu.width(0);
    }

    Cookies.set('nav-state', state, { expires: 7 });
}

function get_menu_height() {

    let menu = $("#menu");

    let menu_padding =
        parseInt(menu.css("padding-top").slice(0, -2)) +
        parseInt(menu.css("padding-bottom").slice(0, -2));

    let footer = $("#contentinfo");
    let document_height = (
        footer.offset().top +
        footer.height() +
        parseInt(footer.css("margin-bottom").slice(0, -2))
    );

    return Math.max(
        document_height,
        $(window).height()
    ) - menu_padding;
}

function get_menu_width() {

    let content = $("#menu-inner")

    let menu_padding =
        parseInt(content.css("padding-left").slice(0, -2)) +
        parseInt(content.css("padding-right").slice(0, -2));

    return menu_padding + content.width()
}
