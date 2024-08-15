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
                <div id="autocomplete-results"></div>
            </form>
            <div id="loading" style="display:none;">
                <div id="lottie-container"></div>
                <p>Generating report... Please wait.</p>
            </div>
        `;

        this.setupEventListeners();
        this.setupLottieAnimation();
        this.setupAutocomplete();
    },
    
    setupComparisonAutocomplete: function(inputId, resultsId) {
        const searchInput = document.getElementById(inputId);
        const resultsContainer = document.getElementById(resultsId);
        if (!searchInput || !resultsContainer) {
            console.error('Comparison input or results container not found');
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
    
        // Hide autocomplete results when clicking outside
        document.addEventListener('click', (event) => {
            if (!resultsContainer.contains(event.target) && event.target !== searchInput) {
                resultsContainer.innerHTML = '';
            }
        });
    },
    
    fetchAutocompleteSuggestions: function(prefix, resultsContainer) {
        fetch(`/api/autocomplete?prefix=${encodeURIComponent(prefix)}`)
            .then(response => response.json())
            .then(data => this.displayAutocompleteSuggestions(data, resultsContainer))
            .catch(error => console.error('Error fetching autocomplete suggestions:', error));
    },
    
    displayAutocompleteSuggestions: function(suggestions, resultsContainer) {
        if (!resultsContainer) {
            console.error('Results container not found');
            return;
        }
    
        resultsContainer.innerHTML = '';
    
        if (suggestions.length === 0) {
            resultsContainer.innerHTML = '<p>No matches found</p>';
            return;
        }
    
        const ul = document.createElement('ul');
        ul.className = 'autocomplete-list';
    
        suggestions.forEach(suggestion => {
            const li = document.createElement('li');
            li.innerHTML = `<strong>${suggestion.name}</strong> (${suggestion.ticker})`;
            li.addEventListener('click', () => this.selectAutocompleteSuggestion(suggestion, resultsContainer.previousElementSibling));
            ul.appendChild(li);
        });
    
        resultsContainer.appendChild(ul);
    },
    
    selectAutocompleteSuggestion: function(suggestion, inputElement) {
        if (inputElement) {
            inputElement.value = suggestion.name;
            const resultsContainer = inputElement.nextElementSibling;
            if (resultsContainer) {
                resultsContainer.innerHTML = '';
            }
        }
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

    setupAutocomplete: function() {
        const searchInput = document.getElementById('search-input');
        const resultsContainer = document.getElementById('autocomplete-results');
        let debounceTimer;

        searchInput.addEventListener('input', () => {
            clearTimeout(debounceTimer);
            debounceTimer = setTimeout(() => {
                const prefix = searchInput.value.trim();
                if (prefix.length >= 2) {
                    this.fetchAutocompleteSuggestions(prefix);
                } else {
                    resultsContainer.innerHTML = '';
                }
            }, 300);
        });

        // Hide autocomplete results when clicking outside
        document.addEventListener('click', (event) => {
            if (!resultsContainer.contains(event.target) && event.target !== searchInput) {
                resultsContainer.innerHTML = '';
            }
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

