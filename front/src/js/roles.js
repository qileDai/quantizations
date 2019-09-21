
function Role() {

};

Role.prototype.run = function () {
    var self = this;
    self.listenDeleteRolesEvent();
    self.listRoleSubmitEvent();

};

Role.prototype.listenDeleteRolesEvent = function () {
    var self = this;
    $('.delete-roles-btn').on("click", function () {
        var currentbtn = $(this);
        var tr = currentbtn.parent().parent();
        var pk = tr.attr('data-role-id');
        console.log(pk)
        xfzalert.alertConfirm({
            'title': '您确定要删除这个角色吗',
            'confirmCallback': function () {
                xfzajax.post({
                    'url': '/rbac/delete_roles/',
                    'data': {
                        'pk': pk
                    },
                    'success': function (result) {
                        console.log(result)
                        if (result['code'] === 200) {
                            window.location.reload()
                        }
                    }
                });
            }
        });
    });

}
Role.prototype.listRoleSubmitEvent = function () {
    roleGroup = $('.role-modal-body ');
    var roleBtn = $('#role-confirm');
    roleBtn.click(function () {
        rolename = roleGroup.find("input[name='rolename']").val()
        permission = roleGroup.find("select[name='permission']").val()
        console.log(rolename, permission)

        xfzajax.post({
            'url': '/rbac/add_roles/',
            'data': {
                'rolename': rolename,
                'permission': permission
            },
            'success': function (result) {
                if (result['code'] === 200) {
                    console.log("sdf")
                    xfzalert.alertSuccess("添加角色成功", function () {
                        window.location.reload()
                    });
                }
            }
        })
    })
};

$(function () {
    var role = new Role();
    role.run();
})