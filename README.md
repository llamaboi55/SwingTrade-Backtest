# SwingTrade-Backtest
````markdown
# 📈 Swing Trading Backtester with RSI, MACD & ATR Strategy

This project implements a **swing trading backtest system** using technical indicators such as **RSI**, **MACD**, and an **ATR-based trailing stop**. It fetches historical stock data via Yahoo Finance and simulates buy/sell trades based on these indicators. The final results are visualized in a chart and saved as a PNG.

---

## 🔧 Features

- Customizable symbol and test window
- Technical indicators used:
  - **RSI (Relative Strength Index)**
  - **MACD (Moving Average Convergence Divergence)**
  - **ATR (Average True Range)**
  - **MA Exit (Moving Average Exit)**
- Dynamic trailing stop-loss based on ATR
- Entry strategy based on oversold RSI recovery + MACD crossover
- Exit strategy includes:
  - Stop-loss trigger
  - RSI overbought condition
  - Price falling below moving average
- Visual trade annotations on the price chart

---

## 📦 Dependencies

```bash
pip install yfinance pandas numpy matplotlib
````

---

## 📁 File Structure

```
.
├── swing_trades.py      # main script
├── swing_trades.png     # output chart (auto-generated)
```

---

## 🧠 Strategy Logic Summary

### Buy Condition:

* RSI crosses up from below 30
* MACD line crosses above Signal line

### Sell Condition:

* Price hits ATR-based trailing stop
* RSI exceeds 60
* Price drops below short-term moving average

### Fallback:

* If no trades are detected, buy at lowest and sell at highest point

---

## 📉 Output

* A chart with:

  * Daily closing prices
  * Buy and sell signals
  * Trade return annotations in %
* Output saved as `swing_trades.png`

---

## 🏃 Example Usage

```bash
python swing_trades.py
```

Example Output:

```
Trades generated: 3
✔ saved swing_trades.png
```

---

## 🖼️ Example Chart

Chart includes:

* Green upward arrows for buy signals
* Red downward arrows for sell signals
* Percentage profit/loss between trade points

---

## 🔍 How It Works (Simplified Code Overview)

```python
# Technical indicator functions
def rsi(prices): ...
def macd(prices): ...
def atr(df): ...

# Load historical price data
yf.download(...)

# Compute indicators
px['RSI'], px['MACD'], px['ATR'], px['MA_EXIT']

# Backtest loop:
#   - Detect entry signals (RSI + MACD)
#   - Monitor trailing stop and exit conditions

# Plot & annotate results
plt.plot(...)
```

---

## 🛠️ Customizable Parameters

| Parameter   | Description                          | Example |
| ----------- | ------------------------------------ | ------- |
| `SYMBOL`    | Stock ticker symbol                  | "GOOGL" |
| `TEST_DAYS` | Number of trading days to backtest   | 30      |
| `RSI_EXIT`  | RSI threshold to trigger exit        | 60      |
| `TRAIL_ATR` | Trailing stop multiplier (ATR-based) | 3       |

---

## 🚀 Ideas for Extension

* Add portfolio performance metrics (Sharpe, drawdown)
* Run on multiple stocks/tickers
* Optimize parameters with grid search
* Integrate a GUI (e.g. Streamlit)
* Connect to live brokerage API

---

## 📜 License

MIT License – free to use, modify, and distribute.

---

## 🤝 Contributing

Pull requests welcome! If you find bugs or have feature suggestions, feel free to open an issue.

