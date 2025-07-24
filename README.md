# Quant Simulator - Prediction and backtest of investment strategies using Python
**⚠️ WIP - NOT WORKING AT THE MOMENT!!!**

## **Goal of this project**
> To design and evaluate rule-based trading strategies using historical data, in order to build intuition about financial markets, develop coding and analytical skills, and lay the foundation for more advanced algorithmic trading or quant research.

## **Overview**
- Built a simulator that tests different investment strategies in securities
- Predict movements or generate signals based in simple data and measure the outcome of those strategies base on real data
- Implemented a Dual Moving Average Crossover (DMAC) Strategy
- Created a algorithmic that checks if theres a pattern in the short and long SMA windows that maximizes returns across multiple securities and time periods.

## **Table of Contents**

## **Requirements**
- Python 3.7+
- Libraries:
  - yfinance
  - pandas
  - numpy
  - inter
  - numpy
  - seaborn
  - matplotlib
  - sqlite3
### **Strategies**
**Dual Moving Average Crossover (DMAC) Strategy**
- The concept of this strategy is fairly straightforward.  Calculate two moving averages of the price of a security.  One average would be the short term (ST) (strictly relative to the other moving average) and the other long term (LT).  Mathematically speaking, the long term moving average (LTMA) will have a lower variance and will move in the same direction as the short term moving average but at a different rate.  The different rates of direction, induces points where the values of the two moving averages may equal and or cross one another.  These points are called the crossover points. 

In the dual moving average crossover trading strategy, these crossovers are points of decision to buy or sell the currencies.  What these crossover points imply depends on the approach the investor has in their strategy. There are two schools of thought: Technical and Value:
- **Technical Approach**: suggests that when the Short Term Moving Average (STMA) moves above the LTMA, that represents a Buy (or Long) signal.  (Conversely, when the STMA moves below the LTMA, the Technical Approach indicates a Sell (or Short) signal.)  The intuition behind this strategy can be explained in terms of momentum.  Basically, the principle of momentum states that a price that is moving up (or down) during period t is likely to continue to move up (or down) in period t+1 unless evidence exists to the contrary.  When the STMA moves above the LTMA, this provides a lagged indicator that the price is moving upward relative to the historical price.  Buy high, sell higher.
  
- **Value Approach**: offers the opposite trading signals to the Technical Approach.  The Value Approach claims that when the STMA crosses from below to above the LTMA, that the investment is now overvalued, and should be sold.  Conversely when the currency STMA moves below the LTMA then the currency is undervalued it should be bought.  The intuition behind the Value Approach can be thought simply as a mean reversion approach.  Buy low (value), sell high (overvalued). 

In this project we followed the Technical Approach.

src: https://people.duke.edu/~charvey/Teaching/BA453_2002/CCAM/CCAM.htm
#### Hypothesis:
> There exists a combination of short and long SMA windows (e.g., 14 and 22) that maximizes returns across multiple securities and time periods.
