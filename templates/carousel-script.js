(function() {
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
            animation: scroll 40s linear infinite;
        }
        .carousel-slide {
            flex: 0 0 20%;
            min-width: 20%;
            padding: 10px;
            box-sizing: border-box;
        }
        .carousel-slide img {
            width: 100%;
            height: auto;
            cursor: pointer;
        }
        @keyframes scroll {
            0% { transform: translateX(0); }
            100% { transform: translateX(-100%); }
        }
        .logo-carousel:hover .carousel-track {
            animation-play-state: paused;
        }
    `;
    document.head.appendChild(style);

    const companyTickers = {
        'Co_logo_1': 'AAPL', 'Co_logo_2': 'GOOGL', 'Co_logo_3': 'MSFT',
        'Co_logo_4': 'AMZN', 'Co_logo_5': 'FB', 'Co_logo_6': 'TSLA',
        'Co_logo_7': 'NVDA', 'Co_logo_8': 'JPM', 'Co_logo_9': 'JNJ',
        'Co_logo_10': 'V', 'Co_logo_11': 'PG', 'Co_logo_12': 'DIS',
        'Co_logo_13': 'MA', 'Co_logo_14': 'HD', 'Co_logo_15': 'BAC',
        'Co_logo_16': 'ADBE', 'Co_logo_17': 'NFLX', 'Co_logo_18': 'CRM',
        'Co_logo_19': 'CSCO', 'Co_logo_20': 'INTC'
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
    }

    function generateReport(ticker, logoNumber) {
        console.log(`Generating report for ${ticker} (Logo ${logoNumber})`);
        // Show a loading indicator
        document.body.classList.add('loading');
        // Redirect to the report page
        window.location.href = `/report/${ticker}`;
    }

    // Expose the createCarousel function globally
    window.createCarousel = createCarousel;
})();