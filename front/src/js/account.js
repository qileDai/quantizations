function Account() {
    var self = this;
    self.accountWrapper = $('.add-account-wrapper');
    self.curryWrapper = $('.account-curry-wrapper');
    self.totalProperty = $('.property-total-wrapper');
    self.detailsProperty = $('.property-details-wrapper');

};


Account.prototype.run = function () {
    var self = this;
    self.listenShowHideAddAccount();
    self.listenShowHideCurryWrapper();
    self.listPropertyTotalShowHideEvent();
    self.listenPropertyDetailsShowEvent();
    self.listtenToalAccountCloseEvent();
    self.listtenPropertyDetailsCloseEvent();
    self.deleteAccount();
    self.listenSubmitAccount();

}

Account.prototype.listenShowHideAddAccount = function () {
    var self = this;
    var closeBtn = $('.close-btn');
    $('#add-account-btn').click(function () {
        self.accountWrapper.show()
    });
    closeBtn.click(function () {
        self.accountWrapper.hide()
    });

};

Account.prototype.listPropertyTotalShowHideEvent = function () {
    var self = this;
    var closeBtn = $('.close-btn');
    $('#property-total').click(function () {
        self.totalProperty.show()
    });
    closeBtn.click(function () {
        self.totalProperty.hide()
    })

};

Account.prototype.listenShowHideCurryWrapper = function () {
    var self = this;
    var closeBtn = $('.close-btn');
    $('.add-property').click(function () {
        self.curryWrapper.show()
        var currentbtn = $(this);
        var tr = currentbtn.parent().parent();
        var pk = tr.attr('data-id');
        self.chargeAccountEvent(pk)
    });
    closeBtn.click(function () {
        self.curryWrapper.hide();
    })

};

Account.prototype.listtenToalAccountCloseEvent = function () {
    $('.property-close-btn').on('click', function () {
        $('.property-total-wrapper').hide()
    })
};

Account.prototype.listtenPropertyDetailsCloseEvent = function () {
    $('.property-close-btn').on('click', function () {
        $('.property-details-wrapper').hide()
    })
};

Account.prototype.listenPropertyDetailsShowEvent = function () {
    var self = this;
    var closeBtn = $('.close-btn');
    $('.check-property').on('click', function () {
        self.detailsProperty.show()
        var currentbtn = $(this);
        var tr = currentbtn.parent().parent();
        var pk = tr.attr('data-id');
        // console.log(pk)
        xfzajax.post({
            'url': '/deal/showassert/',
            'data': {
                'pk': pk
            },
            // 'success': function (result) {
            //     console.log("suceesee")
            //     console.log(result)
            //     if (result['code'] === 200) {
            //         datas = result['data']
            //         console.log(datas['Platform_name'])
            //         console.log(datas['asset_change'])
            //         console.log(datas['assets_dict'])
            //         console.log(datas['history_profit'])
            //     }
            // }
        });
    });
    closeBtn.click(function () {
        self.detailsProperty.hide();
    })

}

Account.prototype.deleteAccount = function () {
    var self = this;
    $('.delete-property').on('click', function () {
        var currentbtn = $(this);
        var tr = currentbtn.parent().parent();
        var pk = tr.attr('data-id');
        xfzalert.alertConfirm({
            'title': '您确定删除这个账户吗？',
            'confirmCallback': function () {
                xfzajax.post({
                    'url': '/deal/deleteaccount/',
                    'data': {
                        'pk': pk,
                    },
                    'success': function (result) {
                        if (result['code'] === 200) {
                            console.log(result)
                            window.location.reload()
                        }
                    }
                })
            }
        })
    })
}

Account.prototype.listenSubmitAccount = function () {
    console.log("sdaf")
    var confirmBtn = $('.confirm');
    var account = $('.account-body');
    confirmBtn.click(function () {
        platform = $('#platform').find("option:selected").val()
        title = account.find("input[name='account-name']").val()
        accesskey = account.find("input[name='access']").val()
        secretkey = account.find("input[name='scrent']").val()
        console.log("screnn")
        console.log(platform, title, secretkey, secretkey)
        xfzajax.post({
            'url': '/deal/addaccount/',
            'data': {
                'platform': platform,
                'title': title,
                'accesskey': accesskey,
                'secretkey': secretkey,
            },
            'success': function (result) {
                if (result['code'] === 200) {
                    xfzalert.alertSuccess("添加账户成功！", function () {
                        window.location.reload()
                    });
                }
            }
        });
    });
}

Account.prototype.chargeAccountEvent = function (pk) {
    var confirmBtn = $('.curry-confirm')
    confirmBtn.click(function () {
        num = $('#currency-number').val()
        currency = $('#currency').val()
        console.log("*" )
        console.log(num,currency,pk)
        xfzajax.post({
            'url': '/deal/chargeaccount/',
            'data': {
                'pk': pk,
                'num': num,
                'currency': currency,
            },
            'success': function (result) {
                if (result['code'] === 200) {
                    xfzalert.alertSuccess("增资成功", function () {
                        window.location.reload();
                    })
                }
            }
        })
    })
}


$(function () {
    var account = new Account();
    account.run();
})