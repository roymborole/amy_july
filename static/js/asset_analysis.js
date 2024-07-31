
function compareAsset(assetName) {
    var asset2 = prompt("Enter the name or ticker of the asset you want to compare with " + assetName + ":");
    if (asset2) {
        showLoadingAnimation();
        window.location.href = '/compare/' + encodeURIComponent(assetName) + '/' + encodeURIComponent(asset2);
    }
}

function showPrediction(assetName) {
    const loadingModal = document.getElementById('loading-modal');
    if (!loadingModal) {
        console.error('Loading modal not found');
        return;
    }
    
    loadingModal.style.display = 'block';
    
    // Fetch prediction data
    fetch('/generate_price_prediction/' + encodeURIComponent(assetName))
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            loadingModal.style.display = 'none';
            
            if (data.error) {
                throw new Error(data.error);
            }
            
            // Redirect to prediction page
            window.location.href = '/prediction/' + encodeURIComponent(assetName);
        })
        .catch(error => {
            loadingModal.style.display = 'none';
            console.error('Error:', error);
            alert("Error fetching prediction data: " + error.message);
        });
}

function displayPredictionData(data) {
    const predictionHtml = `
        <h2>Price Prediction Results</h2>
        <p><strong>Symbol:</strong> ${data.symbol}</p>
        <p><strong>Current Price:</strong> $${data.current_price.toFixed(2)}</p>
        <p><strong>Predicted Price:</strong> $${data.predicted_price.toFixed(2)}</p>
        <p><strong>Prediction Date:</strong> ${data.prediction_date}</p>
        <p><strong>95% Confidence Interval:</strong> $${data.confidence_interval.lower.toFixed(2)} - $${data.confidence_interval.upper.toFixed(2)}</p>
        <p><strong>Date Range:</strong> ${data.display_date_range}</p>
    `;
    const predictionContainer = document.getElementById('prediction-container');
    if (predictionContainer) {
        predictionContainer.innerHTML = predictionHtml;
    } else {
        console.error('Prediction container element not found');
    }
}


function showNewsSummary(assetName) {
    console.log("showNewsSummary called for", assetName);
    window.location.href = '/loading_news/' + encodeURIComponent(assetName);
    // Show loading animation
    fetch('/loading_news/' + encodeURIComponent(assetName))
        .then(response => response.text())
        .then(html => {
            document.body.innerHTML = html;
            // Reinitialize Lottie animation
            var animationContainer = document.getElementById('lottie-animation');
            if (animationContainer) {
                lottie.loadAnimation({
                    container: animationContainer,
                    renderer: 'svg',
                    loop: true,
                    autoplay: true,
                    path: "/static/lottie/news_loading.json"
                });
            }
        });
    
    // Fetch actual news data
    fetch('/news/' + encodeURIComponent(assetName))
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.text();
        })
        .then(html => {
            document.body.innerHTML = html;
            console.log("News data inserted");
        })
        .catch(error => {
            console.error('Error:', error);
            alert("Error fetching news summary: " + error.message);
        });
}

function showLoadingAnimation() {
    const loadingModal = document.getElementById('loading-modal');
    if (loadingModal) {
        loadingModal.style.display = 'block';
    } else {
        console.error('Loading modal not found');
    }
}

function hideLoadingAnimation() {
    const loadingModal = document.getElementById('loading-modal');
    if (loadingModal) {
        loadingModal.style.display = 'none';
    } else {
        console.error('Loading modal not found');
    }
}


function emailReport(assetName) {
    var email = prompt("Enter your email to receive this report for " + assetName + ":");
    if (email) {
        fetch('/send_report', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                email: email,
                asset_name: assetName,
                report_content: document.querySelector('.report-content').innerHTML
            }),
        })
        .then(response => response.json())
        .then(data => {
            alert(data.message);
        })
        .catch((error) => {
            console.error('Error:', error);
            alert('Failed to send email. Please try again.');
        });
    }
}

function subscribeToReports(assetName) {
    var email = prompt("Enter your email to subscribe to weekly reports for " + assetName + ":");
    if (email) {
        fetch('/api/subscribe', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                email: email,
                asset_name: assetName
            }),
        })
        .then(response => response.json())
        .then(data => {
            alert(data.message);
        })
        .catch((error) => {
            console.error('Error:', error);
            alert('Failed to subscribe. Please try again.');
        });
    }
}