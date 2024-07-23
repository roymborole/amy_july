import yfinance as yf
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.pyplot import figure
import pandas as pd
import io
import base64
import sys
from datetime import datetime, timedelta
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
from crypto_analysis import get_crypto_data, crypto_mapping

def next_business_day(date):
    one_day = timedelta(days=1)
    next_day = date + one_day
    return next_day  # For crypto, we don't skip weekends

def prepare_data(data, seq_length):
    X, y = [], []
    for i in range(len(data) - seq_length):
        X.append(data[i:(i + seq_length)])
        y.append(data[i + seq_length])
    return np.array(X), np.array(y)

def create_and_train_model(X_train, y_train):
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train.ravel())
    return model

def predict_with_confidence(model, X):
    predictions = []
    for _ in range(100):  # Bootstrap sampling
        indices = np.random.randint(0, len(X), len(X))
        sample_pred = model.predict(X[indices])
        predictions.append(sample_pred)
    
    mean_pred = np.mean(predictions, axis=0)
    ci_lower = np.percentile(predictions, 2.5, axis=0)
    ci_upper = np.percentile(predictions, 97.5, axis=0)
    
    return mean_pred, ci_lower, ci_upper

def create_config(crypto_symbol):
    return {
        "crypto": {"symbol": crypto_symbol, "period": "5y"},
        "data": {"window_size": 20, "train_split_size": 0.80},
        "plots": {
            "xticks_interval": 90,
            "color_actual": "#001f3f",
            "color_train": "#3D9970",
            "color_val": "#0074D9",
            "color_pred_train": "#3D9970",
            "color_pred_val": "#0074D9",
            "color_pred_test": "#FF4136",
        },
        "model": {
            "input_size": 1,
            "num_trees": 100,
        },
        "training": {
            "batch_size": 64,
            "num_epoch": 100,
        }
    }

def run_crypto_prediction(crypto_name):
    print(f"Running prediction for cryptocurrency: {crypto_name}")
    if not crypto_name or crypto_name.lower() == 'null':
        print("Invalid input")
        return None
    
    try:
        symbol = crypto_mapping.get(crypto_name.lower(), crypto_name.upper())
        print(f"Resolved symbol: {symbol}")
        if not symbol:
            return None
        
        config = create_config(symbol)
        
        # Fetch crypto data
        crypto_data = get_crypto_data(crypto_name)
        if crypto_data is None or 'historical_data' not in crypto_data:
            print(f"Failed to fetch data for {crypto_name}")
            return None

        df = crypto_data['historical_data']
        data = df['Close'].values.reshape(-1, 1)

        # Normalize the data
        scaler = MinMaxScaler(feature_range=(0, 1))
        scaled_data = scaler.fit_transform(data)

        # Prepare training data
        seq_length = 60
        X, y = prepare_data(scaled_data, seq_length)
        
        # Split data into train and test
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        # Train the model
        model = create_and_train_model(X_train, y_train)
        print("Model training completed")

        # Make prediction
        mean_prediction, ci_lower, ci_upper = predict_with_confidence(model, X_test[-1].reshape(1, -1))
        
        predicted_price = scaler.inverse_transform(mean_prediction.reshape(-1, 1)).flatten()
        ci_lower = scaler.inverse_transform(ci_lower.reshape(-1, 1)).flatten()
        ci_upper = scaler.inverse_transform(ci_upper.reshape(-1, 1)).flatten()

        # Prepare result
        current_price = df['Close'].iloc[-1]
        prediction_date = pd.Timestamp.now() + pd.Timedelta(days=1)
        
        result = {
            "symbol": symbol,
            "current_price": float(current_price),
            "predicted_price": float(predicted_price[0]),
            "ci_lower": float(ci_lower[0]),
            "ci_upper": float(ci_upper[0]),
            "prediction_date": prediction_date.strftime('%Y-%m-%d'),
            "display_date_range": f"from {df.index[0].strftime('%Y-%m-%d')} to {df.index[-1].strftime('%Y-%m-%d')}",
        }
        
        print("Prediction result:", result)
        return result
    except Exception as e:
        print(f"Error during prediction for {crypto_name}: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

def generate_crypto_plot(data_date, data_close_price, config, plot_type='full', predicted_price=None, ci_lower=None, ci_upper=None):
    plt.figure(figsize=(25, 5), dpi=80)
    if plot_type == 'full':
        plt.plot(data_date, data_close_price, color=config["plots"]["color_actual"])
        plt.title(f"Daily close price for {config['crypto']['symbol']}")
    elif plot_type == 'prediction':
        plt.plot(data_date[-30:], data_close_price[-30:], label="Actual prices", color=config["plots"]["color_actual"])
        plt.plot(data_date[-1] + pd.Timedelta(days=1), predicted_price, 'ro', label="Predicted price")
        plt.vlines(data_date[-1] + pd.Timedelta(days=1), ci_lower, ci_upper, color='r', linestyles='dashed', label="95% CI")
        plt.title(f"Predicted close price for {config['crypto']['symbol']}")
        plt.legend()
    
    plt.grid(visible=True, which='major', axis='y', linestyle='--')
    
    img_buf = io.BytesIO()
    plt.savefig(img_buf, format='png')
    img_buf.seek(0)
    img_base64 = base64.b64encode(img_buf.getvalue()).decode('utf-8')
    plt.close()
    
    return img_base64

if __name__ == "__main__":
    crypto_name = input("Enter a cryptocurrency name: ") if len(sys.argv) <= 1 else sys.argv[1]
    result = run_crypto_prediction(crypto_name)
    if result:
        print(f"Prediction for {result['symbol']}:")
        print(f"Current price: ${result['current_price']:.2f}")
        print(f"Predicted price for {result['prediction_date']}: ${result['predicted_price']:.2f}")
        print(f"Data range: {result['display_date_range']}")