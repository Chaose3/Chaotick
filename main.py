import discord
import os
import yfinance as yf
from discord import app_commands

# Load token from environment variables
TOKEN = os.getenv("DISCORD_TOKEN")

# Check if the token exists
if not TOKEN:
    raise ValueError("No DISCORD_TOKEN found in environment variables")

# Set up bot intents and client
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
bot = discord.Client(intents=intents)
tree = app_commands.CommandTree(bot)


# Function to calculate MACD
def get_macd_signal(ticker):
    # Fetch stock data (1 month, 1 hour interval)
    data = yf.download(ticker, period="1mo", interval="1h")

    # Ensure we have enough data
    if data.empty or len(data) < 26:
        return None, None

    # Calculate MACD
    short_ema = data['Close'].ewm(span=12, adjust=False).mean()
    long_ema = data['Close'].ewm(span=26, adjust=False).mean()
    macd = short_ema - long_ema
    signal_line = macd.ewm(span=9, adjust=False).mean()

    # Extract the last values as scalars
    if not macd.empty and not signal_line.empty:
        macd_value = macd.iloc[-1].item()  # Convert to scalar using .item()
        signal_value = signal_line.iloc[-1].item()  # Convert to scalar using .item()
        return macd_value, signal_value
    else:
        return None, None


# Command for stock analysis
@tree.command(name="stock", description="Get stock MACD signals for a ticker")
async def stock_command(interaction: discord.Interaction, ticker: str):
    # Get MACD values
    macd, signal = get_macd_signal(ticker)

    # Check if data is available
    if macd is None or signal is None:
        await interaction.response.send_message(f"Could not fetch enough data for {ticker}. Try again later.")
        return

    # Compare MACD and Signal values
    try:
        if macd > signal:
            macd_signal = "Buy (Bullish crossover)"
        elif macd < signal:
            macd_signal = "Sell (Bearish crossover)"
        else:
            macd_signal = "Neutral"
    except ValueError as e:
        await interaction.response.send_message(f"Error comparing MACD and Signal values: {e}")
        return

    # Response message with analysis
    response_message = (
        f"**Stock: {ticker}**\n"
        f"MACD: {macd:.2f} - Signal Line: {signal:.2f} - Signal: {macd_signal}"
    )

    # Send response to Discord
    await interaction.response.send_message(response_message)


# Event to sync commands when bot is ready
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    await tree.sync()


# Run the bot
bot.run(TOKEN)
