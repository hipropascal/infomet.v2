String.prototype.replaceAll = function (search, replacement) {
    var target = this;
    return target.replace(new RegExp(search, 'g'), replacement);
};

var active_menu = "3_Infomet.html";

$.get('/api/menu', function (menus) {
    console.log(menus);
    var menu_template = '<div class="menu-select" page="order_menu-name.html"> menu-name </div>';
    for (let i = 0; i < menus.length; i++) {
        $('.menu').append(menu_template.replaceAll('menu-name', menus[i][1]).replaceAll('order', menus[i][0]));
    }
    $('.menu-select').click(function () {
        $('.menu-select').not(this).removeClass('menu-selected');
        $(this).addClass('menu-selected');
        active_menu = $(this).attr('page');
        load_page(active_menu)
    });
    $('.menu-select[page="' + active_menu + '"]').addClass('menu-selected');
    load_page(active_menu);
});

function load_page(page) {
    $.get('/page/' + page, function (html) {
        $('.content').html('').append(html);
        window[active_menu.split('_')[1].split('.')[0]].show()
    });
}