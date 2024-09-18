let currentSlide = 0; // 현재 슬라이드 인덱스
const slides = document.querySelector('.slides');
const totalSlides = slides.children.length;
const slideWidth = 100 / totalSlides; // 각 슬라이드의 너비 계산

// 3초마다 슬라이드 이동
setInterval(() => {
    currentSlide++;
    if (currentSlide >= totalSlides) {
        currentSlide = 0; // 마지막 슬라이드가 지나면 다시 첫 슬라이드로 돌아감
    }
    // 슬라이드 이동 (우측에서 좌측으로)
    slides.style.transform = `translateX(-${currentSlide * slideWidth}%)`;
}, 3000); // 각 슬라이드마다 3초 대기
