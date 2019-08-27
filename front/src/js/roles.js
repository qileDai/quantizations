// function Role() {
//
// };
//
// Role.prototype.listAddRole = function () {
//     var addBtn = $('#role-add-btn');
//     addBtn.click(function () {
//         xfzalert.alertOneInput({
//             'title': '添加角色',
//             'placeholder': '请输入角色',
//             'confirmCallback': function (inputValue) {
//                 xfzajax.post({
//                     'url': '/rbac/add_roles/',
//                     'data': {
//                         'rolename': inputValue,
//                     },
//                     'success': function (result) {
//                         console.log("safsdf")
//                         console.log(inputValue)
//                         if (result['code'] === 200) {
//                             // window.location.reload()
//                         } else {
//                             xfzalert.close()
//                             window.messageBox.showError(result['message'])
//                         }
//                     }
//                 });
//             }
//         });
//     });
// };
//
// Role.prototype.run = function () {
//     var self = this;
//     // self.listAddRole();
// };
//
// $(function () {
//     var role = new Role();
//     role.run();
// });