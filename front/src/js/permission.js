function Permission() {

}

Permission.prototype.run = function () {
    var self = this;
    self.listenPermissionSubmitEvent();
    self.listenPermissionDeleteEvent();
    self.editPermission();

};
Permission.prototype.listenPermissionSubmitEvent = function () {
    var btn = $('#permission-confirm')
    var permissionGroup = $('.permission-modal-body ')
    btn.click(function () {
        title = permissionGroup.find("input[name='permission']").val()
        permissionUrl = permissionGroup.find("input[name='url']").val()
        menu = permissionGroup.find("select[name='menu']").val()
        console.log(title, permissionUrl, menu)
        xfzajax.post({
            'url': '/rbac/add_permission/',
            'data': {
                'title': title,
                'url': permissionUrl,
                'menu': menu
            },
            'success': function (result) {
                if (result['code'] === 200) {
                    xfzalert.alertSuccess("添加权限成功", function () {
                        window.location.reload()
                    })
                }
            }
        })
    })
}

Permission.prototype.listenPermissionDeleteEvent = function () {
    $('.delete-PermissioneBtn').on('click', function () {
        var currentbtn = $(this);
        var tr = currentbtn.parent().parent();
        var pk = tr.attr('data-permission-id');
        console.log(pk);
        xfzalert.alertConfirm({
            'title': '您确定要删除这个权限吗',
            'confirmCallback': function () {
                xfzajax.post({
                    'url': '/rbac/delete_permission/',
                    'data': {
                        'pk': pk
                    },
                    'success': function (result) {
                        console.log(result)
                        if (result['code'] === 200) {
                            console.log("fsd")
                            window.location.reload()
                        }
                    }
                })
            }
        })
    })
};

Permission.prototype.editPermission = function () {
    var self = this;
    $('#edit-permission').click(function () {
        console.log("sfd")
        $('.permission-wrapper').show();
        var currentbtn = $(this);
        var tr = currentbtn.parent().parent();
        var pk = tr.attr('data-permission-id');
        console.log(pk);
        $('#permission-confirm').attr('permission-id',pk)
        xfzajax.post({

        })
    })
}

$(function () {
    var permission = new Permission();
    permission.run();
})