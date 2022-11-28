function set_banner_margin() {
    let window = $(document);
    let banner = $('#banner');

    if (window.width() > min_width()) {
        banner.css('margin-top', '');
        return;
    }

    let nav_toggle = $('#nav-toggle');
    banner.css('margin-top', nav_toggle.height());
}

function min_width() {
    let nav_toggle = $('#nav-toggle');
    let title_width = $('#banner a').first().width();
    let nav_button_width = (
        nav_toggle.width() +
        parseInt(nav_toggle.css('padding-left')) +
        parseInt(nav_toggle.css('padding-right'))
    );
    return title_width + 2 * nav_button_width;
}