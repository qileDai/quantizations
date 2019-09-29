function Girding() {
    var self = this;

};

Girding.prototype.run = function () {
    var self = this;
    // self.modalRun();
    // self.listenStepsEvent()
};

Girding.prototype.modalRun = function () {
    var self = this;
    var modalDataArray = new Array(self.step1, self.stept2);
    self.moadlDataControl("#modal", modalDataArray, self.modalCallback())
}
/**
 *
 * @param modalSelect modal选择符，本例为“#myModal”
 * @param modalDataArray html代码字符串数组
 * @param currentPageIndex 当前页码
 * @param direction 1表示下一页方向，-1表示上一页方向
 */
Girding.prototype.controlPageToggle = function (modalSelect, modalDataArray, currentPageIndex, direction) {
    var self = this;
    var arrayLength = modalDataArray.length;
    if (arrayLength <= 1)
        return;
    if (direction == 1) {
        //如果当前页是倒数第二页，则将下一页设置为尾页
        if (currentPageIndex == arrayLength - 2) {
            $(modalSelect + " " + ".next-page").text("提交");
        }

        //如果当前页是首页，添加上一页
        if (currentPageIndex == 0 && arrayLength > 1) {
            $(modalSelect + " " + ".previous-page").removeClass("hidden");
        }
        //更换modal-body和页码
        $(modalSelect + " " + ".page-index").text((++currentPageIndex).toString());
        $(modalSelect + " " + ".modal-body").html(modalDataArray[currentPageIndex]);
    } else {
        //如果当前页是尾页
        if (currentPageIndex == arrayLength - 1) {
            $(modalSelect + " " + ".next-page").text("下一页");
        }

        //如果当前页是正数第二页,则将上一页设置为首页
        if (currentPageIndex == 1) {
            $(modalSelect + " " + ".previous-page").addClass("hidden");
        }
        //更换modal-body和页码
        $(modalSelect + " " + ".page-index").text((--currentPageIndex).toString());
        $(modalSelect + " " + ".modal-body").html(modalDataArray[currentPageIndex]);
    }

}

/**
 *
 * @param modalSelect modal选择符
 * @param modalDataArray html代码字符串数组
 * @param modalCallback modal回调函数
 */
Girding.prototype.moadlDataControl = function (modalSelect, modalDataArray, modalCallback) {
    var self = this;
    //初始化模态框首页数据
    $(modalSelect + " " + ".modal-body").html(modalDataArray[0]);
    if (modalDataArray.length <= 1) {
        $(modalSelect + " " + ".next-page").text("提交");
    }

    //点击下一页
    $(modalSelect + " " + ".next-page").click(function () {
        //调用回调函数
        self.modalCallback()
        if ($(this).text() == "提交") {
            $(modalSelect).modal('hide');
            return;
        }
        //获取当前页码
        var currentPageIndex = parseInt($(modalSelect + " " + ".page-index").text());
        self.controlPageToggle(modalSelect, modalDataArray, currentPageIndex, 1);
    });

    //点击上一页
    $(modalSelect + " " + ".previous-page").click(function () {
        //获取当前页码
        var currentPageIndex = parseInt($(modalSelect + " " + ".page-index").text());
        controlPageToggle(modalSelect, modalDataArray, currentPageIndex, -1);
    });

    //关闭模态框时，重置为首页
    $(modalSelect).on('hidden.bs.modal', function () {
        $(modalSelect + " " + ".page-index").text((0).toString());
        if (modalDataArray.length <= 1) {
            $(modalSelect + " " + ".next-page").text("提交");
        } else {
            $(modalSelect + " " + ".next-page").text("下一页");
        }
        $(modalSelect + " " + ".modal-body").html(modalDataArray[0]);
        $(modalSelect + " " + ".previous-page").addClass("hidden");
    })
}

Girding.prototype.modalCallback = function () {
    alert("提交成功");
}


$(function () {
    var gird = new Girding();
    gird.run();
})


function Robot() {
    var self = this;
    self.robotWrapper = $('.robot-wrapper');
    self.tradingOnWrapper = $('.trading-on');
    self.tradingStrategyWrapper = $('.trading-strategy');
    self.setStrategyWrapper = $('.set-strategy');
    self.setRiskWrapper = $('.set-risk-strategy');


};

Robot.prototype.run = function () {
    var self = this;
    // self.initYstepEvent();
    self.listenClickRobotEvent();
    self.listenCloseRobotEvent();
    self.loadstepEvent();
    self.listenTradingRobotEvent();
    self.listenCreatTradingEvent();
    self.listenparameterEven();
    self.listenSubmitRobot();
    self.runRobotEvent();
    self.protectRelieve();
    self.getAccountInfoEvent();
    self.setCurrentPrice();
    // self.listenClickStragerty();
    // self.getAccountInfoEvent();

};
/**
 * 机器人步骤初始化
 */
Robot.prototype.initYstepEvent = function () {
    //根据jQuery选择器找到需要加载ystep的容器
//loadStep 方法可以初始化ystep

    $(".ystep").setStep(1);

};
Robot.prototype.loadstepEvent = function () {
    $(".ystep").loadStep({
        size: "large",
        color: "green",
        steps: [{
            title: "选择交易对",

        }, {
            title: "选择交易策略",
        }, {
            title: "设置策略参数",
        }, {
            title: "设置风险策略",
        },]
    });
}

Robot.prototype.listenClickRobotEaaavent = function () {

    var self = this;

    var btnPre = $("#btnPre")
    var btnNext = $("#btnNext")
    var robotDataArray = new Array(self.tradingOnWrapper, self.tradingStrategyWrapper, self.setStrategyWrapper, self.setRiskWrapper)
    var arrayLength = robotDataArray.length
    var num = 0;
    var creatrobotclick = 0
    // console.log(arrayLength)
    // if (arrayLength <= 1)
    //     return;
    $('#create-robot').on('click', function () {
        if (creatrobotclick == 0) {
            self.robotWrapper.show();
            robotDataArray[num].show()
            creatrobotclick++
        } else {
            console.log(creatrobotclick)
            self.robotWrapper.show()
        }

        $("#btnPre").unbind();
        btnPre.click(function () {
            console.log('num')
            if (num <= 0) {
                num = 0;
                // li[num].show().sibling().hide();
            } else {
                num--;
                $('#btnNext').text('下一步')
                // li[num].show().sibling().hide();

            }
            //跳转到上一个步骤
            $(".ystep").prevStep();

            console.log('val', robotDataArray)
            for (var i = 0; i < robotDataArray.length; i++) {

                if (num === i) {
                    robotDataArray[i].show()
                } else {
                    robotDataArray[i].hide()
                }
            }
        });
        $("#btnNext").unbind();
        btnNext.click(function () {


            var transactionCurrency = $('#curry').find(" option:selected").text();//交易币种
            var markettitle = $('#market').find(" option:selected").text();//交易市场
            var parameterscontrol = $('.parameters-control').find(" option:selected").text()//交易账户
            var resistancevalue = $('.strategy-parameters .trading-parameters .resistance-value').val()//阻力值
            var support = $('.strategy-parameters .trading-parameters .support').val()//支撑位
            var gridnumber = $('.strategy-parameters .trading-parameters .grid-number').val()//网格数量


            // alert('请选择交易币种/交易市场')


            var text = transactionCurrency + '/' + markettitle
            $('.trading-strategy .strategy-curry .curry').text(text);
            $('.set-strategy .strategy-curry .curry').text(text);
            $('.set-risk-strategy .strategy-curry .curry').text(text);


            $('.set-strategy-title .strategy-parameters-top .user').text(parameterscontrol)

            $('.set-risk-strategy .set-strategy-title .resistance').text(resistancevalue)
            $('.set-risk-strategy .set-strategy-title .support-level').text(support)
            $('.set-risk-strategy .set-strategy-title .girding-num').text(gridnumber)

            // $('.trading-strategy .strategy-curry .curry1').text(markettitle)

            var strategytitle = '网格交易v1.0'
            $('.strategy-name .strategy-button button').unbind();
            $('.strategy-name .strategy-button button').on('click', function () {
                $(this).addClass('active').siblings().removeClass('active');
                var strategytitle = $(this).text();//交易策略
                console.log(strategytitle);
                $('.set-strategy .strategy-title .strategy').text(strategytitle)
                $('.set-risk-strategy .strategy-title .curry').text(strategytitle)
            })

            // $('.set-strategy .strategy-curry .curry').text(transactionCurrency)
            // $('.set-strategy .strategy-curry .curry1').text(markettitle)
            console.log('next')
            if (num >= 2) {
                $('#btnNext').hide();
                $('#btnComplete').show();
                num = 3;
            } else {
                num++;
                $('#btnNext').text('下一步')
            }
            //跳转到下一个步骤

            // var stepNum = $(".ystep").getStep();
            // robotDataArray[stepNum+1].show()
            // console.log(stepNum)

            //  if (transactionCurrency=='---请选择---' ) {
            //     console.log(transactionCurrency)
            //         alert('请选择交易币种/交易市场')
            //          num=0;
            // }else{
            $(".ystep").nextStep();
            //  }


            $.each(robotDataArray, function (key, value) {
                if (num === key) {
                    value.show()
                } else {
                    value.hide()
                }
            })

        });
        $('.warninguser label').on('click', function () {
            $(this).toggleClass('btn-success')
        })

    })


}

/**
 * 机器人信息填写
 */
Robot.prototype.listenClickRobotEvent = function () {

    var self = this;

    var btnPre = $("#btnPre")
    var btnNext = $("#btnNext")
    var robotDataArray = new Array(self.tradingOnWrapper, self.tradingStrategyWrapper, self.setStrategyWrapper, self.setRiskWrapper)
    var num = 0;
    var creatrobotclick = 0
    $('#create-robot').on('click', function () {
        if (creatrobotclick == 0) {
            self.robotWrapper.show();
            robotDataArray[num].show()
            creatrobotclick++
        } else {
            console.log(creatrobotclick)
            self.robotWrapper.show()
        }
        $("#btnPre").unbind();
        btnPre.click(function () {
            console.log('num')
            if (num <= 0) {
                num = 0;
            } else {
                num--;
                $('#btnNext').show().text('下一步')
                $('#btnComplete').hide();
            }
            //跳转到上一个步骤
            $(".ystep").prevStep();
            console.log('val', robotDataArray)
            for (var i = 0; i < robotDataArray.length; i++) {

                if (num === i) {
                    robotDataArray[i].show()
                } else {
                    robotDataArray[i].hide()
                }
            }
        });

        $("#btnNext").unbind();
        btnNext.click(function () {


            var transactionCurrency = $('#curry').find(" option:selected").text();//交易币种
            var markettitle = $('#market').find(" option:selected").text();//交易市场
            var parameterscontrol = $('.parameters-control').find(" option:selected").text()//交易账户
            var resistancevalue = $('.strategy-parameters .trading-parameters .resistance-value').val()//阻力值
            var support = $('.strategy-parameters .trading-parameters .support').val()//支撑位
            var gridnumber = $('.strategy-parameters .trading-parameters .grid-number').val()//网格数量

            // alert('请选择交易币种/交易市场')
            var text = transactionCurrency + '/' + markettitle
            $('.trading-strategy .strategy-curry .curry').text(text);
            $('.set-strategy .strategy-curry .curry').text(text);
            $('.set-risk-strategy .strategy-curry .curry').text(text);

            $('.set-strategy-title .strategy-parameters-top .user').text(parameterscontrol)

            $('.set-risk-strategy .set-strategy-title .resistance').text(resistancevalue)
            $('.set-risk-strategy .set-strategy-title .support-level').text(support)
            $('.set-risk-strategy .set-strategy-title .girding-num').text(gridnumber)

            // $('.trading-strategy .strategy-curry .curry1').text(markettitle)

            var strategytitle = '网格交易v1.0'
            $('.strategy-name .strategy-button button').unbind();
            $('.strategy-name .strategy-button button').on('click', function () {
                $(this).addClass('active').siblings().removeClass('active');
                var strategytitle = $(this).text();//交易策略
                console.log(strategytitle);
                $('.set-strategy .strategy-title .strategy').text(strategytitle)
                $('.set-risk-strategy .strategy-title .curry').text(strategytitle)
            })

            if (num >= 2) {
                $('#btnNext').hide();
                $('#btnComplete').show();
                num = 3;
            } else {
                num++;
                $('#btnNext').text('下一步')
            }
            //跳转到下一个步骤

            $(".ystep").nextStep();
            $.each(robotDataArray, function (key, value) {
                if (num === key) {
                    value.show()
                } else {
                    value.hide()
                }
            })

        });
        $('.warninguser label').on('click', function () {
            $(this).toggleClass('btn-success')
        })
    })
}

/**
 * 关闭机器人弹出框
 */
Robot.prototype.listenCloseRobotEvent = function () {
    var closeBtn = $('.close-btn');
    var robotWrapper = $('.robot-wrapper');
    closeBtn.click(function () {
        robotWrapper.hide();

    })
};

/**
 * 机器人交易详情
 */
Robot.prototype.listenCreatTradingEvent = function () {
    $('.robot-details').on('click', function () {
        $('.tradingParticulars').show();
        $('.tradingShade').show();
        var currentbtn = $(this);
        var tr = currentbtn.parent().parent();
        var robot_id = tr.attr('data-id');
        console.log(robot_id)
        xfzajax.post({
            'url': '/deal/showtradedetail/',
            'data': {
                'robot_id': robot_id
            },
            'success': function (result) {
                var robot = result['data']
                console.log(robot)
                var tpl = template('robot-deal-details',{'robots':robot})
                var details = $('.tradingParticulars')
                details.append(tpl)
            }
        })
    })

}

Robot.prototype.listenTradingRobotEvent = function () {
    var tradingclosebtn = $('.trading-close-btn');
    var tradingParticulars = $('.tradingParticulars');
    var tradingShade = $('.tradingShade')
    var tradingloading = $('.trading-loading')
    var tradingending = $('.trading-ending')
    var tradingcontainer = $('.trading-container')
    var tradingendingtable = $('.trading-ending-table')
    tradingclosebtn.click(function () {
        tradingParticulars.hide();
        tradingShade.hide();
        window.location.reload()
    })
    tradingending.click(function () {

        tradingcontainer.hide();
        tradingendingtable.show();
        tradingloading.toggleClass('green')
        tradingending.toggleClass('green')

    })
    tradingloading.click(function () {
        tradingcontainer.show();
        tradingendingtable.hide();
        tradingending.toggleClass('green')
        tradingloading.toggleClass('green')
    })

}

Robot.prototype.listenparameterEven = function () {
    var parameterconfiguration = $('.parameter-configuration');
    var parameterclosebtn = $('.parameter-close-btn');
    var deleteproperty = $('.allocation');
    var tradingShade = $('.tradingShade')
    deleteproperty.click(function () {
        parameterconfiguration.show();
        tradingShade.show();
        var currentbtn = $(this);
        var tr = currentbtn.parent().parent();
        var robot_id = tr.attr('data-id');
        xfzajax.post({
            'url':'/deal/showconfiginfo/',
            'data':{
                'robot_id':robot_id,
            },
            'success':function (result) {
                var robot = result['data']
                console.log(robot)
                var tpl = template('robots-details',{'robots':robot})

                var robotGroup = $('#parameter-list-content')
                robotGroup.append(tpl)
            }
        })

    })
    parameterclosebtn.click(function () {
        parameterconfiguration.hide();
        tradingShade.hide();
    })
}

/**
 * 获取账户信息
 */
Robot.prototype.getAccountInfoEvent = function () {
    // var parantersGroup = $('.strategy-parameters')
    // id = parantersGroup.find("select['name='account']").val()
    console.log("sfsfsfsdf")
    // console.log(id)
    $('#robot-account').change(function () {
        var parantersGroup = $('.set-strategy')
        var currency = parantersGroup.find('.strategy-curry .curry').text()
        var strr = currency.split('/')
        var curry = strr[0]
        var market = strr[1]
        var id = $('#robot-account').find("option:selected").val()
        xfzajax.post({
            'url': '/deal/getaccountinfo/',
            'data': {
                'curry-title': curry,
                'market-title': market,
                'account_id': id,
            },
            'success': function (result) {
                if (result['code'] === 200) {
                    var data = result['data']
                    console.log(data)
                    var resistance = data['resistance']  //阻力位
                    var support_level = data['support_level'] //支撑位
                    var currency = data['currency']  //可用
                    var last = data['last']    //当前价
                    var market = data['market']  //市场价
                    //往设置策略中插入请求到的账户信息
                    $('.current-price .price').text(last)
                    $('.account-details .currency').text(currency)
                    $('.account-details .market').text(market)


                    var num = $('#stratery-girding-num ').val()
                    var free = $('#one-girding-free').val()
                    var girding = (resistance - support_level) / num
                    var mix_profit = (girding - (resistance * 2 + girding) * free) / resistance
                    var max_price = (girding - (support_level * 2 + girding) * free) / support_level
                    var profit = mix_profit + '%' + '-' + max_price + '%'
                    $('.resistance-value').val(resistance)
                    $('.support-value').val(support_level)
                    $('.profit-value').text(profit)
                    $('#stratery-girding-num').on('blur', function () {
                        if (!$('#stratery-girding-num').val() == '') {
                            var num = $('#stratery-girding-num ').val()
                            var free = $('#one-girding-free').val()
                            var girding = (resistance - support_level) / num     //单网格=（阻力位价格-支撑位价格）/网格数量
                            var mix_profit = (girding - (resistance * 2 + girding) * free) / resistance
                            var max_price = (girding - (support_level * 2 + girding) * free) / support_level
                            var profit = mix_profit + '%' + '-' + max_price  + '%'
                            $('.profit-value').text(profit)
                        }
                    })

                    $('#one-girding-free').on('blur', function () {
                        if (!$('#one-girding-free').val() == '') {
                            var num = $('#stratery-girding-num ').val()
                            var free = $('#one-girding-free').val()
                            var girding = (resistance - support_level) / num     //单网格=（阻力位价格-支撑位价格）/网格数量
                            var mix_profit = (girding - (resistance * 2 + girding) * free) / resistance
                            var max_price = (girding - (support_level * 2 + girding) * free) / support_level
                            var profit = mix_profit + '%' + '-' + max_price  + '%'
                            $('.profit-value').text(profit)
                        }
                    });
                    $('.resistance-value').on('blur',function () {
                        var resistance = $('.resistance-value').val()
                        var price = $('.current-price .price').val()
                        if(!resistance == ''){
                            if(resistance <= price){
                                console.log("sf")
                                $('.resistance-error-message .error').text("阻力位不得低于等于当前价")
                                // $('.resistance-value').after("<span class='error-account'>阻力位不得低于等于当前价</span>")
                            }else {
                                $('.resistance-error-message .error').text("")
                            }
                        }
                    });
                    $('')
                }
            }

        })

    })


}

/**
 * 点击交易策略切换
 */
Robot.prototype.listenClickStragerty = function () {
    var btnList = $('.deal-strategy')
    btnList.each(function (index, element) {
        var btn = $(element)
        btn.click(function () {
            btn.addClass('active').siblings().removeClass('active')
        })
    })
}

/**
 * 机器人提交
 */
Robot.prototype.listenSubmitRobot = function () {
    var btnComplete = $('#btnComplete ')
    //获取交易对数据
    btnComplete.click(function () {
        console.log("dafasdf")
        var robotGroup = $('.set-risk-strategy')
        var curry = robotGroup.find('.strategy-curry .curry').text()        //交易对
        var strr = curry.split('/')
        var curreny = strr[0]
        var market = strr[1]
        console.log('交易币种',curreny)
        console.log('交易市场',market)
        // var account = robotGroup.find('.strategy-parameters-top .user"').text() //交易账户
        var strategy = $('.set-risk-strategy .strategy-title .curry').text()
        console.log(strategy)//交易策略
        var account = $('#robot-account').find("option:selected").val()
        var resistance = $('.strategy-parameters-top .resistance').text()//阻力位
        var support = $('.strategy-parameters-top .support-level').text()
        var girding_num = $('.strategy-parameters-top .girding-num').text()
        var curren_price = $('.current-price .price').text()
        var millisecond = $('.millisecond-value').val()
        var mix_num = $('.mix-number .value ').val()
        var max_num = $('.max-number .value ').val()
        console.log('当前价:',curren_price,'毫秒:',millisecond,'最小数量:',mix_num,'最大数量',max_num)

        var free = $('.strategy-parameters-below .deal-account').text()  //交易手续费
        var girding_profit = $('.strategy-parameters-below .resistance').text()  //单网格利润
        var stoploss = $('.stopLoss .loss').val()
        var waring = $('.warning .value').val()

        var userList = $('.warninguser .active')
        console.log(userList)
        var users = ""
        for(var i = 0; i<userList.length; i++){
            var element = userList[i]
            console.log(element)
           var  user = $(element).text()
            // console.log(user)
            // users.push(user)
            users += user + ''
        }
        console.log(users)


        console.log('止损价',stoploss,waring)
        console.log('策略：',strategy, '账户：',account,'阻力位:', resistance, '支撑位:',support, '网格数量:',girding_num, '交易手续费',free, '网格利润',girding_profit)

        xfzajax.post({
            'url':'/deal/createrobot/',
            'data':{
                'trading_account':account,
                'currency':curreny,
                'market':market,
                'trading_strategy':strategy,
                'total_money':0,
                'float_profit':0,
                'realized_profit':0,
                'total_profit':0,
                'annual_yield':0,
                'protection':2,
                'status':0,
                'current_price':curren_price,
                'orders_frequency':millisecond,
                'resistance':resistance,
                'support_level':support,
                'girding_num':girding_num,
                'procudere_fee':free,
                'min_num':mix_num,
                'max_num':max_num,
                'girding_profit':girding_profit,
                'stop_price':stoploss,
                'warning_price':waring,
                'warning_account':users,
            },
            'success':function (result) {
                console.log(result)
                if(result['code'] === 200){
                    xfzalert.alertSuccess('添加机器人成功',function () {
                        window.location.reload()
                    })
                }
            }
        })

    })

}

/**
 * 机器人运行
 */
Robot.prototype.runRobotEvent = function () {

    $('.run-stop').click(function () {
        var currentbtn = $(this);
        var tr = currentbtn.parent().parent();
        var robot_id = tr.attr('data-id');

        var status = tr.attr('status')

        xfzajax.post({
            'url': '/deal/startrobot/',
            'data': {
                'robot_id': robot_id,
                'flag':status,
            },
            traditional: true,
            'success': function (result) {
                if (result['code'] === 200) {
                    xfzalert.alertSuccess("机器人ID:"+robot_id+" 运行成功")
                }else {
                    xfzalert.alertError("机器人ID: "+robot_id+" 运行失败")
                }
            }
        })
    })

};

/**
 * 设置当前价
 */
Robot.prototype.setCurrentPrice = function(){
    $('#set-currenPrice').click(function () {
        var price1 = $('.set-price').val()
        console.log(price1)
        $('.current-price .price').text(price1)
    })
}

/**
 * 机器人运行|禁止保护解除
 */
Robot.prototype.protectRelieve = function () {
    $('.protect-relieve').on('click', function () {
        var currentbtn = $(this);
        var tr = currentbtn.parent().parent();
        var robot_id = tr.attr('data-id');
        console.log(robot_id)
        var flag = $(this).text()
        console.log(flag)
        var element = $(this).siblings()
        var runflg = $(element[0]).text()
        console.log("****")
        console.log(runflg)
        if (runflg === '运行' || runflg === '运行(保护)') {
            var flg_text = '运行'
        }
        if (runflg === '停止' || runflg === '停止(保护)') {
            var flg_text = '停止'
        }
        if (flag === '保护') {
            var new_value = runflg + '(' + flag + ')'
            console.log(new_value)
            $(element[0]).text(new_value)
            $(this).text('解除')
        } else {
            $(element[0]).text(flg_text)
            $(this).text('保护')
            
        }
        xfzajax.post({
            'url':"/deal/robot_protection/",
            'data':{
                'robot_id':robot_id
            },
            'success':function (result) {
                console.log(result)
            }
        })
    })
}


$(function () {
    var robot = new Robot();
    robot.run();

});









