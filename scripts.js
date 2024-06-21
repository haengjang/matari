$(document).ready(function () {
    // 스크롤 애니메이션
    $('.btn-scroll').on('click', function (e) {
        e.preventDefault();
        var target = $(this).data('target');
        if (target && $(target).length) {
            $('html, body').animate({
                scrollTop: $(target).offset().top
            }, 1000);
        }
    });

    // 헤더 내비게이션 스크롤 애니메이션
    $('header nav a').on('click', function (e) {
        e.preventDefault();
        var target = $(this).attr('href');
        if (target && $(target).length) {
            $('html, body').animate({
                scrollTop: $(target).offset().top
            }, 1000);
        }
    });

    // 링크 클릭 시 팝업 또는 새 창으로 이동
    $('.link-popup').on('click', function (e) {
        e.preventDefault();
        var newWindow = window.open("", "popup", "width=600,height=400");
        newWindow.document.write("<p>팝업 또는 새창으로 이동이 가능합니다. 해당 팝업은 샘플입니다.</p>");
        newWindow.document.close();
    });

    // 단가표 계산기
    var priceData = {
        basic: [100000, 200000, 300000, 400000],
        designWork: [50000, 100000, 150000, 200000],
        layoutChange: [100000, 200000, 300000, 400000],
        functionAdd: [200000, 300000, 400000, 500000]
    };

    function calculateTotal() {
        var quantity = parseInt($('#quantity').val());
        var basicPrice = priceData.basic[quantity - 1] || 0;
        var designWork = $('#designWork').is(':checked') ? priceData.designWork[quantity - 1] : 0;
        var layoutChange = $('#layoutChange').is(':checked') ? priceData.layoutChange[quantity - 1] : 0;
        var functionAdd = $('#functionAdd').is(':checked') ? priceData.functionAdd[quantity - 1] : 0;

        var totalPrice = basicPrice + designWork + layoutChange + functionAdd;
        $('#totalPrice').val(totalPrice.toLocaleString() + '원');
    }

    $('#decreaseQuantity').on('click', function () {
        var quantity = parseInt($('#quantity').val());
        if (quantity > 1) {
            $('#quantity').val(quantity - 1);
            calculateTotal();
        }
    });

    $('#increaseQuantity').on('click', function () {
        var quantity = parseInt($('#quantity').val());
        if (quantity < 4) {
            $('#quantity').val(quantity + 1);
            calculateTotal();
        }
    });

    $('#designWork, #layoutChange, #functionAdd').on('change', calculateTotal);
    calculateTotal();  // 초기 계산
});
