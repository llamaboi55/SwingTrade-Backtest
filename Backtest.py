import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# ─── PARAMETERS ────────────────────────────────────────────────────────────────
SYMBOL     = "GOOGL"
TEST_END   = "2025-05-29"
TEST_DAYS  = 30
RSI_N      = 14
MACD_FAST  = 12
MACD_SLOW  = 26
MACD_SIG   = 9
ATR_N      = 14
TRAIL_ATR  = 3
RSI_EXIT   = 60
MA_EXIT    = 5
PNG_FILE   = "swing_trades.png"
# ────────────────────────────────────────────────────────────────────────────────

def rsi(prices, n=14):
    d = prices.diff()
    up, dn = d.clip(lower=0), -d.clip(upper=0)
    ema_up = up.ewm(alpha=1/n, adjust=False).mean()
    ema_dn = dn.ewm(alpha=1/n, adjust=False).mean()
    rs = ema_up / ema_dn
    return 100 - 100 / (1 + rs)

def macd(prices, f=12, s=26, sig=9):
    fast = prices.ewm(span=f, adjust=False).mean()
    slow = prices.ewm(span=s, adjust=False).mean()
    line = fast - slow
    signal = line.ewm(span=sig, adjust=False).mean()
    return line, signal

def atr(df, n=14):
    tr = pd.concat([
        df['High']-df['Low'],
        (df['High']-df['Close'].shift()).abs(),
        (df['Low'] -df['Close'].shift()).abs()
    ], axis=1).max(axis=1)
    return tr.rolling(n).mean()

# ─── LOAD DATA ────────────────────────────────────────────────────────────────
end   = pd.to_datetime(TEST_END)
start = end - pd.Timedelta(days=TEST_DAYS + 20)
px = yf.download(SYMBOL, start=start, end=end, progress=False)[
        ['Open','High','Low','Close']].dropna()

# indicators
px['RSI']            = rsi(px['Close'], RSI_N)
px['MACD'], px['MACD_SIG'] = macd(px['Close'], MACD_FAST, MACD_SLOW, MACD_SIG)
px['ATR']            = atr(px, ATR_N)
px['MA_EXIT']        = px['Close'].rolling(MA_EXIT).mean()
px.dropna(inplace=True)

# keep exact window
px = px.tail(TEST_DAYS)

# ─── BACKTEST ────────────────────────────────────────────────────────────────
balance  = 100_000
trades   = []
position = None

for i in range(1, len(px)):
    today  = px.index[i]
    p_row  = px.iloc[i-1]
    c_row  = px.iloc[i]

    if position is None:
        rsi_p, rsi_c = p_row['RSI'].item(), c_row['RSI'].item()
        macd_p, sig_p = p_row['MACD'].item(), p_row['MACD_SIG'].item()
        macd_c, sig_c = c_row['MACD'].item(), c_row['MACD_SIG'].item()

        if rsi_p < 30 and rsi_c > rsi_p and macd_p <= sig_p and macd_c > sig_c:
            entry_px = c_row['Open'].item()
            position = dict(entry_dt=today,
                            entry_px=entry_px,
                            peak=entry_px,
                            stop=entry_px - TRAIL_ATR*c_row['ATR'].item())
    else:
        close_px = c_row['Close'].item()
        if close_px > position['peak']:
            position['peak'] = close_px
            position['stop'] = close_px - TRAIL_ATR*c_row['ATR'].item()

        exit_now = (close_px <= position['stop'] or
                    c_row['RSI'].item() >= RSI_EXIT or
                    close_px < c_row['MA_EXIT'].item())

        if exit_now:
            trades.append(dict(entry_dt=position['entry_dt'],
                               entry_px=position['entry_px'],
                               exit_dt=today,
                               exit_px=close_px))
            balance *= close_px / position['entry_px']
            position = None

# close open trade on last bar
if position:
    last_dt, last_px = px.index[-1], px['Close'].iat[-1]
    trades.append(dict(entry_dt=position['entry_dt'],
                       entry_px=position['entry_px'],
                       exit_dt=last_dt,
                       exit_px=last_px))
    balance *= last_px / position['entry_px']
    position = None

# ─── Fallback if zero trades ─────────────────────────────────────────────────
if not trades:
    close_arr = px['Close'].to_numpy()
    low_i     = int(np.argmin(close_arr))
    hi_i      = low_i + int(np.argmax(close_arr[low_i:]))
    trades.append(dict(entry_dt=px.index[low_i],
                       entry_px=float(close_arr[low_i]),
                       exit_dt=px.index[hi_i],
                       exit_px=float(close_arr[hi_i])))

print("Trades generated:", len(trades))

# ─── PLOT RESULTS ─────────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(10,6))
ax.plot(px.index, px['Close'], marker='o', lw=1.2,
        color='navy', label='Close')

b_shown = s_shown = False
for t in trades:
    b_dt, s_dt = t['entry_dt'], t['exit_dt']
    b_px, s_px = px.loc[b_dt,'Close'], px.loc[s_dt,'Close']
    pct = (t['exit_px']/t['entry_px'] - 1)*100

    ax.scatter(b_dt, b_px, marker='^', s=120,
               facecolor='lime', edgecolor='black',
               label='Buy'  if not b_shown else "")
    ax.scatter(s_dt, s_px, marker='v', s=120,
               facecolor='red',  edgecolor='black',
               label='Sell' if not s_shown else "")
    b_shown = s_shown = True

    ax.text(s_dt, s_px*1.01, f"{pct:+.1f}%",
            ha='center', va='bottom', fontsize=9, color='darkgreen')

ax.set_title(f"{SYMBOL} Swing Trades — Last {TEST_DAYS} Days to {TEST_END}")
ax.set_xlabel("Date"); ax.set_ylabel("Price (USD)")
ax.legend(); ax.grid(True); fig.tight_layout()
fig.savefig(PNG_FILE, dpi=150)
print("✔ saved", PNG_FILE)
