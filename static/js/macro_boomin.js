document.addEventListener('DOMContentLoaded', function() {
    const analysisForm = document.getElementById('analysis-form');
    const companyList = document.getElementById('company-list');
    const loadingModal = document.getElementById('loadingModal');
    const analysisResult = document.getElementById('analysis-result');

    analysisForm.addEventListener('submit', function(e) {
        e.preventDefault();
        const ticker = document.getElementById('ticker-input').value;
        generateAnalysis(ticker);
    });

    companyList.addEventListener('click', function(e) {
        if (e.target.classList.contains('company-link')) {
            e.preventDefault();
            const ticker = e.target.getAttribute('data-ticker');
            generateAnalysis(ticker);
        }
    });

    function generateAnalysis(ticker) {
        // Show the loading modal
        loadingModal.style.display = 'block';

        // Clear previous results and charts
        analysisResult.innerHTML = '';
        document.getElementById('price-chart').innerHTML = '';
        document.getElementById('volume-chart').innerHTML = '';

        fetch(`/generate_macro_analysis/${ticker}`)
            .then(response => response.json())
            .then(data => {
                // Hide the loading modal
                loadingModal.style.display = 'none';

                if (data.error) {
                    throw new Error(data.error);
                }

                // Format and display the analysis result
                const formattedAnalysis = formatAnalysis(data.analysis, ticker);
                analysisResult.innerHTML = formattedAnalysis;

                // Create charts if historical data is available
                if (data.historical_data && Array.isArray(data.historical_data) && data.historical_data.length > 0) {
                    createPriceChart(data.historical_data, ticker);
                    createVolumeChart(data.historical_data, ticker);
                } else {
                    console.warn('Historical data not available for charts');
                    document.getElementById('price-chart').innerHTML = '<p>Price chart data not available</p>';
                    document.getElementById('volume-chart').innerHTML = '<p>Volume chart data not available</p>';
                }
            })
            .catch(error => {
                // Hide the loading modal
                loadingModal.style.display = 'none';

                // Display error message
                analysisResult.innerHTML = `<p class="error">An error occurred: ${error.message}</p>`;
                console.error('Error:', error);
            });
    }

    function formatAnalysis(analysis, ticker) {
        if (typeof analysis !== 'string') {
            return `<p class="error">Invalid analysis data received for ${ticker}</p>`;
        }

        // Remove the initial JSON-like structure and extra newlines
        let cleanedAnalysis = analysis.replace(/^{"analysis":"/, '').replace(/\\n/g, '');
        
        // Remove trailing quote and curly brace if present
        cleanedAnalysis = cleanedAnalysis.replace(/"}$/, '');

        // Replace the first line with the correct heading
        const lines = cleanedAnalysis.split('\n');
        lines[0] = `<h1 class="text-center pink-heading">Comprehensive Macroeconomic Analysis for ${ticker}</h1>`;

        // Join the lines back together
        return lines.join('\n');
    }

    function createPriceChart(data, ticker) {
        if (!Array.isArray(data) || data.length === 0) {
            console.warn('Invalid data for price chart');
            return;
        }

        const dates = data.map(d => d.Date).filter(d => d != null);
        const prices = data.map(d => d.Close).filter(p => p != null);

        if (dates.length === 0 || prices.length === 0) {
            console.warn('No valid data points for price chart');
            document.getElementById('price-chart').innerHTML = '<p>Price chart data not available</p>';
            return;
        }

        const trace = {
            x: dates,
            y: prices,
            type: 'scatter',
            mode: 'lines',
            name: 'Close Price'
        };

        const layout = {
            title: `${ticker} Price Chart`,
            xaxis: { title: 'Date' },
            yaxis: { title: 'Price' }
        };

        Plotly.newPlot('price-chart', [trace], layout);
    }

    function createVolumeChart(data, ticker) {
        if (!Array.isArray(data) || data.length === 0) {
            console.warn('Invalid data for volume chart');
            return;
        }

        const dates = data.map(d => d.Date).filter(d => d != null);
        const volumes = data.map(d => d.Volume).filter(v => v != null);

        if (dates.length === 0 || volumes.length === 0) {
            console.warn('No valid data points for volume chart');
            document.getElementById('volume-chart').innerHTML = '<p>Volume chart data not available</p>';
            return;
        }

        const trace = {
            x: dates,
            y: volumes,
            type: 'bar',
            name: 'Volume'
        };

        const layout = {
            title: `${ticker} Volume Chart`,
            xaxis: { title: 'Date' },
            yaxis: { title: 'Volume' }
        };

        Plotly.newPlot('volume-chart', [trace], layout);
    }
});