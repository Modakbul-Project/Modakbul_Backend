                   //마우스 가로 스크롤 이벤트
                $(function() {

                    $(".cards").mousewheel(function(event, delta) {

                        this.scrollLeft -= (delta * 30);

                        event.preventDefault();

                    });

                });
               //스크롤 버튼
                    $(".scrollBt-right").click(function(){ $(this).siblings(".cards").animate({scrollLeft:"+=500"},800);
                });
                $(".scrollBt-left").click(function(){
                    $(this).siblings(".cards").animate({scrollLeft:"-=500"},800);
                });
