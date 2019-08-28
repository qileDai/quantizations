
function Permission() {

}

Permission.prototype.run  =function () {
    var self = this;
    self.listenPermissionSubmitEvent();

};
Permission.prototype.listenPermissionSubmitEvent = function(){
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
    var permission = new Permission();
    permission.run();
})