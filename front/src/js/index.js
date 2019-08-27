/**
 * Created by Administrator on 2018/8/16.
 */

function Banner() {
    this.bannerGroup = $("#banner-group");
    this.index = 1;

    this.leftArrow = $(".left-arrow");
    this.rightArrow = $(".right-arrow");
    this.bannerUl = $("#banner-ul");
    this.liList = this.bannerUl.children("li");
    this.bannerLiCount = this.liList.length;
    this.bannerWidth = 798;
    this.pagControl = $(".page-control");


}
Banner.prototype.lsitenBannerHover = function () {
    var self = this;
    this.bannerGroup.hover(function () {
        clearInterval(self.timer);
        self.toggleArrow(true);
    }, function () {
        self.loop();
        self.toggleArrow(false);
    });
};

Banner.prototype.toggleArrow = function (isShow) {
    var self = this;
    if (isShow) {
        self.leftArrow.show();
        self.rightArrow.show();
    } else {
        self.leftArrow.hide();
        self.rightArrow.hide();
    }


};
Banner.prototype.loop = function () {
    var self = this;
    var bannerul = $("#banner-ul");
    // bannerul.css(("left":-798));
    this.timer = setInterval(function () {
        if (self.index >= self.bannerLiCount + 1) {
            self.bannerUl.css({"left": -self.bannerWidth});
            self.index = 2;
        } else {
            self.index++;
        }

        self.anamite();
    }, 2000)
};
Banner.prototype.run = function () {
    var self = this;
    this.initBanneer();
    // console.log("runining ...");
    self.loop();
    this.listArrowClick();
    this.initPageControl();
    this.lsitenBannerHover();
    this.lsitPageControl();
};
Banner.prototype.anamite = function () {
    var self = this;
    var index = self.index;
    if (index === 0) {
        index = self.bannerLiCount - 1;
    } else if (index === self.bannerLiCount + 1) {
        index = 0;

    } else {
        index = self.index - 1
    }
    var bannerul = $("#banner-ul");
    bannerul.stop().animate({"left": -798 * self.index}, 500);
    self.pagControl.children("li").eq(index).addClass("active").siblings().removeClass("active");

}
Banner.prototype.lsitPageControl = function () {
    var self = this;
    var bannerul = $("#banner-ul");
    self.pagControl.children("li").each(function (index, obj) {
        $(obj).click(function () {
            self.index = index + 1;
            // bannerul.animate({"left":-798*self.index},500);
            self.anamite();
        });
    })
};

Banner.prototype.initPageControl = function
    () {
    var self = this;

    for (var i = 0; i < self.bannerLiCount; i++) {
        var circle = $("<li></li>")
        self.pagControl.append(circle);
        if (i === 0) {
            circle.addClass("active");
        }
    }
    self.pagControl.css({"width": self.bannerLiCount * 12 + 8 * 2 + 16 * (self.bannerLiCount - 1)});

};
Banner.prototype.initBanneer = function () {
    var self = this;

    var firstBanner = self.liList.eq(0).clone();
    var lastBanner = self.liList.eq(self.bannerLiCount - 1).clone();
    self.bannerUl.append(firstBanner);
    self.bannerUl.append(lastBanner);
    self.bannerUl.css({
        "width": self.bannerWidth * (self.bannerLiCount + 2),
        "left": -self.bannerWidth
    });


};
Banner.prototype.listArrowClick = function () {
    var self = this;
    var bannerul = $("#banner-ul");
    self.leftArrow.click(function () {
        if (self.index === 0) {
            self.bannerUl.css({"left": self.bannerWidth * self.bannerLiCount});
            self.index = self.bannerLiCount - 1;
        } else {
            self.index--;
        }
        self.anamite();
    });
    self.rightArrow.click(function () {
        if (self.index === self.bannerLiCount + 1) {
            self.bannerUl.css({"left": self.bannerWidth});
            self.index = 2;
        } else {
            self.index++;
        }
        self.anamite();
    });
};

function Index() {
    var self = this;
    self.category_id = 0;
    self.page = 2;


};

Index.prototype.listLoadMoreEvent = function () {
    var self = this
    self.categroy_id = 0;
    var loadbtn = $('#load-more');
    loadbtn.click(function () {

        xfzajax.get({
            'url': '/news/news_list/',
            'data': {
                'p': self.page,
                'categroy_id':self.categroy_id,
            },
            'success': function (result) {
                if (result['code'] === 200) {
                    var newes = result['data'];
                    console.log(newes)
                    if (newes.length > 0) {
                        var tpl = template("news-item", {'newses': newes});
                        var ul = $('.list-inner-group');
                        ul.append(tpl)
                        self.page += 1;
                    } else {
                        loadbtn.hide();
                    }
                }
            }
        });
    });
};
Index.prototype.listCategrySwichEvent = function () {
    var self = this;
    var tableGroup = $('.list-tab');
    tableGroup.children().click(function () {
        var li = $(this);
        var categroy_id = li.attr('data-categroy');
        console.log(categroy_id)
        var page = 1;

        xfzajax.get({
            'url':'/news/news_list/',
            'data':{
                'categroy_id':categroy_id,
                'p':page,
            },
            'success':function (result) {
                if(result['code'] ===200){
                    var newes = result['data'];
                    var tpl = template("news-item", {'newses': newes});
                    var newsListGroup = $(".list-inner-group");
                    newsListGroup.empty();
                    newsListGroup.append(tpl);
                    self.page = 2;
                    self.categroy_id = categroy_id;
                    li.addClass('active').siblings().removeClass('active');
                    var loadbtn = $('#load-more');
                    loadbtn.show();
                    // var loadbtn = $('#load-more');
                    // loadbtn.show();
                }
            }
        });
    });
};

Index.prototype.run = function () {
    var self = this;
    self.listLoadMoreEvent();
    self.listCategrySwichEvent();
};

$(function () {
    var banner = new Banner();
    banner.run();

    var index = new Index();
    index.run();

});