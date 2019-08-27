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
    self.listUserSubmintEvent();
    self.listRoleSubmitEvent();
    self.listDelteUsersEvent();
    self.listenDeleteRolesEvent();
    self.listenEditUserShowEvent();
    self.listenPermissionSubmitEvent();
};

User.prototype.listUserSubmintEvent = function () {
    var siginupGroup = $('.singup-group');
    var userSubmitBtn = $('#user-confirm');
    userSubmitBtn.click(function () {
        console.log("用户添加页面")
        var usernameInput = siginupGroup.find("input[name='username']")
        var emailInput = siginupGroup.find("input[name='email']")
        var passwordInput = siginupGroup.find("input[name='password']")
        var roleInput = siginupGroup.find("select[name='userrole']")
        var username = usernameInput.val()
        var email = emailInput.val()
        var password = passwordInput.val()
        var role = roleInput.val()
        console.log(username, email, password,role)

        xfzajax.post({
            'url': '/rbac/add_users/',
            'data': {
                'username': username,
                'password': password,
                'email': email,
                'role':role
            },
            'success': function (result) {
                if (result['code'] === 200) {
                    xfzalert.alertSuccess("添加用户成功", function () {
                        window.location.reload()
                    });
                }
            }
        });

    });

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
User.prototype.listDelteUsersEvent = function () {
    var self = this;
    $('.delete-users-btn').on("click", function () {
        var currentbtn = $(this);
        var tr = currentbtn.parent().parent();
        var pk = tr.attr('data_users_id');
        console.log(pk)
        xfzalert.alertConfirm({
            'title': '您确定要删除这个用户吗？',
            'confirmCallback': function () {
                xfzajax.post({
                    'url': '/rbac/delete_users/',
                    'data': {
                        'pk': pk,
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

User.prototype.listenEditUserShowEvent = function () {
    var self = this;
    var userGroup = $('.singup-group ');
    var userWrapper = $('.mask-wrapper');
    // console.log(user)
    $('.edit-user-btn').on('click', function () {
        var currentbtn = $(this);
        var tr = currentbtn.parent().parent();
        var user = tr.attr('data-name');
        var email = tr.attr('data-email');
        var role = tr.attr('data-role');
        console.log(role)
        var password = tr.attr('data-password')
        userWrapper.show()
        userGroup.find("input[name='username']").val(user)
        userGroup.find("input[name='password']").val(password)
        userGroup.find("input[name='email']").val(email)
        userGroup.find("select[name='userrole']").val(role)

    })
};

User.prototype.listenPermissionSubmitEvent = function(){
    var btn = $('#permission-confirm')
    var permissionGroup = $('.permission-modal-body ')
    btn.click(function () {
        title = permissionGroup.find("input[name='permission']").val()
        permissionUrl = permissionGroup.find("input[name='url']").val()
        menu = permissionGroup.find("select[name='menu']").val()
        console.log(title,permissionUrl,menu)
        xfzajax.post({
            'url': '/rbac/add_permission/',
            'data':{
                'title':title,
                'url':permissionUrl,
                'menu':menu
            },
            'success':function (result) {
                if(result['code'] === 200){
                    xfzalert.alertSuccess("添加权限成功",function () {
                         window.location.reload()
                    })
                }
            }
        })
    })
}

$(function () {
    var user = new User();
    user.run();
})