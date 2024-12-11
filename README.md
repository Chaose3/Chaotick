# 📈 Discord Stock Alert Bot




This bot sends daily stock signals and alerts based on technical indicators (RSI, SMA, and MACD) to a Discord channel. Built with `discord.py`, `yfinance`, and `APScheduler`.




## ⚙️ Features




- Daily stock signals posted automatically to a Discord channel.
- Supports basic technical analysis indicators (All are using the one-hour timeframe):
- **Moving Average Convergence Divergence (MACD)** crossover signals.
- **Relative Strength Index (RSI)** overbought/oversold signals.
- **Simple Moving Average (SMA)** crossover signals.
- Slash commands to check stock signals for specific tickers and to clear messages.




---








Clone the project




```bash
git clone https://github.com/Chaose3/Chaotick.git
```




Go to the project directory




```bash
cd StockAlert
```




Install dependencies, might need sudo permissions




```bash
pip install -r requirements.txt
```




Start the server




```bash
python3 app.py
```
## 🧩 Commands




- **`/stock <ticker>`**: Get real-time signals for a specified stock ticker (e.g., `/stock AAPL`).
- **`/clear <amount>`**: Clear the specified number of messages from the chat.




---chaose3 on discord or email me at chaose3@outlook.com
