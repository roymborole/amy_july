import yfinance as yf
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.pyplot import figure
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import pandas as pd
import io
import base64
import sys
import torch.nn.functional as F
from datetime import datetime, timedelta
from ticker_utils import get_ticker_from_name

def next_business_day(date):
    one_day = timedelta(days=1)
    next_day = date + one_day
    while next_day.weekday() >= 5:  # 5 = Saturday, 6 = Sunday
        next_day += one_day
    return next_day        

def create_sequences(data, seq_length):
    xs = []
    ys = []
    for i in range(len(data) - seq_length - 1):
        x = data[i:(i + seq_length)]
        y = data[i + seq_length]
        xs.append(x)
        ys.append(y)
    return np.array(xs), np.array(ys)

def prepare_data_x(x, window_size):
    n_row = x.shape[0] - window_size + 1
    output = np.lib.stride_tricks.as_strided(x, shape=(n_row, window_size), strides=(x.strides[0], x.strides[0]))
    return output[:-1], output[-1]

def prepare_data_y(x, window_size):
    output = x[window_size:]
    return output

class Normalizer:
    def __init__(self):
        self.mu = None
        self.sd = None

    def fit_transform(self, x):
        self.mu = np.mean(x, axis=(0), keepdims=True)
        self.sd = np.std(x, axis=(0), keepdims=True)
        normalized_x = (x - self.mu)/self.sd
        return normalized_x

    def inverse_transform(self, x):
        return (x*self.sd) + self.mu

class TimeSeriesDataset(Dataset):
    def __init__(self, x, y):
        x = np.expand_dims(x, 2)
        self.x = x.astype(np.float32)
        self.y = y.astype(np.float32)

    def __len__(self):
        return len(self.x)

    def __getitem__(self, idx):
        return (self.x[idx], self.y[idx])

class LSTMModel(nn.Module):
    def __init__(self, input_size=1, hidden_layer_size=32, num_layers=2, output_size=1, dropout=0.2):
        super().__init__()
        self.hidden_layer_size = hidden_layer_size
        self.linear_1 = nn.Linear(input_size, hidden_layer_size)
        self.relu = nn.ReLU()
        self.lstm = nn.LSTM(hidden_layer_size, hidden_size=self.hidden_layer_size, num_layers=num_layers, batch_first=True)
        self.dropout = nn.Dropout(dropout)
        self.linear_2 = nn.Linear(num_layers * hidden_layer_size, output_size)
        self.init_weights()

    def forward(self, x):
        batchsize = x.shape[0]
        x = self.linear_1(x)
        x = self.relu(x)
        lstm_out, (h_n, c_n) = self.lstm(x)
        x = h_n.permute(1, 0, 2).reshape(batchsize, -1)
        x = self.dropout(x)
        predictions = self.linear_2(x)
        return predictions[:, -1]

    def enable_dropout(self):
        """ Function to enable the dropout layers during test-time """
        for m in self.modules():
            if m.__class__.__name__.startswith('Dropout'):
                m.train()

    def init_weights(self):
        for name, param in self.lstm.named_parameters():
            if 'bias' in name:
                nn.init.constant_(param, 0.0)
            elif 'weight_ih' in name:
                nn.init.kaiming_normal_(param)
            elif 'weight_hh' in name:
                nn.init.orthogonal_(param)

    def forward(self, x):
        batchsize = x.shape[0]
        x = self.linear_1(x)
        x = self.relu(x)
        lstm_out, (h_n, c_n) = self.lstm(x)
        x = h_n.permute(1, 0, 2).reshape(batchsize, -1)
        x = self.dropout(x)
        predictions = self.linear_2(x)
        return predictions[:, -1]
    
    def enable_dropout(self):
        """ Function to enable the dropout layers during test-time """
        for m in self.modules():
            if m.__class__.__name__.startswith('Dropout'):
                m.train()

def run_epoch(dataloader, model, optimizer, scheduler, criterion, is_training=False):
    epoch_loss = 0
    if is_training:
        model.train()
    else:
        model.eval()
    for idx, (x, y) in enumerate(dataloader):
        if is_training:
            optimizer.zero_grad()
        batchsize = x.shape[0]
        x = x.to(model.linear_1.weight.device)
        y = y.to(model.linear_1.weight.device)
        out = model(x)
        loss = criterion(out.contiguous(), y.contiguous())
        if is_training:
            loss.backward()
            optimizer.step()
        epoch_loss += (loss.detach().item() / batchsize)
    lr = scheduler.get_last_lr()[0]
    return epoch_loss, lr

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
            "num_lstm_layers": 2,
            "lstm_size": 32,
            "dropout": 0.2,
        },
        "training": {
            "device": "cpu",
            "batch_size": 64,
            "num_epoch": 100,
            "learning_rate": 0.01,
            "scheduler_step_size": 40,
        }
    }

def download_data(config):
    ticker = yf.Ticker(config["stock"]["symbol"])
    data = ticker.history(period=config["stock"]["period"])
    if data.empty:
        print(f"No data found for symbol: {config['stock']['symbol']}")
        print(f"Ticker info: {ticker.info}")
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
        # First, try to use the input as a ticker symbol
        ticker = yf.Ticker(input_string)
        info = ticker.info
        if 'symbol' in info:
            return info['symbol']
        
        # If that doesn't work, search for the company
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
        
        # Use the resolved symbol to create the config
        config = create_config(symbol)
        
        # Fetch analyst recommendations
        stock = yf.Ticker(symbol)
        recommendations = stock.recommendations
        if recommendations is not None and not recommendations.empty:
            recommendations = recommendations.iloc[-5:]  # Get the last 5 recommendations
            recommendations_dict = recommendations.reset_index().to_dict('records')
        else:
            recommendations_dict = []
        
        data_date, data_close_price, num_data_points, display_date_range = download_data(config)
        print("Data downloaded successfully")
    
        scaler = Normalizer()
        normalized_data_close_price = scaler.fit_transform(data_close_price)
        print("Data normalized")
        
        data_x, data_x_unseen = prepare_data_x(normalized_data_close_price, window_size=config["data"]["window_size"])
        data_y = prepare_data_y(normalized_data_close_price, window_size=config["data"]["window_size"])
        print("Data prepared for model")
        
        split_index = int(data_y.shape[0] * config["data"]["train_split_size"])
        data_x_train, data_x_val = data_x[:split_index], data_x[split_index:]
        data_y_train, data_y_val = data_y[:split_index], data_y[split_index:]
        
        dataset_train = TimeSeriesDataset(data_x_train, data_y_train)
        dataset_val = TimeSeriesDataset(data_x_val, data_y_val)
        
        train_dataloader = DataLoader(dataset_train, batch_size=config["training"]["batch_size"], shuffle=True)
        val_dataloader = DataLoader(dataset_val, batch_size=config["training"]["batch_size"], shuffle=True)
        print("Dataloaders created")
        
        model = LSTMModel(
            input_size=config["model"]["input_size"],
            hidden_layer_size=config["model"]["lstm_size"],
            num_layers=config["model"]["num_lstm_layers"],
            output_size=1,
            dropout=config["model"]["dropout"]
        )
        model = model.to(config["training"]["device"])
        print("Model created")
        
        criterion = nn.MSELoss()
        optimizer = optim.Adam(model.parameters(), lr=config["training"]["learning_rate"], betas=(0.9, 0.98), eps=1e-9)
        scheduler = optim.lr_scheduler.StepLR(optimizer, step_size=config["training"]["scheduler_step_size"], gamma=0.1)
        
        print("Starting model training")
        for epoch in range(config["training"]["num_epoch"]):
            loss_train, lr_train = run_epoch(train_dataloader, model, optimizer, scheduler, criterion, is_training=True)
            loss_val, lr_val = run_epoch(val_dataloader, model, optimizer, scheduler, criterion)
            scheduler.step()
            if epoch % 10 == 0:
                print(f"Epoch {epoch}: train loss {loss_train:.4f}, val loss {loss_val:.4f}")
        print("Model training completed")
        
        model.eval()
        model.enable_dropout()  # Enable dropout during inference

        # Monte Carlo Dropout for confidence interval
        num_samples = 1000
        predictions = []
        x = torch.tensor(data_x_unseen).float().to(config["training"]["device"]).unsqueeze(0).unsqueeze(2)
        
        print("Starting Monte Carlo predictions")
        for _ in range(num_samples):
            with torch.no_grad():
                output = model(x)
                predictions.append(output.item())

        predictions = np.array(predictions)
        predicted_price = scaler.inverse_transform(predictions.reshape(-1, 1)).flatten()
        
        mean_prediction = np.mean(predicted_price)
        ci_lower = np.percentile(predicted_price, 2.5)
        ci_upper = np.percentile(predicted_price, 97.5)
        print(f"Prediction completed: mean {mean_prediction:.2f}, CI [{ci_lower:.2f}, {ci_upper:.2f}]")

        current_price = data_close_price[-1]
        current_date = datetime.now().date()
        prediction_date = next_business_day(current_date)
    
        plot_full = generate_full_plot(data_date, data_close_price, config)
        plot_prediction = generate_prediction_plot(data_date, data_close_price, mean_prediction, ci_lower, ci_upper, config)
        print("Plots generated")
        
        result = {
            "symbol": symbol,
            "current_price": float(current_price),
            "predicted_price": round(float(mean_prediction), 2),
            "ci_lower": round(float(ci_lower), 2),
            "ci_upper": round(float(ci_upper), 2),
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


   
        
  