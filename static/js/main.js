           //숨기기 토글
            //숨기기 클릭 - 카드 컨테이너 위쪽으로 밀려 올라감 (밑면이 top0이 되게)
            $(".hideToggle a").click(function(){
                $(".cardContainer").animate({height:"0"},500);

            });

            //카드 띄우기
            $(".card").click(function(){
                $(".detailsBg").show();
                //this통해 검색, 받아와서 보여주기, 주소창에 정보 띄울 것!(주소로 카드 접근 가능하도록)
            })