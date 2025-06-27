import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("5y_data.csv")

xpoint = df["Date"]

ypoint = df["Close"]

plt.plot(
    xpoint,
    ypoint,
    color='orange',
    linestyle='-',
    linewidth=2,
    markersize=5,
    label='Close Price'
)

plt.title(
    'SPY Close Price (2009-03-02 to 2014-03-02)',
    fontsize=16,
    fontweight='bold'
    )

plt.xlabel('Date', fontsize=12)

plt.ylabel('Closing Price (USD)', fontsize=12)

df['SMA_20'] = df['Close'].rolling(window=20).mean()

# List to store the SMA values
#sma_20_list = []

# Loop through each index in the dataframe
#for i in range(len(df)):
    #if i < 19:
        # Not enough data points to compute SMA-20 yet
        #"sma_20_list.append(None)  # Or np.nan if you prefer
    #
        # Slice the last 20 close prices (i-19 to i, inclusive)
        #window = df['Close'][i-19:i+1]  # 20 values ending at index i
        #$average = window.mean()
        #sma_20_list.append(int(average))

# Assign the computed SMA list to a new column
# df['SMA_20_manual'] = sma_20_list

plt.plot(
    df['Date'],
    df['SMA_20_manual'],
    color='red',
    linestyle='--',
    linewidth=2,
    label='20-Day SMA'
)

sma_50_list = []

for i in range(len(df)): # 
    if i < 49:
        sma_50_list.append(None)
    else:
        window = df['Close'][i-49:i+1]
        average = window.mean()
        sma_50_list.append(int(average))

# Assign the computed SMA list to a new column

df['SMA_50'] = sma_50_list

plt.plot(
    df['Date'],
    df['SMA_50'],
    color='green',
    linestyle='--',
    linewidth=2,
    label='50-Day SMA'
)


buy = []


for i in df:
    if ['SMA_20_manual'] == ['SMA_50']:
        if ['SMA_20_manual'][i+1] > ['SMA_50'][i+1]:
            buy = df['Close']
    else:
        buy = 0

df['Buy Signal'] = buy
    
print(df.to_string(100))

plt.scatter(
    df['Date'],
    df['Buy Signal'],
    color='blue',
)

plt.show()
