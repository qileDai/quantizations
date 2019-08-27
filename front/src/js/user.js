

function User() {

};

User.prototype.listAddUserEvent = function(){
   var addBtn = $('#user-add-btn');
   addBtn.click(function () {
       xfzalert.alertOneInput({
           'title':'添加新闻分类',
            'placeholder':'请输入新闻分类',
            'confirmCallback':function (inputValue) {

            }
       });
   })
}

User.prototype.run = function () {
  var self = this;
  self.listAddUser();
};

$(function () {
    var usr = new User();
    usr.run();
});