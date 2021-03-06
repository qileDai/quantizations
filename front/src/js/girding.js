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
    self.oneStepRun();
    self.editRobotEvent();
    self.listenRightFlagEvent();
    self.getUser();
    self.submitTipsEvent();
    self.robotYieldEvent();
    // self.getRobotsId();
    // self.websocketRobot();
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
            if (num <= 0) {
                num = 0;
            } else {
                num--;
                $('#btnNext').show().text('下一步')
                $('#btnComplete').hide();
            }
            //跳转到上一个步骤
            $(".ystep").prevStep();
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
            // if(num == 1){
            //     console.log(num,"执行函数")
            //     self.listenCurrencySelecctedEvent();
            // }

            var transactionCurrency = $('#curry').find(" option:selected").text();//交易币种
            var markettitle = $('#market').find(" option:selected").text();//交易市场
            var parameterscontrol = $('.parameters-control').find(" option:selected").text()//交易账户
            var resistancevalue = $('.strategy-parameters .trading-parameters .resistance-value').val()//阻力值
            var support = $('.support-value').val()//支撑位
            var gridnumber = $('.strategy-parameters .trading-parameters .grid-number').val()//网格数量
            var free = $('#one-girding-free').val()
            var profit_value = $('.profit-value').text()
            var Theyareoften = $('.strategy-parameters .trading-parameters .millisecond-value').val()//挂单频率
            var mixnumber = $('.strategy-parameters .mix-number .mix-number-value  ').val()//单网格最小交易量
            var maxnumber = $('.strategy-parameters  .max-number .max-number-value ').val()//单网格最大交易量

            // alert('请选择交易币种/交易市场')
            var text = transactionCurrency + '/' + markettitle
            $('.trading-strategy .strategy-curry .curry').text(text);
            $('.set-strategy .strategy-curry .curry').text(text);
            $('.set-risk-strategy .strategy-curry .curry').text(text);

            $('.set-strategy-title .strategy-parameters-top .user').text(parameterscontrol)

            $('.set-risk-strategy .set-strategy-title .resistance').text(resistancevalue)
            $('.set-risk-strategy .set-strategy-title .support-level').text(support)
            $('.set-risk-strategy .set-strategy-title .girding-num').text(gridnumber)
            $('.strategy-parameters-below .deal-account').text(free + '%')
            $('.strategy-parameters-below .resistance').text(profit_value)
            var patt1 = /[\u4e00-\u9fa5]/;
            if (patt1.test(text)) {
                xfzalert.alertError("请选择交易币种/交易名称")
                return
            }
            ;
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
                if (parameterscontrol == '---请选择---') {
                    xfzalert.alertError("请选择交易账户")
                    return
                }
                ;
                if (Theyareoften.trim() == '') {
                    xfzalert.alertError("请输入挂单频率")
                    return
                }
                ;

                if (mixnumber.trim() == '') {
                    xfzalert.alertError("请输入单网格最小交易数量")
                    return
                }
                ;
                if (maxnumber.trim() == '') {
                    xfzalert.alertError("请输入单网格最大交易数量")
                    return
                }
                ;


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
        $('#btnNext1').attr('robot_id', robot_id)
        xfzajax.post({
            'url': '/deal/showtradedetail/',
            'data': {
                'robot_id': robot_id
            },
            'success': function (result) {
                var robot = result['data']
                var close = robot['closed_num']
                var opne = robot['open_num']
                // var closed_info = JSON.parse(robot['closed_info'])

                // console.log(closed_info)
                $('.deal-opening').text("(" + opne + ")")
                $('.deal-completed').text("(" + close + ")")
                console.log(robot)
                var tpl = template('robot-deal-details', {'robots': robot})
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
    // var tradingcontainer = $('.trading-particulars')
    // var tradingendingtable = $('.trading-ending-table')
    tradingclosebtn.click(function () {
        tradingParticulars.hide();
        tradingShade.hide();
        window.location.reload()

    })
    tradingending.click(function () {

        $('.trading-particulars').hide();
        $('.trading-ending-table').show();
        tradingloading.toggleClass('green')
        tradingending.toggleClass('green')

    })
    tradingloading.click(function () {
        $('.trading-particulars').show();
        $('.trading-ending-table').hide();
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
        $('#btnNext1').attr("robot_id", robot_id)
        xfzajax.post({
            'url': '/deal/showconfiginfo/',
            'data': {
                'robot_id': robot_id,
            },
            'success': function (result) {
                var robot = result['data']
                console.log(robot)
                // var users = result['data']['robot']['fields']['warning_account']
                //
                // var user = users.split('&')
                // console.log(user)
                var tpl = template('robots-details', {'robots': robot})

                var robotGroup = $('#parameter-list-content')
                robotGroup.append(tpl)
            }
        })

    })
    parameterclosebtn.click(function () {
        parameterconfiguration.hide();
        tradingShade.hide();
        window.location.reload()
    });
    $('.prevent-btn').click(function () {
        parameterconfiguration.hide();
        tradingShade.hide();
        window.location.reload()
    });
}

Robot.prototype.fomatFloat = function (num, n) {
    var f = parseFloat(num);
    if (isNaN(f)) {
        return false;
    }
    f = Math.round(num * Math.pow(10, n)) / Math.pow(10, n); // n 幂
    var s = f.toString();
    var rs = s.indexOf('.');
    //判定如果是整数，增加小数点再补0
    if (rs < 0) {
        rs = s.length;
        s += '.';
    }
    while (s.length <= rs + n) {
        s += '0';
    }
    return s;
}

/**
 * 获取账户信息
 */
Robot.prototype.getAccountInfoEvent = function () {
    var self = this;
    // var parantersGroup = $('.strategy-parameters')
    // id = parantersGroup.find("select['name='account']").val()
    // console.log(id)
    $('#robot-account').change(function () {
        var parantersGroup = $('.set-strategy')
        var currency = parantersGroup.find('.strategy-curry .curry').text()
        var strr = currency.split('/')
        var curry = strr[0]
        var market_cuurrency = strr[1]
        var id = $('#robot-account').find("option:selected").val()
        xfzajax.post({
            'url': '/deal/getaccountinfo/',
            'data': {
                'curry-title': curry,
                'market-title': market_cuurrency,
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
                    var total_currency = data['total_currency'].replace(/[^\d.]/g, "")
                    console.log(total_currency)
                    var total_market = data['total_market'].replace(/[^\d.]/g, "")
                    var currency_price = last.replace(/[^\d.]/g, "")
                    console.log(currency_price)
                    var total_money = Number(total_currency) * Number(currency_price) + Number(total_market)
                    console.log(total_money)
                    $('.current-price .price').attr("total_money",total_money.toFixed(2) + market_cuurrency)
                    // var total_input = currency/last

                    //往设置策略中插入请求到的账户信息
                    $('.current-price .price').text(last)
                    $('.account-details .currency').text(currency)
                    $('.account-details .market').text(market)


                    var num = $('#stratery-girding-num ').val()
                    var free = $('#one-girding-free').val() / 100
                    console.log("free", free)
                    var girding = (resistance - support_level) / num //单网格
                    console.log("单网格", girding)

                    var mix_profit = [girding - (resistance * 2 + girding) * free] / resistance
                    console.log("最小", mix_profit)
                    var max_price = (girding - (support_level * 2 + girding) * free) / support_level
                    console.log("最da", max_price)
                    var profit = self.fomatFloat(mix_profit * 100, 2) + '%' + '-' + self.fomatFloat(max_price * 100, 2) + '%'
                    $('.resistance-value').val(resistance)

                    $('.support-value').val(support_level)
                    //判断阻力位不能大于当前价
                    if (resistance <= last) {
                        xfzalert.alertError("阻力位不能小于等于当前价")
                    }
                    $('.profit-value').text(profit)
                    //网格数量焦点事件
                    $('#stratery-girding-num').on('blur', function () {
                        if (!$('#stratery-girding-num').val() == '') {
                            var num = $('#stratery-girding-num ').val()
                            var free = $('#one-girding-free').val() / 100
                            var girding = (resistance - support_level) / num     //单网格=（阻力位价格-支撑位价格）/网格数量
                            var mix_profit = (girding - (resistance * 2 + girding) * free) / resistance
                            var max_price = (girding - (support_level * 2 + girding) * free) / support_level
                            var profit = self.fomatFloat(mix_profit * 100, 2) + '%' + '-' + self.fomatFloat(max_price * 100, 2) + '%'
                            $('.profit-value').text(profit)
                        }
                    })
                    //交易手续费焦点事件
                    $('#one-girding-free').on('blur', function () {
                        if (!$('#one-girding-free').val() == '') {
                            var num = $('#stratery-girding-num ').val()
                            var free = $('#one-girding-free').val() / 100
                            var girding = (resistance - support_level) / num     //单网格=（阻力位价格-支撑位价格）/网格数量
                            var mix_profit = (girding - (resistance * 2 + girding) * free) / resistance

                            var max_price = (girding - (support_level * 2 + girding) * free) / support_level
                            var profit = self.fomatFloat(mix_profit * 100, 2) + '%' + '-' + self.fomatFloat(max_price * 100, 2) + '%'
                            $('.profit-value').text(profit)
                        }
                    });
                    //支撑位位失去焦点事件
                    $('.support-value').on('blur', function () {
                        console.log("支撑位")
                        var resistance = $('.resistance-value').val()
                        // var price = $('.current-price .price').text()
                        var support_level = $('.support-value').val()
                        console.log(support_level,resistance)

                        if (!support_level == '') {
                            console.log("wori")
                            var num = $('#stratery-girding-num ').val()
                            var free = $('#one-girding-free').val() / 100
                            var girding = (resistance - support_level) / num     //单网格=（阻力位价格-支撑位价格）/网格数量
                            var mix_profit = (girding - (resistance * 2 + girding) * free) / resistance

                            var max_price = (girding - (support_level * 2 + girding) * free) / support_level
                            var profit = self.fomatFloat(mix_profit * 100, 2) + '%' + '-' + self.fomatFloat(max_price * 100, 2) + '%'
                            $('.profit-value').text(profit)
                            console.log(profit)
                        }
                    })


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

        // var account = robotGroup.find('.strategy-parameters-top .user"').text() //交易账户
        var strategy = $('.set-risk-strategy .strategy-title .curry').text()
        console.log(strategy)//交易策略
        var account = $('#robot-account').find("option:selected").val()
        var total_money = $('.current-price .price').attr('total_money')
        console.log(total_money)

        var resistance = $('.strategy-parameters-top .resistance').text()//阻力位
        var support = $('.strategy-parameters-top .support-level').text()
        var girding_num = $('.strategy-parameters-top .girding-num').text()
        var curren_price = $('.current-price .price').text().replace(/[^\d.]/g, "")
        var millisecond = $('.millisecond-value').val()
        var mix_num = $('.mix-number .value ').val()
        var max_num = $('.max-number .value ').val()
        console.log('当前价:', curren_price, '毫秒:', millisecond, '最小数量:', mix_num, '最大数量', max_num)

        var free = $('.strategy-parameters-below .deal-account').text()  //交易手续费
        var girding_profit = $('.strategy-parameters-below .resistance').text()  //单网格利润
        var stoploss = $('.stopLoss .loss').val()
        var waring = $('.warning .value').val()

        var userList = $('.warninguser .active')
        console.log(userList)
        var users = []
        for (var i = 0; i < userList.length; i++) {
            var element = userList[i]
            console.log(element)
            var user = $(element).text()
            console.log($.trim(user))
            // console.log(user)
            // users.push(user)
            users += $.trim(user) + "&"
        }

        // console.log('止损价', stoploss, waring)
        // console.log('策略：', strategy, '账户：', account, '阻力位:', resistance, '支撑位:', support, '网格数量:', girding_num, '交易手续费', free, '网格利润', girding_profit)
        xfzajax.post({
            'url': '/deal/createrobot/',
            'data': {
                'trading_account': account,
                'currency': curreny,
                'market': market,
                'trading_strategy': strategy,
                'total_money': total_money,
                'float_profit': 0,
                'realized_profit': 0,
                'total_profit': 0,
                'annual_yield': 0,
                'protection': 1,
                'status': 0,
                'run_status': 1,
                'current_price': curren_price,
                'orders_frequency': millisecond,
                'resistance': resistance,
                'support_level': support,
                'girding_num': girding_num,
                'procudere_fee': free,
                'min_num': mix_num,
                'max_num': max_num,
                'girding_profit': girding_profit,
                'stop_price': stoploss,
                'warning_price': waring,
                'warning_account': users,
            },
            'success': function (result) {
                console.log(result)
                if (result['code'] === 200) {
                    xfzalert.alertSuccess('添加机器人成功', function () {
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
        var run_status = $(this).attr('run_status')
        var status = tr.attr('status')
        console.log(robot_id, run_status, status)
        if (run_status == 0 && status == 1) {
            run_status = 1
            status = 0
        } else if (run_status == 1 && status == 0) {
            run_status = 0
            status = 1
        } else if (status == 2 || status == 3) {
            $(this).attr('disabled', true)
        }

        xfzajax.post({
            'url': '/deal/startrobot/',
            'data': {
                'robot_id': robot_id,
                'flag': status,
                'run_status': run_status,
            },
            traditional: true,
            'success': function (result) {
                if (result['code'] === 200) {

                    xfzalert.alertSuccess("机器人ID:" + robot_id + " 运行成功", function () {
                        window.location.reload()
                    })
                } else {
                    xfzalert.alertError("机器人ID: " + robot_id + " 运行失败")
                }
            }
        })
    })

};

/**
 * 设置当前价
 */
Robot.prototype.setCurrentPrice = function () {
    $('#set-currenPrice').click(function () {
        var price = $('.set-price').val()
        if (!price == "") {
            $('.current-price .price').text(price)
        } else {
            xfzalert.alertError("请输入当前价")
        }

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
        var status = tr.attr('status');
        var protect = tr.attr('protect')
        console.log(robot_id, status, protect)

        // console.log(flag)
        // var element = $(this).siblings()
        // var runflg = $(element[0]).text()
        // console.log("****")
        // console.log(runflg)
        // if (runflg === '运行' || runflg === '运行(保护)') {
        //     var flg_text = '运行'
        // }
        // if (runflg === '停止' || runflg === '停止(保护)') {
        //     var flg_text = '停止'
        // }
        // if (flag === '保护') {
        //     var new_value = runflg + '(' + flag + ')'
        //     console.log(new_value)
        //     $(element[0]).text(new_value)
        //     $(this).text('解除')
        // } else {
        //     $(element[0]).text(flg_text)
        //     $(this).text('保护')
        //
        // }
        if (status == 1 && protect == 1) {
            status = 2
            protect = 0
        } else if (status == 2 && protect == 0) {
            status = 1
            protect = 1
        } else if (status == 0 && protect == 1) {
            status = 3
            protect = 0
            // var element = $(this).siblings()[0];
            // console.log(element)
            // $(element).attr('disabled', true)
        } else if (status == 3 && protect == 0) {
            status = 0
            protect = 1
        }
        console.log('status:' + status, 'protect:' + protect)
        xfzajax.post({
            'url': "/deal/robot_protection/",
            'data': {
                'robot_id': robot_id,
                'flag': status,
                'protect': protect,
            },
            'success': function (result) {
                console.log(result)
                // window.location.reload()
            }
        })
    })
}

/**
 * 一键运行停止
 */

/**
 * 机器人配置编辑
 */
Robot.prototype.editRobotEvent = function () {
    $("#btnNext1").click(function () {
        console.log("配置")

        var robot_id = $(this).attr("robot_id")
        console.log("robotid", robot_id)
        var mix_num = $('.edit-mix-num').val()
        var max_num = $('.edit-max-numx').val()
        var stoploss = $('.edit-stoploss').val()
        var waring = $('.edit-waring').val()
        var orders_frequency = $('.edit-orders-frequency').val()

        xfzajax.post({
            'url': '/deal/showconfig/',
            'data': {
                'robot_id': robot_id,
                'min_num': mix_num,
                'max_num': max_num,
                'stop_price': stoploss,
                'warning_price': waring,
                'orders_frequency': orders_frequency,
            },
            'success': function (result) {
                console.log(result)
                if (result['code'] === 200) {
                    xfzalert.alertSuccess("机器人配置成功", function () {
                        window.location.reload()
                    })
                }
            }
        })
    })
}
Robot.prototype.oneStepRun = function () {
    $('#one-key-stop').click(function () {
        var currentbtn = $(this);
        var tr = currentbtn.parent().parent();
        var robot_id = tr.attr('data-id');
        var run_status = $(this).attr('run_status')
        var status = tr.attr('status')

        if (run_status == 0 && status == 1) {
            run_status = 1
            status = 0
        } else if (run_status == 1 && status == 0) {
            run_status = 0
            status = 1
        }
        xfzajax.post({
            'url': '/deal/startrobot/',
            'data': {
                'robot_id': '',
                'flag': 0,

            },
            'success': function (result) {
                console.log(result)
            }

        })
    })
    $('#one-key-run').click(function () {
        xfzajax.post({
            'url': '/deal/startrobot/',
            'data': {
                'robot_id': '',
                'flag': 1,
            },
            'success': function (result) {
                console.log(result)
            }

        })
    })
}


/**
 * 图标填写
 */
Robot.prototype.listenRightFlagEvent = function () {
    $('#btnNext').click(function () {
        console.log("right")
        var currency = $('.strategy-curry .currency').text()
        if (!currency == "") {
            $('.strategy-curry').append("<img src=\"{% static 'images/1-1.png' %}\" alt=\"\">")
        }
    })
}

Robot.prototype.getUser = function () {
    $('#create-robot').click(function () {
        xfzajax.get({
            'url': '/deal/waring_usrs/',
            'success': function (result) {
                if (result['code'] === 200) {
                    console.log(result)
                    var users = result['data']
                    var tpl = template('users-item', {'users': users})
                    var usersGroup = $('#waring-users')
                    usersGroup.append(tpl)
                }
            }
        })
    })

}

Robot.prototype.listenCurrencySelecctedEvent = function () {
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
                var profit = self.fomatFloat(mix_profit, 2) + '%' + '-' + self.fomatFloat(max_price, 2) + '%'
                $('.resistance-value').val(resistance)

                $('.support-value').val(support_level)
                $('.profit-value').text(profit)

            }
        }

    })
}

/**
 * 机器人提交 数据校验提示方法
 * 包括止损价提示
 * 单网格不能超过交易币种，市场币种价格提示
 */
Robot.prototype.submitTipsEvent = function () {
    var self = this;
    //止损价提示
    $('.stopLoss .loss').on('blur', function () {
        var support = $('.strategy-parameters-top .support-level').text()
        var loss = $('.stopLoss .loss').val()
        console.log(support,loss)
        if (loss > support) {
            xfzalert.alertError("止损价必须低于支撑位")
        }
    });
    //单网格最大提示
    $('.max-number-value').on('blur', function () {
        var max_num = $('.max-number-value').val()
        var currency = $('.account-details .currency').text().replace(/[^\d.]/g, "")
        var market = $('.account-details .market').text().replace(/[^\d.]/g, "")
        console.log('currency:'+currency,'market:'+ market)
        var support = $('.support-value').val()
        var resistance = $('.resistance-value').val()
        console.log("支撑位"+support, "阻力位："+resistance)
        var num = $('#stratery-girding-num').val()
        // var current_matket = max_num *
        var average_price = (parseInt(resistance) + parseInt(support)) / 2
        var market_price = average_price * max_num * num  //账户市场
        console.log("市场价计算："+market_price)

        var currency_price = max_num * num
        console.log(currency_price,"交易币种价格")
        if (parseInt(market) < parseInt(market_price)) {
            xfzalert.alertError("账户市场币种余额不足")
        }
        if (parseInt(currency) < parseInt(currency_price)) {
            xfzalert.alertError("账户交易币种余额不足")
        }
        if (parseInt(market) < parseInt(market_price) && parseInt(currency) < parseInt(currency_price)) {
            xfzalert.alertError("账户市场币种和交易币种余额不足")
        }

    })

    $('.resistance-value').on('blur', function () {

        var resistance = $('.resistance-value').val()
        var price = $('.current-price .price').text()
        var support_level = $('.support-value').val()
        if (!resistance == '') {
            if (parseInt(resistance) <= parseInt(price)) {
                xfzalert.alertError("阻力位不得低于等于当前价")
                // $('.resistance-value').after("<span class='error-account'>阻力位不得低于等于当前价</span>")
            } else {
                var num = $('#stratery-girding-num ').val()
                var free = $('#one-girding-free').val() / 100
                var girding = (resistance - support_level) / num     //单网格=（阻力位价格-支撑位价格）/网格数量
                var mix_profit = (girding - (resistance * 2 + girding) * free) / resistance

                var max_price = (girding - (support_level * 2 + girding) * free) / support_level
                var profit = self.fomatFloat(mix_profit * 100, 2) + '%' + '-' + self.fomatFloat(max_price * 100, 2) + '%'
                $('.profit-value').text(profit)
            }
        }
    });

}


Robot.prototype.websocketRobot = function () {
    var self = this;
    var socket = new WebSocket("ws://"+window.location.host + "/deal/webtask_stu/");
    socket.onopen = function () {
        console.log('WebSocket open');//成功连接上Websocket
        socket.send('1');//发送数据到服务端
    };
    socket.onmessage = function (result) {
        // console.log('message: ' + e.data);//打印服务端返回的数据
        // console.log(typeof (e.data));
        console.log(result);
        console.log("dfa")

    };
    socket.onclose = function (e) {
        console.log(e);
        socket.close(); //关闭TCP连接
    };

}


Robot.prototype.robotYieldEvent = function(){
    var self = this
    xfzajax.post({
        'url': '/deal/robot_yield/',
        'success':function (result) {
            console.log(result)
        }

    })



}


template.defaults.imports.fomat= function (n) {
        return n.toFixed(2)
    }



// Robot.prototype.getRobotsId = function () {
//     xfzajax.get({
//         'url': '/deal/get_robotid/',
//         'success': function (result) {
//             console.log(result)
//         }
//     })
// }
$(function () {
    var robot = new Robot();
    robot.run();

});









