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
from crypto_analysis import get_crypto_data, crypto_mapping
from sklearn.preprocessing import MinMaxScaler

def next_business_day(date):
    one_day = timedelta(days=1)
    next_day = date + one_day
    return next_day  # For crypto, we don't skip weekends

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

    def init_weights(self):
        for name, param in self.lstm.named_parameters():
            if 'bias' in name:
                nn.init.constant_(param, 0.0)
            elif 'weight_ih' in name:
                nn.init.kaiming_normal_(param)
            elif 'weight_hh' in name:
                nn.init.orthogonal_(param)

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
        x, y = create_sequences(scaled_data, seq_length)
        
        # Split data into train and test
        train_size = int(len(x) * 0.8)
        x_train, x_test = x[:train_size], x[train_size:]
        y_train, y_test = y[:train_size], y[train_size:]

        # Convert to PyTorch tensors
        x_train = torch.FloatTensor(x_train)
        y_train = torch.FloatTensor(y_train)
        x_test = torch.FloatTensor(x_test)
        y_test = torch.FloatTensor(y_test)

        # Build LSTM model
        model = LSTMModel(input_size=1, hidden_layer_size=50, num_layers=2, output_size=1)
        criterion = nn.MSELoss()
        optimizer = optim.Adam(model.parameters(), lr=0.01)

        # Train the model
        num_epochs = 100
        for epoch in range(num_epochs):
            model.train()
            optimizer.zero_grad()
            outputs = model(x_train.unsqueeze(2))
            loss = criterion(outputs, y_train)
            loss.backward()
            optimizer.step()
            if (epoch+1) % 10 == 0:
                print(f'Epoch [{epoch+1}/{num_epochs}], Loss: {loss.item():.4f}')

        # Make prediction
        model.eval()
        with torch.no_grad():
            test_pred = model(x_test.unsqueeze(2))
            predicted_price = scaler.inverse_transform(test_pred[-1].numpy().reshape(1, -1))

        # Prepare result
        current_price = df['Close'].iloc[-1]
        prediction_date = pd.Timestamp.now() + pd.Timedelta(days=1)
        
        result = {
            "symbol": symbol,
            "current_price": float(current_price),
            "predicted_price": float(predicted_price[0][0]),
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