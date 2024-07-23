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
from ticker_utils import get_ticker_from_name

def next_business_day(date):
    one_day = timedelta(days=1)
    next_day = date + one_day
    while next_day.weekday() >= 5:  # 5 = Saturday, 6 = Sunday
        next_day += one_day
    return next_day        

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

def create_config(symbol):
    return {
        "stock": {"symbol": symbol, "period": "5y"},
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

def download_data(config):
    ticker = yf.Ticker(config["stock"]["symbol"])
    data = ticker.history(period=config["stock"]["period"])
    if data.empty:
        raise ValueError(f"No data found for {config['stock']['symbol']}. Please check if the symbol is correct and try again.")
    data_date = data.index
    data_close_price = data['Close'].values
    num_data_points = len(data_date)
    display_date_range = f"from {data_date[0].strftime('%Y-%m-%d')} to {data_date[-1].strftime('%Y-%m-%d')}"
    print("Number data points", num_data_points, display_date_range)
    return data_date, data_close_price, num_data_points, display_date_range

def get_ticker_symbol(input_string):
    if not input_string or input_string.lower() == 'null':
        print(f"Invalid input: {input_string}")
        return None
    try:
        ticker = yf.Ticker(input_string)
        info = ticker.info
        if 'symbol' in info:
            return info['symbol']
        
        search = yf.Ticker(input_string).search()
        if search:
            return search[0]['symbol']
        
        print(f"Could not find ticker symbol for {input_string}")
        return None
    except Exception as e:
        print(f"Error in get_ticker_symbol: {str(e)}")
        return None
        
def run_prediction(name_or_ticker):
    print(f"Running prediction for symbol or name: {name_or_ticker}")
    if not name_or_ticker or name_or_ticker.lower() == 'null':
        print("Invalid input")
        return None
    
    try:
        symbol = get_ticker_from_name(name_or_ticker)
        print(f"Resolved symbol: {symbol}")
        if not symbol:
            return None
        
        config = create_config(symbol)
        
        stock = yf.Ticker(symbol)
        recommendations = stock.recommendations
        if recommendations is not None and not recommendations.empty:
            recommendations = recommendations.iloc[-5:]  # Get the last 5 recommendations
            recommendations_dict = recommendations.reset_index().to_dict('records')
        else:
            recommendations_dict = []
        
        data_date, data_close_price, num_data_points, display_date_range = download_data(config)
        print("Data downloaded successfully")
    
        scaler = MinMaxScaler()
        normalized_data_close_price = scaler.fit_transform(data_close_price.reshape(-1, 1))
        print("Data normalized")
        
        X, y = prepare_data(normalized_data_close_price, window_size=config["data"]["window_size"])
        print("Data prepared for model")
        
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        print("Starting model training")
        model = create_and_train_model(X_train, y_train)
        print("Model training completed")
        
        print("Starting predictions")
        mean_prediction, ci_lower, ci_upper = predict_with_confidence(model, X_test[-1].reshape(1, -1))
        
        predicted_price = scaler.inverse_transform(mean_prediction.reshape(-1, 1)).flatten()
        ci_lower = scaler.inverse_transform(ci_lower.reshape(-1, 1)).flatten()
        ci_upper = scaler.inverse_transform(ci_upper.reshape(-1, 1)).flatten()
        
        print(f"Prediction completed: mean {predicted_price[0]:.2f}, CI [{ci_lower[0]:.2f}, {ci_upper[0]:.2f}]")

        current_price = data_close_price[-1]
        current_date = datetime.now().date()
        prediction_date = next_business_day(current_date)
    
        plot_full = generate_full_plot(data_date, data_close_price, config)
        plot_prediction = generate_prediction_plot(data_date, data_close_price, predicted_price[0], ci_lower[0], ci_upper[0], config)
        print("Plots generated")
        
        result = {
            "symbol": symbol,
            "current_price": float(current_price),
            "predicted_price": round(float(predicted_price[0]), 2),
            "ci_lower": round(float(ci_lower[0]), 2),
            "ci_upper": round(float(ci_upper[0]), 2),
            "prediction_date": prediction_date.strftime('%Y-%m-%d'),
            "display_date_range": display_date_range,
            "plot_full": plot_full,
            "plot_prediction": plot_prediction,
            "analyst_recommendations": recommendations_dict
        }
        print("Prediction result:", result)
        return result
    except Exception as e:
        print(f"Error during prediction for {name_or_ticker}: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

def generate_full_plot(data_date, data_close_price, config):
    fig = figure(figsize=(25, 5), dpi=80)
    plt.plot(data_date, data_close_price, color=config["plots"]["color_actual"])
    plt.title(f"Daily close price for {config['stock']['symbol']}")
    plt.grid(visible=True, which='major', axis='y', linestyle='--')
    
    img_buf = io.BytesIO()
    plt.savefig(img_buf, format='png')
    img_buf.seek(0)
    img_base64 = base64.b64encode(img_buf.getvalue()).decode('utf-8')
    plt.close()
    
    return img_base64

def generate_prediction_plot(data_date, data_close_price, predicted_price, ci_lower, ci_upper, config):
    fig = figure(figsize=(25, 5), dpi=80)
    plt.plot(data_date[-30:], data_close_price[-30:], label="Actual prices", color=config["plots"]["color_actual"])
    plt.plot(data_date[-1] + pd.Timedelta(days=1), predicted_price, 'ro', label="Predicted price")
    plt.vlines(data_date[-1] + pd.Timedelta(days=1), ci_lower, ci_upper, color='r', linestyles='dashed', label="95% CI")
    plt.title(f"Predicted close price for {config['stock']['symbol']}")
    plt.grid(visible=True, which='major', axis='y', linestyle='--')
    plt.legend()
    
    img_buf = io.BytesIO()
    plt.savefig(img_buf, format='png')
    img_buf.seek(0)
    img_base64 = base64.b64encode(img_buf.getvalue()).decode('utf-8')
    plt.close()
    
    return img_base64

if __name__ == "__main__":
    symbol = input("Enter a stock symbol: ") if len(sys.argv) <= 1 else sys.argv[1]
    result = run_prediction(symbol)
    if result:
        print(f"Prediction for {result['symbol']}:")
        print(f"Current price: ${result['current_price']:.2f}")
        print(f"Predicted price for {result['prediction_date']}: ${result['predicted_price']:.2f}")
        print(f"Data range: {result['display_date_range']}")