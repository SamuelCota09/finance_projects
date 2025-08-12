import itertools
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import yfinance as yf 
import sqlite3

# --- CLASS ---
class SMABacktester:
    def __init__(self, data, short_window, long_window):
        self.df = data.copy()
        self.short_window = short_window
        self.long_window = long_window
        self._prepare_data()

    # --- DATA PREPARATION ---
    def _prepare_data(self):

        # SMA Short Calculatin and Atribution to a Row
        self.df['SMA_Short'] = self.df['Close'].rolling(window=self.short_window).mean()

        # SMA Long Calculatin and Atribution to a Row
        self.df['SMA_Long'] = self.df['Close'].rolling(window=self.long_window).mean()
        
        # --- STRATEGY ---

        # Initial Signal
        self.df['Signal'] = 0

        # Signal of 1 (Long) when SMA Short crosses and is greater than SMA Long
        self.df.loc[(self.df['SMA_Short'].shift(1) > self.df['SMA_Long'].shift(1)) & 
                    (self.df['SMA_Short'] < self.df['SMA_Long']), 'Signal'] = 1

        # Signal of -1 (Short) when SMA Short crosses and is not greater than SMA Long
        self.df.loc[(self.df['SMA_Short'].shift(1) < self.df['SMA_Long'].shift(1)) & 
                    (self.df['SMA_Short'] > self.df['SMA_Long']), 'Signal'] = -1
        
        # Uses Only the Data with Long or Short Signals
        self.signals = self.df[self.df['Signal'] != 0].copy()
        # Restraints the Data where theres Equal Signals
        self.signals = self.signals[self.signals['Signal'] != self.signals['Signal'].shift(1)]
        
        self.df['daily_return'] = self.df['Close'].pct_change()*100

    # --- SIMULATION ---
    def simulate_trades(self):
        self.signals['Trade_Return'] = np.nan
        entry_price = None

        # Iterates over each row
        for i, row in self.signals.iterrows():
            if row['Signal'] == 1:
                entry_price = row['Close']
            elif row['Signal'] == -1 and entry_price is not None:
                current_return = row['Close'] - entry_price
                
                # Stores the Current Return if its Positive and Ignores if the Short leads in a loss
                if current_return > 0:
                    self.signals.loc[i, 'Trade_Return'] = current_return
                    entry_price = None
        self.signals['Cumulative_Return'] = self.signals['Trade_Return'].cumsum()
        return self.signals[['Date', 'Signal', 'Close', 'Trade_Return', 'Cumulative_Return']]

# --- OPTIMIZATION FUNCTION ---
def optimize_sma_strategy(df, short_range, long_range):
    results = []

    # Computes the multiple combinations of SMA Short and SMA long and checks the Best
    for short_w, long_w in itertools.product(short_range, long_range):
        if short_w >= long_w:
            continue
        bt = SMABacktester(df, short_window=short_w, long_window=long_w)
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

# --- PARAMETERS ---
tickers = [
    # Tech
    'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA',
    # Finance
    'JPM', 'BAC', 'WFC', 'GS', 'AXP',
    # Energy
    'XOM', 'CVX', 'BP', 'ENB', 'SLB',
    # Health
    'JNJ', 'PFE', 'MRK', 'LLY', 'ABBV',
    # Consume
    'WMT', 'PG', 'KO', 'PEP', 'COST',
    # Industry
    'GE', 'CAT', 'UPS', 'MMM', 'BA',
    # China / Global
    'BABA', 'TSM', 'NIO', 'XIACY', 'XPEV',
    # ETFs
    'SPY', 'QQQ', 'DIA', 'ARKK', 'EFA'
]
start_date = "2023-04-25"
end_date = "2025-08-12"
short_range = range(5, 51, 5)
long_range = range(20, 201, 10)

# --- DATA DOWNLOAD ---
data = yf.download(tickers, start=start_date, end=end_date, interval="1d", group_by='ticker')
if data.empty:
    raise ValueError("Download falhou.")

results_summary = []
all_results = {}

# --- PRICE CHARTS FIRST ---
fig_price, axes_price = plt.subplots(len(tickers), 1, figsize=(14, 5 * len(tickers)))

# Single Ticket
if len(tickers) == 1:
    axes_price = [axes_price]  # ensure it's iterable

# Multiple Tickets
for idx, ticker in enumerate(tickers):
    df = data[ticker].reset_index()[['Date', 'Close']]
    df['Date'] = pd.to_datetime(df['Date'])

    # Simulation with SMA 14-22
    backtester = SMABacktester(df, 14, 22)
    trades = backtester.simulate_trades()

    results_df, best_result = optimize_sma_strategy(df, short_range, long_range)
    all_results[ticker] = results_df

    results_summary.append({
        'Ticker': ticker,
        'Start_Date': start_date,
        'End_Date': end_date,
        'Short_SMA': int(best_result['Short_SMA'].values[0]),
        'Long_SMA': int(best_result['Long_SMA'].values[0]),
        'Best_Cumulative_Return': float(best_result['Cumulative_Return'].values[0])
    })

    # PLOT - PRICE + SIGNALS
    ax = axes_price[idx]
    df_plot = backtester.df
    buy = backtester.signals[backtester.signals['Signal'] == 1]
    sell = backtester.signals[backtester.signals['Signal'] == -1]

    ax.plot(df_plot['Date'], df_plot['Close'], label='Close Price', color='gray', alpha=0.6)
    ax.plot(df_plot['Date'], df_plot['SMA_Short'], label=f'SMA {backtester.short_window}', color='red')
    ax.plot(df_plot['Date'], df_plot['SMA_Long'], label=f'SMA {backtester.long_window}', color='blue')
    ax.scatter(buy['Date'], buy['Close'], label='Buy', marker='^', color='green', s=60)
    ax.scatter(sell['Date'], sell['Close'], label='Sell', marker='v', color='red', s=60)
    ax.set_title(f"{ticker} - SMA Strategy")
    ax.set_xlabel("Date")
    ax.set_ylabel("Price")
    ax.legend()
    ax.grid(True)

plt.tight_layout()
plt.suptitle("SMA Strategy - Price Charts", fontsize=20, y=1.02)
plt.show()

# --- HEATMAPS SEPARATE ---
fig_heat, axes_heat = plt.subplots(len(tickers), 1, figsize=(10, 5 * len(tickers)))

# Single Ticket
if len(tickers) == 1:
    axes_heat = [axes_heat]

#Multiple Tickets
for idx, ticker in enumerate(tickers):
    results_df = all_results[ticker]
    pivot = results_df.pivot(index="Short_SMA", columns="Long_SMA", values="Cumulative_Return")

    sns.heatmap(pivot, ax=axes_heat[idx], cmap="viridis", cbar=True)
    axes_heat[idx].set_title(f"{ticker} - SMA Cumulative Return Heatmap")

plt.tight_layout()
plt.suptitle("SMA Optimization - Heatmaps", fontsize=20, y=1.02)
plt.show()

# --- SAVE TO DATABASE ---
connection = sqlite3.connect('DataPatterns.db')
cursor = connection.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS data_p (
    Ticker TEXT,
    Start_Date TEXT,
    End_Date TEXT,
    Short_SMA INTEGER,
    Long_SMA INTEGER,
    Best_Cumulative_Return REAL
)
""")

for row in results_summary:
    cursor.execute("""
    INSERT INTO data_p (Ticker, Start_Date, End_Date, Short_SMA, Long_SMA, Best_Cumulative_Return)
    VALUES (?, ?, ?, ?, ?, ?)
    """, (row['Ticker'], row['Start_Date'], row['End_Date'],
          row['Short_SMA'], row['Long_SMA'], row['Best_Cumulative_Return']))

connection.commit()
connection.close()
