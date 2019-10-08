
function User() {

};

User.prototype.run = function () {
    var self = this;
    self.listDelteUsersEvent();
    self.listUserSubmintEvent();
    self.listenEditUserShowEvent();

};

User.prototype.listUserSubmintEvent = function () {
    var siginupGroup = $('.singup-group');
    var userSubmitBtn = $('#user-confirm');
    userSubmitBtn.click(function () {
        console.log("用户添加页面")
        var usernameInput = siginupGroup.find("input[name='usernamea']")
        var phonenumber =  siginupGroup.find("input[name='phone_number']")
        var emailInput = siginupGroup.find("input[name='email']")
        var passwordInput = siginupGroup.find("input[name='password']")
        var roleInput = siginupGroup.find("select[name='userrole']")
        var username = usernameInput.val()
        var phone_number = phonenumber.val()
        var email = emailInput.val()
        var password = passwordInput.val()
        var role = roleInput.val()
        console.log(username, email, password,role)

        xfzajax.post({
            'url': '/rbac/add_users/',
            'data': {
                'username': username,
                'phone_number':phone_number,
                'password': password,
                'email': email,
                'roles':role
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

$(function () {
    var user = new  User();
    user.run();
})