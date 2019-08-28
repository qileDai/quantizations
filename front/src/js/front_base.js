/**
 * Created by Administrator on 2019/1/3.
 */

/* 处理登录问题*/

function Auth() {
    var self = this;
    self.maskWrapper = $('.mask-wrapper');
    self.roleWrapper = $('.role-wrapper');
    self.menuWwrapper = $('.menu-wrapper');
    self.permissionWrapper = $('.permission-wrapper')
}

Auth.prototype.run = function () {
    var self = this;
    // self.listenShowHideEvent();
    self.listenUserShowHideEvent();
    self.listMenuShowHideEvent();
    self.listRoleShowHideEvent();
    self.listCancelEvent();
    self.listtenPermissionShowEvent();
};


Auth.prototype.showUserEvent = function () {
    var self = this;
    self.maskWrapper.show();
};
Auth.prototype.showRoleEvent = function () {
    var self = this;
    self.roleWrapper.show();
};
Auth.prototype.showPermissionEvent = function () {
    var self = this;
    self.permissionWrapper.show();
}

Auth.prototype.showMenuEvent = function () {
    var self = this;
    self.menuWwrapper.show();
    self.roleWrapper.show();
};


Auth.prototype.hideEvent = function () {
    var self = this;
    self.maskWrapper.hide();
    self.roleWrapper.hide();
    self.menuWwrapper.hide();
    self.permissionWrapper.hide();
};
Auth.prototype.listRoleShowHideEvent = function () {
    var self = this;
    var roleBtn = $('#role-add-btn');
    var closeBtn = $('.close-btn');
    roleBtn.click(function () {
        self.showRoleEvent();
    });
    closeBtn.click(function () {
        self.hideEvent();
    });

};
Auth.prototype.listCancelEvent = function () {
    var self = this;
    var cancelBtn = $('#cacle');
    cancelBtn.click(function () {
        self.hideEvent();
    })
}
Auth.prototype.listMenuShowHideEvent = function () {
    var self = this;
    var menuBtn = $('#menu-add-btn');
    var closeBtn = $('.close-btn');
    menuBtn.click(function () {
        self.showMenuEvent();
    });
    closeBtn.click(function () {
        self.hideEvent();
    });
}
Auth.prototype.listenUserShowHideEvent = function () {
    var self = this;
    var addBtn = $('#user-add-btn');
    var closeBtn = $('.close-btn');

    addBtn.click(function () {
        console.log("dddd")
        self.showUserEvent();
    });
    closeBtn.click(function () {
        self.hideEvent();
    });
};
Auth.prototype.listtenPermissionShowEvent = function () {
    var self = this;
    var permissionBtn = $('#permission-add-btn');
    var closeBtn = $('.close-btn');
    permissionBtn.click(function () {
        self.showPermissionEvent()
    });
    closeBtn.click(function () {
        self.hideEvent();
    });

};

$(function () {
    var auth = new Auth();
    auth.run();
});

/*处理用户*/
function User() {

};

User.prototype.run = function () {
    var self = this;
    self.listRoleSubmitEvent();
    self.listenDeleteRolesEvent();
 ;
};



User.prototype.listRoleSubmitEvent = function () {
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

User.prototype.listenDeleteRolesEvent = function () {
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
                        if (result['code'] === 200) {
                            window.location.reload()
                        }
                    }
                });
            }
        });
    });

}







$(function () {
    var user = new User();
    user.run();
})