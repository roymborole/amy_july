const IASearchModule = {
    init: function(containerId, options = {}) {
        const container = document.getElementById(containerId);
        if (!container) return;
    
        const defaultHtml = `
            <form id="ia-search-form">
                <div class="input-group mb-3">
                    <input type="text" class="form-control" id="ia-search-input" name="ticker" placeholder="Enter company name" required>
                    <div class="input-group-append">
                        <button class="btn-analyze" type="submit">Analyze</button>
                    </div>
                </div>
                <div id="ia-autocomplete-results"></div>
            </form>
        `;
    
        container.innerHTML = options.customHtml || defaultHtml;
    
        this.setupEventListeners();
        if (!options.skipLottie) {
            this.setupLottieAnimation();
        }
        this.setupAutocomplete(options.searchInputId, options.resultsContainerId);
    },
    renderCharts: function(data, ticker) {
        console.log("Rendering charts for:", ticker, data);  // Debug log
    
        // Render Performance Chart
        this.renderPerformanceChart(data.performance);
        
        // Render Price History Chart
        this.renderPriceHistoryChart(data.price_history);
    
        // Remove raw data display
        document.getElementById('raw-performance-data').remove();
        document.getElementById('raw-price-history-data').remove();
    },
    
    renderPerformanceChart: function(performanceData) {
        const ctx = document.getElementById('performanceChart').getContext('2d');
        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: Object.keys(performanceData),
                datasets: [{
                    label: 'Stock Performance',
                    data: Object.values(performanceData).map(d => d.stock),
                    backgroundColor: 'rgba(75, 192, 75, 0.6)'  // Green
                }, {
                    label: 'S&P 500 Performance',
                    data: Object.values(performanceData).map(d => d.sp500),
                    backgroundColor: 'rgba(255, 159, 64, 0.6)'  // Orange
                }]
            },
            options: {
                responsive: true,
                title: {
                    display: true,
                    text: 'Performance Comparison'
                }
            }
        });
    },
    
    renderPriceHistoryChart: function(priceHistory) {
        const ctx = document.getElementById('priceHistoryChart').getContext('2d');
        new Chart(ctx, {
            type: 'line',
            data: {
                labels: priceHistory.dates,
                datasets: [{
                    label: 'Stock Price',
                    data: priceHistory.prices,
                    borderColor: 'rgb(75, 192, 192)',
                    tension: 0.1
                }]
            },
            options: {
                responsive: true,
                title: {
                    display: true,
                    text: 'Price History'
                }
            }
        });
    },
    setupAutocomplete: function(searchInputId = 'ia-search-input', resultsContainerId = 'ia-autocomplete-results') {
        const searchInput = document.getElementById(searchInputId);
        const resultsContainer = document.getElementById(resultsContainerId);
        if (!searchInput || !resultsContainer) {
            console.error('Search input or results container not found');
            return;
        }

        let debounceTimer;

        searchInput.addEventListener('input', () => {
            clearTimeout(debounceTimer);
            debounceTimer = setTimeout(() => {
                const prefix = searchInput.value.trim();
                if (prefix.length >= 2) {
                    this.fetchAutocompleteSuggestions(prefix, resultsContainer);
                } else {
                    resultsContainer.innerHTML = '';
                }
            }, 300);
        });

        resultsContainer.addEventListener('click', (event) => {
            const clickedElement = event.target.closest('li');
            if (clickedElement) {
                const suggestionText = clickedElement.textContent;
                searchInput.value = suggestionText.split('(')[0].trim();
                resultsContainer.innerHTML = '';
            }
        });

        document.addEventListener('click', (event) => {
            if (!resultsContainer.contains(event.target) && event.target !== searchInput) {
                resultsContainer.innerHTML = '';
            }
        });
    },

    fetchAutocompleteSuggestions: function(prefix, resultsContainer) {
        const companies = {
            "Apple Inc.": "AAPL",
            "Abbott Laboratories": "ABT",
            "Aflac Inc.": "AFL",
            "Akamai Technologies, Inc.": "AKAM",
            "Advanced Micro Devices, Inc.": "AMD",
            "Amgen Inc.": "AMGN",
            "Amazon.com, Inc.": "AMZN",
            "Aon plc": "AON",
            "Activision Blizzard, Inc.": "ATVI",
            "Booking Holdings Inc.": "BKNG",
            "BlackRock, Inc.": "BLK",
            "Boston Scientific Corporation": "BSX",
            "Caterpillar Inc.": "CAT",
            "Chubb Limited": "CB",
            "Cboe Global Markets, Inc.": "CBOE",
            "Carnival Corporation": "CCL",
            "Cadence Design Systems, Inc.": "CDNS",
            "Cigna Corporation": "CI",
            "Cummins Inc.": "CMI",
            "ConocoPhillips": "COP",
            "Costco Wholesale Corporation": "COST",
            "Campbell Soup Company": "CPB",
            "Cisco Systems, Inc.": "CSCO",
            "CVS Health Corporation": "CVS",
            "Lockheed Martin Corporation": "LMT",
            "Mastercard Incorporated": "MA",
            "Marriott International, Inc.": "MAR",
            "Mattel, Inc.": "MAT",
            "Microchip Technology Incorporated": "MCHP",
            "MGM Resorts International": "MGM",
            "Monster Beverage Corporation": "MNST",
            "Morgan Stanley": "MS",
            "Microsoft Corporation": "MSFT",
            "M&T Bank Corporation": "MTB",
            "Netflix, Inc.": "NFLX",
            "AT&T Inc.": "T"
        };

        const suggestions = Object.entries(companies)
            .filter(([name, ticker]) => name.toLowerCase().startsWith(prefix.toLowerCase()))
            .slice(0, 5);  // Limit to 5 suggestions

        this.displayAutocompleteSuggestions(suggestions, resultsContainer);
    },

    displayAutocompleteSuggestions: function(suggestions, resultsContainer) {
        resultsContainer.innerHTML = '';

        if (suggestions.length === 0) {
            resultsContainer.innerHTML = '<p>No matches found</p>';
            return;
        }

        const ul = document.createElement('ul');
        ul.className = 'autocomplete-list';

        suggestions.forEach(([name, ticker]) => {
            const li = document.createElement('li');
            li.innerHTML = `<strong>${name}</strong> (${ticker})`;
            ul.appendChild(li);
        });

        resultsContainer.appendChild(ul);
    },

    setupEventListeners: function() {
        const form = document.getElementById('ia-search-form');
        form.addEventListener('submit', this.handleSubmit.bind(this));
    },

    setupLottieAnimation: function() {
        const animationContainer = document.getElementById('ia-lottie-container');
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
        const searchInput = document.getElementById('ia-search-input');
        const companyName = searchInput.value.trim();
    
        if (!companyName) {
            alert('Please enter a company name');
            return;
        }
    
        const ticker = this.getTickerFromName(companyName);
        
        // Redirect to the loading page
        window.location.href = `/ias_loading/${encodeURIComponent(ticker)}`;
    },
    

        companies: {
            "Apple Inc.": "AAPL",
            "Abbott Laboratories": "ABT",
            "Aflac Inc.": "AFL",
            "Akamai Technologies, Inc.": "AKAM",
            "Advanced Micro Devices, Inc.": "AMD",
            "Amgen Inc.": "AMGN",
            "Amazon.com, Inc.": "AMZN",
            "Aon plc": "AON",
            "Activision Blizzard, Inc.": "ATVI",
            "Booking Holdings Inc.": "BKNG",
            "BlackRock, Inc.": "BLK",
            "Boston Scientific Corporation": "BSX",
            "Caterpillar Inc.": "CAT",
            "Chubb Limited": "CB",
            "Cboe Global Markets, Inc.": "CBOE",
            "Carnival Corporation": "CCL",
            "Cadence Design Systems, Inc.": "CDNS",
            "Cigna Corporation": "CI",
            "Cummins Inc.": "CMI",
            "ConocoPhillips": "COP",
            "Costco Wholesale Corporation": "COST",
            "Campbell Soup Company": "CPB",
            "Cisco Systems, Inc.": "CSCO",
            "CVS Health Corporation": "CVS",
            "Lockheed Martin Corporation": "LMT",
            "Mastercard Incorporated": "MA",
            "Marriott International, Inc.": "MAR",
            "Mattel, Inc.": "MAT",
            "Microchip Technology Incorporated": "MCHP",
            "MGM Resorts International": "MGM",
            "Monster Beverage Corporation": "MNST",
            "Morgan Stanley": "MS",
            "Microsoft Corporation": "MSFT",
            "M&T Bank Corporation": "MTB",
            "Netflix, Inc.": "NFLX",
            "AT&T Inc.": "T"
        },
    
        getTickerFromName: function(input) {
            // Check if input is already a ticker
            if (Object.values(this.companies).includes(input.toUpperCase())) {
                return input.toUpperCase();
            }
            
            // Check if input is a full company name
            for (let [name, ticker] of Object.entries(this.companies)) {
                if (name.toLowerCase() === input.toLowerCase()) {
                    return ticker;
                }
            }
            
            // If not found, return the input as is
            return input;
        },
    
        generateReport: function(ticker) {
            console.log(`Generating report for ${ticker}`);
        
            // Get the CSRF token from the meta tag
            const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');
        
            // Make AJAX call to generate macro analysis
            fetch('/generate_macro', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-CSRFToken': csrfToken  // Include the CSRF token in the headers
                },
                body: `ticker=${encodeURIComponent(ticker)}`
            })
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    alert(`Error: ${data.error}`);
                    window.location.href = '/';
                } else {
                    localStorage.setItem('reportData', JSON.stringify(data));
                    window.location.href = `/ias_report/${ticker}`;
                }
            })
            .catch(error => {
                alert(`An error occurred: ${error}`);
                window.location.href = '/';
            });
        },
        
        displayMacroeconomicAnalysis: function(ticker, data) {
            const resultElement = document.getElementById('ia-analysis-result');
            console.log("Displaying analysis for:", ticker, data);  // Debug log
            resultElement.innerHTML = `
                <div style="color: white;">
                    ${data.analysis}
                </div>
            `;
            
            this.renderCharts(data, ticker);
        },
    }
    window.IASearchModule = IASearchModule;