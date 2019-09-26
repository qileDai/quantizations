function Account() {
    var self = this;
    self.accountWrapper = $('.add-account-wrapper');
    self.curryWrapper = $('.account-curry-wrapper');
    self.totalProperty = $('.property-total-wrapper');
    self.detailsProperty = $('.property-details-wrapper');
    self.carryWrapper = $('.account-carry-curry-wrapper');

};


Account.prototype.run = function () {
    var self = this;
    self.listenShowHideAddAccount();
    self.listenShowHideCurryWrapper();
    self.listPropertyTotalShowHideEvent();
    // self.listenPropertyDetailsShowEvent();
    self.listtenToalAccountCloseEvent();
    self.listtenPropertyDetailsCloseEvent();
    self.deleteAccount();
    self.listenSubmitAccount();
    self.listendenominationEvent();
    self.listtencuyyencyShow();
    self.showCollectAsset();
    self.showDetailProperty();
    self.refershAccountEvent();
    // self.listenEditAccount();

}

Account.prototype.showDetailProperty = function () {
    var self = this;
    $('.update-property').on('click', function () {
        var currentbtn = $(this);
        var tr = currentbtn.parent().parent();
        var pk = tr.attr('data-id');
        $('#add-account-pk').attr('account-pk', pk)
        console.log(pk)
        self.accountWrapper.show()
        xfzajax.post({
            'url': '/deal/accountinfo/',
            'data': {
                'pk': pk,
            },
            'success': function (result) {
                console.log(result)
                if (result['code'] === 200) {
                    account = result['data']
                    console.log(account)
                    var accountGroup = $('.account-body');
                    platform = account['platform']['Platform_name']
                    id = account['platform']['id']
                    console.log(platform)
                    title = account['title']
                    accesskey = account['accesskey']
                    secretkey = account['secretkey']
                    $("#platform option[value=" + id + "]").prop("selected", true);
                    // var option = $("<option>").val(id).text(platform);
                    //  $("#platform").append(option)
                    accountGroup.find("input[name='account-name']").val(title)
                    accountGroup.find("input[name='access']").val(accesskey)
                    accountGroup.find("input[name='scrent']").val(secretkey)
                    //

                    // tpl = template('add-accountInfo',{"account":account})
                    //
                    // var accountGroup = $('.account-modal-header')
                    // accountGroup.append(tpl)

                }
            }
        })
    })
}
Account.prototype.listenShowHideAddAccount = function () {
    var self = this;
    var closeBtn = $('.close-btn');
    $('#add-account-btn').click(function () {
        self.accountWrapper.show()
    });

    closeBtn.click(function () {
        console.log("sssfsdf")
        self.accountWrapper.hide()
        window.location.reload()
    });
    $('.cancel').click(function () {
        self.accountWrapper.hide();
        window.location.reload()
    })

};


Account.prototype.listendenominationEvent = function () {

    $('#account-curry-configuration').on('click', function () {
        $('.denomination-mask-account-wrapper').show();
        $('.denomination-account-wrapper').show();
    })

    $('.denomination-close-btn').on('click', function () {
        $('.denomination-mask-account-wrapper').hide();
        $('.denomination-account-wrapper').hide();

    });
    $('.cancel').click(function () {
        $('.denomination-mask-account-wrapper').hide();
        $('.denomination-account-wrapper').hide();
    })

}

Account.prototype.listPropertyTotalShowHideEvent = function () {
    var self = this;
    var closeBtn = $('.close-btn');
    $('#property-total').click(function () {
        self.totalProperty.show()
    });
    closeBtn.click(function () {
        self.totalProperty.hide()
    });
    $('.cancel').click(function () {
        self.totalProperty.hide();
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
    });
    $('.cancel').click(function () {
        self.curryWrapper.hide();
    })

};

Account.prototype.listtenToalAccountCloseEvent = function () {
    $('.property-close-btn').on('click', function () {
        $('.property-total-wrapper').hide()
        window.location.reload()
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
        $('.refersh').attr('property-id', pk)
        // console.log(pk)
        xfzajax.post(
            {
                'url': '/deal/showassert/',
                'data': {
                    'pk': pk
                },
                'success': function (result) {
                    console.log(result)
                    if (result['code'] === 200) {
                        datas = result['data']
                        var properties = result['data']
                        console.log(properties)
                        var platform = datas['Platform_name']  //平台名称
                        // var asset_change = datas['asset_change']  //今日资产变化
                        // var original_assets = datas['original_assets'] //初始资产
                        // var history_profit = datas['history_profit'] //历史盈亏
                        // var withdraw_record = datas['withdraw_record'] //总提币
                        // var assets_dict = datas['assets_dict']   //资产表
                        // var profit_loss_dict = datas['profit_loss_dict'] //损益表
                        //
                        $('.property-account-value').text(platform)  //插入平台到html中
                        // var detailsGroup = $('.property-details-wrapper')
                        // detailsGroup.find('.assets-change .number').text(asset_change['number']) //资产变化
                        // detailsGroup.find('.assets-change .percentage').text(asset_change['percent']) //资产变化
                        // detailsGroup.find('.initial-asset .number').text(original_assets) //初始变化
                        //
                        // detailsGroup.find('.curry-account-total .total-number').text(withdraw_record) //总计提币
                        //
                        // detailsGroup.find('.history-profit  .number').text(history_profit['number']) //总计提币
                        // detailsGroup.find('.history-profit .percentage').text(history_profit['percent']) //总计提币

                        // var tpl1 = template("",{"assets_dict":assets_dict})
                        // var tpl2 = template("",{"profit_loss_dict":profit_loss_dict})
                        // var tpl = template("details-item",{"datas":datas})
                        // var detailsGroup = $(".property-details-wrapper");
                        // detailsGroup.append(tpl)
                        var tpl = template('property-details', {'properties': properties})
                        var accountProperty = $('#property-details-ids')
                        accountProperty.append(tpl)
                        // var detailsTab = $('#property-details')
                        // // var td = detailsTab.find("tbody tr td")
                        // $.each(assets_dict, function (key, value) {
                        //     console.log(key)
                        //     $.each(value, function (j, k) {
                        //         console.log(k)
                        //     })
                        // })

                    }
                }
            });
    });
    closeBtn.click(function () {
        self.detailsProperty.hide();
    });
    $('.cancel').click(function () {
        self.detailsProperty.hide();
    })

}


Account.prototype.showCollectAsset = function () {
    $('#property-total').click(function () {
        xfzajax.post({
            'url': '/deal/showcollectasset/',
            'success': function (result) {
                console.log(result)
            }
        })
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

Account.prototype.listenEditAccount = function (pk) {
    var self = this;
    var confirmBtn = $('.confirm');
    confirmBtn.on('click', function () {
        var account = $('.account-body');
        platform = $('#platform').find("option:selected").val()
        title = account.find("input[name='account-name']").val()
        accesskey = account.find("input[name='access']").val()
        secretkey = account.find("input[name='scrent']").val()
        xfzajax.post({
            'url': '/deal/editaccount/',
            'data': {
                'platform': platform,
                'title': title,
                'accesskey': accesskey,
                'secretkey': secretkey,
                'pk': pk,
            },
            'success': function (result) {
                if (result['code'] === 200) {
                    xfzalert.alertSuccess("添加账户成功！", function () {
                        window.location.reload()
                    });
                }
            }

        });

    })

}
Account.prototype.listenSubmitAccount = function (pk) {
    var confirmBtn = $('.confirm');

    confirmBtn.click(function () {
        var pk = $(this).attr('account-pk')
        console.log(pk)
        var account = $('.account-body');
        platform = $('#platform').find("option:selected").val()
        title = account.find("input[name='account-name']").val()
        accesskey = account.find("input[name='access']").val()
        secretkey = account.find("input[name='scrent']").val()
        var url = ''
        if (pk) {
            url = '/deal/editaccount/'
        } else {
            url = '/deal/addaccount/'
        }
        xfzajax.post({
            'url': url,
            'data': {
                'platform': platform,
                'title': title,
                'accesskey': accesskey,
                'secretkey': secretkey,
                'pk': pk,
            },
            'success': function (result) {
                if (result['code'] === 200) {
                    if (pk) {
                        xfzalert.alertSuccess("编辑账户成功！", function () {
                            window.location.reload()
                        });
                    } else {
                        xfzalert.alertSuccess("添加账户成功！", function () {
                            window.location.reload()
                        });
                    }
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
        console.log("*")
        console.log(num, currency, pk)
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

Account.prototype.listtencuyyencyShow = function () {
    var self = this;
    var closeBtn = $('.close-btn');
    $('.mention-money').click(function () {
        self.carryWrapper.show();
        var currentbtn = $(this);
        var tr = currentbtn.parent().parent();
        var pk = tr.attr('data-id');
        self.listenWithDraw(pk)

    });
    closeBtn.click(function () {
        self.carryWrapper.hide()
    });
    $('.cancel').click(function () {
        self.carryWrapper.hide();
    })


};

Account.prototype.listenWithDraw = function (pk) {
    var self = this;
    var btn = $('.carry-confirm')
    btn.click(function () {
        num = $('#currency-number').val()
        currency = $('#currency').val()
        console.log("*")
        console.log(num, currency, pk)
        xfzajax.post({
            'url': '/deal/withdraw/',
            'data': {
                'num': num,
                'currency': currency,
                'pk': pk,
            },
            'success': function (result) {
                if (result['code'] === 200) {
                    xfzalert.alertSuccess("提币成功", function () {
                        window.location.reload()
                    })
                }
            }
        })
    })
}

Account.prototype.refershAccountEvent = function () {
    var self = this;
    $('#details-refersh').click(function () {
        console.log("ssdfas")
        self.detailsProperty.hide();
        setTimeout(function () {
           self.detailsProperty.show()

        }, 100);


        pk = $(this).attr('property-id')
        // xfzajax.post({
        //     'url': '/deal/showassert/',
        //     'data': {
        //         'pk': pk
        //     },
        //     'success':function (result) {
        //         if(result['code'] === 200 ){
        //             var properties = result['data']
        //             console.log(properties)
        //             var tpl = template('property-details',{'properties':properties})
        //             var accountProperty = $('#property-details-ids')
        //             accountProperty.replace(tpl)
        //         }
        //     }
        // })
    })
}

$(function () {
    var account = new Account();
    account.run();
})