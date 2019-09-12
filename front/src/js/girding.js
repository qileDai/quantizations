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

};

Robot.prototype.initYstepEvent = function () {
    //根据jQuery选择器找到需要加载ystep的容器
//loadStep 方法可以初始化ystep

    $(".ystep").setStep(1);

};
Robot.prototype.loadstepEvent =function(){
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

Robot.prototype.listenClickRobotEvent = function () {

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
        if (creatrobotclick==0){
             self.robotWrapper.show();
              robotDataArray[num].show()
             creatrobotclick++
        }else{
            console.log(creatrobotclick)
             self.robotWrapper.show()
        }

        console.log('open1')

        // console.log("daiqe")
        // self.initYstepEvent();

        // var li = document.querySelectorAll('li')
        // var lilength = li.length;
        // console.log(lilength)
        $("#btnPre").unbind();
        btnPre.click(function () {
             console.log('num')
            if (num<=0){
               num=0;
               // li[num].show().sibling().hide();
            }else {
                num--;
                 $('#btnNext').text('下一步')
               // li[num].show().sibling().hide();

            }
            //跳转到上一个步骤
            $(".ystep").prevStep();
            // var stepNum = $(".ystep").getStep();
            // console.log(stepNum)
            // robotDataArray[stepNum-1]
           // $.each(robotDataArray,function (key,value) {
           //     console.log('val',value)
           //      if(num=== key){
           //          value.show()
           //      }else {
           //          value.hide()
           //      }
           //  })
             console.log('val',robotDataArray)
            for (var i=0;i<robotDataArray.length;i++){

                if(num=== i){
                    robotDataArray[i].show()
                }else {
                    robotDataArray[i].hide()
                }
            }


        });
        $("#btnNext").unbind();
        btnNext.click(function () {
            console.log('next')
            if (num>=2){
                $('#btnNext').text('完成')
                num=3;


            }else{
                num++;
                $('#btnNext').text('下一步')
            }
            //跳转到下一个步骤
            $(".ystep").nextStep();
            // var stepNum = $(".ystep").getStep();
            // robotDataArray[stepNum+1].show()
            // console.log(stepNum)
            $.each(robotDataArray,function (key,value) {
                if(num=== key){
                    value.show()
                }else {
                    value.hide()
                }
            })

        });
        $('.warninguser label').on('click', function () {
           $(this).toggleClass('btn-success')
        })

    })


}


Robot.prototype.listenCloseRobotEvent = function(){
    var closeBtn = $('.close-btn');
    var robotWrapper = $('.robot-wrapper');
    closeBtn.click(function () {
        robotWrapper.hide();



    })
};
Robot.prototype.listenCreatTradingEvent = function(){
    $('.update-property').on('click', function () {
        $('.tradingParticulars').show();
        $('.tradingShade').show();
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
Robot.prototype.listenparameterEven = function(){
    var parameterconfiguration = $('.parameter-configuration');
    var parameterclosebtn = $('.parameter-close-btn');
    var deleteproperty = $('.delete-property');
    var tradingShade = $('.tradingShade')
    deleteproperty.click(function () {
        parameterconfiguration.show();
        tradingShade.show();

    })
    parameterclosebtn.click(function () {
        parameterconfiguration.hide();
        tradingShade.hide();
    })
}



$(function () {
    var robot = new Robot();
    robot.run();

});









