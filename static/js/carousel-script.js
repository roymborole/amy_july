(function() {
    // Create and append styles
    const style = document.createElement('style');
    style.textContent = `
        .logo-carousel {
            position: relative;
            width: 100%;
            max-width: 1000px;
            margin: 0 auto;
            overflow: hidden;
        }
        .carousel-container {
            width: 100%;
            overflow: hidden;
        }
        .carousel-track {
            display: flex;
            animation: scroll 20s linear infinite;
        }
        .carousel-slide {
            flex: 0 0 20%;
            min-width: 20%;
            padding: 20px;
            box-sizing: border-box;
            display: flex;
            justify-content: center;
            align-items: center;
        }
        .carousel-slide img, .carousel-icon {
            width: 80px;
            height: auto;
            cursor: pointer;
        }
        @keyframes scroll {
            0% { transform: translateX(0); }
            100% { transform: translateX(-200%); }
        }
        .logo-carousel:hover .carousel-track {
            animation-play-state: paused;
        }
    `;
    document.head.appendChild(style);

    // Company tickers mapping
    const companyTickers = {
        'Co_logo_1': 'TSM', 'Co_logo_2': 'GOOGL', 'Co_logo_3': 'AMD',
        'Co_logo_4': 'INTC', 'Co_logo_5': 'AVGO', 'Co_logo_6': 'RIVN',
        'Co_logo_7': 'AAL', 'Co_logo_8': 'WMT', 'Co_logo_9': 'PFE',
        'Co_logo_10': 'MCD', 'Co_logo_11': 'CMG', 'Co_logo_12': 'AAPL',
        'Co_logo_13': 'SPOT', 'Co_logo_14': 'DIS', 'Co_logo_15': 'AMZN',
        'Co_logo_16': 'MSFT', 'Co_logo_17': 'TSLA', 'Co_logo_18': 'NVDA',
        'Co_logo_19': 'NFLX', 'Co_logo_20': 'META'
    };

    function createCarousel(elementId) {
        const container = document.getElementById(elementId);
        if (!container) return;

        const carouselHTML = `
            <div class="logo-carousel">
                <div class="carousel-container">
                    <div class="carousel-track"></div>
                </div>
            </div>
        `;
        container.innerHTML = carouselHTML;

        const track = container.querySelector('.carousel-track');
        const totalSlides = 20;

        for (let i = 1; i <= totalSlides; i++) {
            const slide = document.createElement('div');
            slide.classList.add('carousel-slide');
            const img = document.createElement('img');
            img.src = `/static/Co_logo_${i}.png`;
            img.alt = `Company Logo ${i}`;
            img.classList.add('carousel-icon');
            
            const logoKey = `Co_logo_${i}`;
            const ticker = companyTickers[logoKey] || 'UNKNOWN';
            
            img.addEventListener('click', () => {
                generateReport(ticker, i);
            });
            
            slide.appendChild(img);
            track.appendChild(slide);
        }

        // Clone slides for infinite loop
        const slides = track.querySelectorAll('.carousel-slide');
        slides.forEach(slide => {
            const clone = slide.cloneNode(true);
            track.appendChild(clone);
        });

        // Adjust the animation duration based on the number of slides
        const animationDuration = totalSlides * 1.5; // 1.5 seconds per slide
        track.style.animation = `scroll ${animationDuration}s linear infinite`;
    }

    function generateReport(ticker, logoNumber) {
        console.log(`Generating report for ${ticker} (Logo ${logoNumber})`);
        // Show a loading indicator
        document.body.classList.add('loading');
        // Redirect to the loading page instead of the report page
        window.location.href = `/loading/${ticker}`;
    }

    // Expose the createCarousel function globally
    window.createCarousel = createCarousel;
})();