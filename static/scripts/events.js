$(document).ready(function () {
    nav_init();
    set_banner_margin();
});

$(window).on('resize', function () {
    set_banner_margin();
    adjust_nav_menu();
});

$('#nav-toggle').click(function () {
    nav_toggle();
});