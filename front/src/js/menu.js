function Menu() {

};

Menu.prototype.run = function () {
    var self = this;
    self.listenDeleteMenuEvent();
    self.listenLevelmenuEvent();
    self.submitMenuEvent();
};

Menu.prototype.listenDeleteMenuEvent = function () {
    $('.delete-menusBtn').on('click', function () {
        console.log("删除目录开始")
        var currentbtn = $(this);
        var tr = currentbtn.parent().parent();
        var pk = tr.attr('data-menu-id');
        xfzalert.alertConfirm({
            'title': '您确定要删除这个目录吗',
            'confirmCallback': function () {
                xfzajax.post({
                    'url': '/rbac/delete_menu/',
                    'data': {
                        'pk': pk
                    },
                    'success': function (result) {
                        if (result['code'] === 200) {
                            window.location.reload()
                        }
                    }
                });
            }
        });
    })
}
Menu.prototype.listenLevelmenuEvent = function () {
    $('.menu-level').on('change', function () {
        if ($(this).val() == 1) {
            console.log($(this).val())
            $('.menu-modal-body .from-group1').hide()

            $('.menu-modal-body .menu-model-title2').text('一级菜单名称')
            $('.level2-wrapper .form-control').attr('placeholder', "请输入一级菜单名称")

        } else {
            $('.menu-modal-body .from-group1').show()
            $('.menu-modal-body .menu-model-title2').text('二级菜单名称')
            $('.level2-wrapper .form-control').attr('placeholder', "请输入二级菜单名称")
        }
    })

}
Menu.prototype.editMenu = function () {

}

Menu.prototype.submitMenuEvent = function () {


    $('.menu-confirm').click(function () {
        var menu = $('.menu-title').val()
        var parent_menu = $('.parent-menu').val()
        console.log(menu,parent_menu)
        xfzajax.post({
        'url': '/rbac/add_menu/',
        'data': {
            'title': menu,
            'parent': parent_menu
        },
        'success': function (result) {
            if (result['code'] === 200) {
                xfzalert.alertSuccess("添加菜单成功", function () {
                    window.location.reload()
                })
            }
        }
    })
    })


}

$(function () {
    var menu = new Menu();
    menu.run()


})