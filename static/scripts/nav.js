$(document).ready(function () {
    let state = Cookies.get('nav-state');
    
    if (state == null) {
        state = 'hidden';
        Cookies.set('nav-state', state, { expires: 7 });
    }
    
    set_nav_state(state);

    let menu = $('#menu');
    menu.height(get_menu_height());
});

$(window).on('resize', function () {
    let menu = $('#menu');
    menu.height(get_menu_height());
});

$('#nav-toggle').click(function () {

    let state = Cookies.get('nav-state');

    if (state == null) {
        state = 'hidden';
    }

    state = (state == 'visible') ? 'hidden' : 'visible';

    set_nav_state(state);
});

function set_nav_state(state) {

    let button = $('#nav-toggle');
    let menu = $('#menu');

    if (state == 'visible') {
        if (!button.hasClass('is-active')) {
            button.addClass('is-active');
        }

        menu.css('padding', '1em').width('144px');
    }
    else if (state == 'hidden') {
        if (button.hasClass('is-active')) {
            button.removeClass('is-active');
        }
        
        menu.width(0).delay(200).queue(function (next) {
            $(this).css('padding', 0);
            next();
        });
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
        footer.css("margin-bottom").slice(0, -2)
    );

    return Math.max(
        document_height,
        $(window).height()
    ) - menu_padding;
}
