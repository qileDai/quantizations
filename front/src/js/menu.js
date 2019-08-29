
function Menu() {

};

Menu.prototype.run = function () {
    var self = this;
    self.listenDeleteMenuEvent();
};

Menu.prototype.listenDeleteMenuEvent = function(){
    $('.delete-menusBtn').on('click',function () {
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

$(function () {
    var menu = new Menu();
    menu.run()


})