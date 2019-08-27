/**
 * Created by Administrator on 2019/7/1.
 */

function Staff() {
    var self = this;
}

Staff.prototype.run = function () {
    var self = this;
    self.deleteStaffs()
}
Staff.prototype.deleteStaffs =function () {
    console.log("delete staffs")
    var staffDeleteBtn = $('#staff_detele');
    staffDeleteBtn.click(function () {
        var currentbtn = $(this);
        var tr = currentbtn.parent().parent;
        var telephone = tr.attr('data-staff');
        xfzalert.alertConfirm({
             'title':'您确定要删除这个分类吗？',
            'confirmCallback':function () {
                 xfzajax.post({
                     'url':'/cms/delete_staffs/',
                     'data':{
                         'telephone':telephone
                     },
                     'success':function (result) {
                         if(result['code']===200){
                             window.location.reload()
                         }
                     }
                 });
            }
        });

    });
}

$(function () {
    var staff = new Staff();
    staff.run();
})