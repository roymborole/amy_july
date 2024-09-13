const TASearchModule = {
    init: function(containerId, options = {}) {
        const container = document.getElementById(containerId);
        if (!container) {
            console.error(`Container with id ${containerId} not found`);
            return;
        }
    
        const defaultHtml = `
            <form id="ta-search-form">
                <div class="input-group mb-3">
                    <input type="text" class="form-control" id="ta-search-input" placeholder="Enter asset name or ticker" required>
                    <div class="input-group-append">
                        <button class="btn-analyze" type="submit">Analyze</button>
                    </div>
                </div>
                <div id="ta-autocomplete-results"></div>
            </form>
            <div id="loading" style="display:none;">
                <div id="lottie-container"></div>
                <p>Generating report... Please wait.</p>
            </div>
        `;
    
        container.innerHTML = options.customHtml || defaultHtml;
    
        this.setupEventListeners();
        if (!options.skipLottie) {
            this.setupLottieAnimation();
        }
        this.setupAutocomplete(options.searchInputId || 'search-input', options.resultsContainerId || 'ta-autocomplete-results');
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
    
        // Add this new event listener for handling clicks on suggestions
        resultsContainer.addEventListener('click', (event) => {
            const clickedElement = event.target.closest('li');
            if (clickedElement) {
                const suggestionText = clickedElement.textContent;
                searchInput.value = suggestionText.split('(')[0].trim(); // Set the input value to the name part
                resultsContainer.innerHTML = ''; // Clear suggestions
                // You might want to trigger a comparison here or update some UI
                // For example: this.compareAsset(searchInput.value);
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
        ul.className = 'ta-autocomplete-list';
    
        suggestions.forEach(suggestion => {
            const li = document.createElement('li');
            li.innerHTML = `<strong>${suggestion.name}</strong> (${suggestion.ticker})`;
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

    setupAutocomplete: function(searchInputId = 'search-input', resultsContainerId = 'ta-autocomplete-results') {
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
    
        // Add this new event listener for handling clicks on suggestions
        resultsContainer.addEventListener('click', (event) => {
            const clickedElement = event.target.closest('li');
            if (clickedElement) {
                const suggestionText = clickedElement.textContent;
                searchInput.value = suggestionText.split('(')[0].trim(); // Set the input value to the name part
                resultsContainer.innerHTML = ''; // Clear suggestions
            }
        });
    
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

// Expose the TASearchModule globally
window.TASearchModule = TASearchModule;