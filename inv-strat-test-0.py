import itertools
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import yfinance as yf 
import sqlite3 

class SMABacktester:
    def __init__(self, data, short_window, long_window):
        self.df = data.copy()
        self.short_window = short_window
        self.long_window = long_window
        self._prepare_data()

    def _prepare_data(self):
        self.df['SMA_Short'] = self.df['Close'].rolling(window=self.short_window).mean()
        self.df['SMA_Long'] = self.df['Close'].rolling(window=self.long_window).mean()
        self.df['Signal'] = 0
        # Buy signal
        self.df.loc[(self.df['SMA_Short'].shift(1) < self.df['SMA_Long'].shift(1)) &
                    (self.df['SMA_Short'] > self.df['SMA_Long']), 'Signal'] = 1
        # Sell signal
        self.df.loc[(self.df['SMA_Short'].shift(1) > self.df['SMA_Long'].shift(1)) &
                    (self.df['SMA_Short'] < self.df['SMA_Long']), 'Signal'] = -1
        self.signals = self.df[self.df['Signal'] != 0].copy()
        self.signals = self.signals[self.signals['Signal'] != self.signals['Signal'].shift(1)]
        self.df['daily_return'] = self.df['Close'].pct_change()*100

    def simulate_trades(self):
        self.signals['Trade_Return'] = np.nan
        entry_price = None

        for i, row in self.signals.iterrows():
            if row['Signal'] == 1:
                entry_price = row['Close']

            elif row['Signal'] == -1 and entry_price is not None:
                current_return = row['Close'] - entry_price

                # Only sell if return is positive
                if current_return > 0:
                    self.signals.loc[i, 'Trade_Return'] = current_return
                    entry_price = None  # Reset because we sold
                else:
                    pass  # Don't sell — hold the position

        self.signals['Cumulative_Return'] = self.signals['Trade_Return'].cumsum()
        return self.signals[['Date', 'Signal', 'Close', 'Trade_Return', 'Cumulative_Return']]

    def plot_strategy(self):
        plt.figure(figsize=(14, 8))
        plt.plot(self.df['Date'], self.df['Close'], label='Close Price', color='gray', alpha=0.6)
        plt.plot(self.df['Date'], self.df['SMA_Short'], label=f'{self.short_window}-Day SMA', color='red')
        plt.plot(self.df['Date'], self.df['SMA_Long'], label=f'{self.long_window}-Day SMA', color='blue')
        plt.plot(self.df['Date'], self.df['daily_return'], label='Daily Returns', color = 'green')
                 
        buy = self.signals[self.signals['Signal'] == 1]
        sell = self.signals[self.signals['Signal'] == -1]

        plt.scatter(buy['Date'], buy['Close'], label='Buy Signal', marker='^', color='green', s=100)
        plt.scatter(sell['Date'], sell['Close'], label='Sell Signal', marker='v', color='red', s=100)

        plt.title('SMA Crossover Strategy')
        plt.xlabel('Date')
        plt.ylabel('Price')
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        plt.show()

ticker = ['MSFT', 'APPL', 'SPY', 'TSLA', 'NVDA']
start_date = "2009-03-02"
end_date = "2014-02-28"

# Download data
data = yf.download(ticker, start=start_date, end=end_date, interval="1d")

print(data)

# Checking
if data.empty:
    raise ValueError("Download falhou ou ticker não tem dados nesse período.")

# Preparation

for i in ticker:
    df = data[['Close'][i]].reset_index()
    df['Close'] = pd.to_numeric(df['Close'], errors='coerce')
    df['Date'] = pd.to_datetime(df['Date'])
    backtester = SMABacktester(df, 14, 22) # self
    results = backtester.simulate_trades()
    print(results)
    backtester.plot_strategy()

def optimize_sma_strategy(df, short_range, long_range):
    results = []

    for short_w, long_w in itertools.product(short_range, long_range):
        if short_w >= long_w:
            continue  # Skip invalid pairs

        bt = SMABacktester(df, short_window=short_w, long_window=long_w)
        bt._prepare_data()
        trades = bt.simulate_trades()

        if trades['Cumulative_Return'].dropna().empty:
            continue

        final_return = trades['Cumulative_Return'].dropna().iloc[-1]
        results.append({
            'Short_SMA': short_w,
            'Long_SMA': long_w,
            'Cumulative_Return': final_return
        })

    results_df = pd.DataFrame(results)
    best_result = results_df.sort_values(by='Cumulative_Return', ascending=False).head(1)

    return results_df, best_result

short_range = range(5, 51, 5)    # e.g., 5, 10, ..., 50
long_range = range(20, 201, 10)  # e.g., 20, 30, ..., 200
for i in ticker:
    results_df, best_result = optimize_sma_strategy(df, short_range, long_range)

    print("Top 5 performing SMA combinations:")
    print(results_df.sort_values(by='Cumulative_Return', ascending=False).head(5))

    pivot = results_df.pivot(index="Short_SMA", columns="Long_SMA", values="Cumulative_Return")

"""
plt.figure(figsize=(12, 8))
sns.heatmap(pivot, annot=True, fmt=".1f", cmap="viridis")
plt.title("Cumulative Return by SMA Window Combination")
plt.show()
"""

 # Creat Table and DB in Python for SQL
connection = sqlite3.connect('DataPatterns.db')
cursor = connection.cursor()

for i in ticker:
    name = i
    start_date = start_date
    end_date = end_date
    short_window = best_result['short_range']
    long_window = best_result['long_range']
    cumlt_return = results_df['Cumulative_Return']
    cursor.execute("INSERT INTO data_p VALUES (?, ?, ?, ?, ?, ?)", (name, start_date, end_date, short_window, long_window,
                                                       cumlt_return))
# MUST commit data or no changes will be saved
connection.commit()
connection.close()
