const SearchModule = {
    init: function(containerId) {
        const container = document.getElementById(containerId);
        if (!container) return;

        container.innerHTML = `
            <form id="search-form">
                <div class="input-group mb-3">
                    <input type="text" class="form-control" id="search-input" placeholder="Enter asset name or ticker" required>
                    <div class="input-group-append">
                         <button class="btn-analyze" type="submit">Analyze</button>
                    </div>
                </div>
            </form>
            <div id="loading" style="display:none;">
                <div id="lottie-container"></div>
                <p>Generating report... Please wait.</p>
            </div>
        `;

        this.setupEventListeners();
        this.setupLottieAnimation();
    },

    setupEventListeners: function() {
        const form = document.getElementById('search-form');
        form.addEventListener('submit', this.handleSubmit.bind(this));
    },

    setupLottieAnimation: function() {
        const animationContainer = document.getElementById('lottie-container');
        lottie.loadAnimation({
            container: animationContainer,
            renderer: 'svg',
            loop: true,
            autoplay: true,
            path: '/static/loading_animation.json'
        });
    },

    handleSubmit: function(event) {
        event.preventDefault();
        const searchInput = document.getElementById('search-input');
        const name_or_ticker = searchInput.value.trim();

        if (!name_or_ticker) {
            alert('Please enter an asset name or ticker');
            return;
        }

        this.generateReport(name_or_ticker);
    },

    generateReport: function(name_or_ticker) {
        console.log(`Generating report for ${name_or_ticker}`);
        // Show a loading indicator
        document.body.classList.add('loading');
        // Redirect to the loading page
        window.location.href = `/loading/${encodeURIComponent(name_or_ticker)}`;
    }
};

// Expose the SearchModule globally
window.SearchModule = SearchModule;