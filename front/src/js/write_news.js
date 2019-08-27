/**
 * Created by Administrator on 2019/3/14.
 */

function News() {

};

News.prototype.run = function () {
    var self = this;
    self.listUploadFileEvent();
    // self.listenQiniuUploadFileEvent();
    self.initEditor();
    self.listSubmitNewsEvent();
};

News.prototype.listUploadFileEvent = function () {
    var uploadbtn = $('#thumbnail-btn');
    uploadbtn.change(function () {
        var file = uploadbtn[0].files[0];
        var formDate = new FormData();
        formDate.append('file', file);
        xfzajax.post({
            'url': '/cms/upload_file/',
            'data': formDate,
            'contentType': false,
            'processData': false,
            'success': function (result) {
                if (result['code'] === 200) {
                    console.log(result['data'])
                    var url = result['data']['url'];
                    console.log(url)
                    var thumbnail = $('#thumbnail-form');
                    thumbnail.val(url)

                }
            }
        });

    });
};

News.prototype.initEditor = function () {

    // var ue = UE.getEditor('ueditor');
    window.ue = UE.getEditor('ueditor', {
        'initialFrameHeight': 200,
        'serverUrl': '/ueditor/upload/'
    });


};

News.prototype.listenQiniuUploadFileEvent = function () {
    var self = this;
    var uploadBtn = $('#thumbnail-btn');
    uploadBtn.change(function () {
        var file = this.files[0];
        xfzajax.get({
            'url': '/cms/qntoken/',
            'success': function (result) {
                if (result['code'] === 200) {
                    var token = result['data']['token'];
                    // a.b.jpg = ['a','b','jpg']
                    // 198888888 + . + jpg = 1988888.jpg
                    var key = (new Date()).getTime() + '.' + file.name.split('.')[1];
                    var putExtra = {
                        fname: key,
                        params: {},
                        mimeType: ['image/png', 'image/jpeg', 'image/gif', 'video/x-ms-wmv']
                    };
                    var config = {
                        useCdnDomain: true,
                        retryCount: 6,
                        region: qiniu.region.z0
                    };
                    var observable = qiniu.upload(file, key, token, putExtra, config);
                    observable.subscribe({
                        'next': self.handleFileUploadProgress,
                        'error': self.handleFileUploadError,
                        'complete': self.handleFileUploadComplete
                    });
                }
            }
        });
    });
};

News.prototype.handleFileUploadProgress = function (response) {
    var total = response.total;
    var percent = response.percent;
    console.log(percent)
    console.log(total)

};

News.prototype.handleFileUploadError = function (error) {
    console.log(error.message)

};

News.prototype.handleFileUploadComplete = function (response) {
    console.log(response)
};

News.prototype.listSubmitNewsEvent = function () {
    var submitbtn = $('#submitbtn');
    submitbtn.click(function (event) {
        var btn = $(this);
        event.preventDefault();
        var title = $("input[name='title']").val();
        var categroy = $("select[name='categroy']").val();
        var desc = $("input[name='desc']").val();
        var thumbnail = $("input[name='thumbnail']").val();
        var content = window.ue.getContent();
        xfzajax.post({
            'url':'/cms/write_news/',
            'data':{
                'title':title,
                'categroy':categroy,
                'desc':desc,
                'thumbnail':thumbnail,
                'content':content,
            },
            'success':function (result) {
                if(result['code'] ===200){
                    xfzalert.alertSuccess("恭喜！新闻发布成功",function () {
                        window.location.reload()
                    });
                }
            }
        });
    });
};


$(function () {
    var news = new News();
    news.run();
});