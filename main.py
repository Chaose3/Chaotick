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


def get_rsi_signal(ticker):
    data = yf.download(ticker, period="1mo", interval="1h")
    if data.empty or len(data) < 14:   # This is the duration of the RSI calculation
        return None
    delta = data['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1+rs))
    if not rsi.empty:
        return rsi.iloc[-1].item()
    else:
        return None


def get_ma_crossover_signal(ticker):
    # Fetch the stock data (1 month, 1 hour interval)
    data = yf.download(ticker, period="1mo", interval="1h")

    if data.empty:
        return None

    # Calculate the long-term and short-term moving averages, you can change the window variables as desired
    data['Short_MA'] = data['Close'].rolling(window=9).mean()  # 9-Period MA
    data['Long_MA'] = data['Close'].rolling(window=21).mean()  # 21-Period MA

    # Drop rows with NaN values
    data = data.dropna()

    # Ensure there is enough data for MAs
    if len(data.dropna()) < 2:
        return None

    # Get 2 variables for comparison
    short_ma_current = data['Short_MA'].iloc[-1]
    short_ma_previous = data['Short_MA'].iloc[-2]
    long_ma_current = data['Long_MA'].iloc[-1]
    long_ma_previous = data['Long_MA'].iloc[-2]

    # Check for a crossover
    if short_ma_previous <= long_ma_previous and short_ma_current > long_ma_current:
        return "Buy (Bullish crossover"
    elif short_ma_previous >= long_ma_previous and short_ma_current < long_ma_current:
        return "Sell (Bearish crossover"
    else:
        return "No crossover"


# Command for stock analysis
@tree.command(name="stock", description="Calculate long and short signals based on technical indicators")
async def stock_command(interaction: discord.Interaction, ticker: str):
    # Get MACD values
    macd, signal = get_macd_signal(ticker)

    # Get RSI values
    rsi = get_rsi_signal(ticker)

    # Get MA values
    ma_signal = get_ma_crossover_signal(ticker)

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

    if rsi > 70:
        rsi_signal = "Overbought (Consider selling)"
    elif rsi < 30:
        rsi_signal = "Oversold (Consider buying"
    else:
        rsi_signal = "Neutral"


    # Check if MA Crossover Data is availible
    if ma_signal is None:
        await interaction.response.send_message(f"Could not fetch enough data for {ticker} (MA Crossover).", ephemeral=True)
    # Response message with analysis
    response_message = (
        f"**Stock: {ticker}**\n"
        f"MACD: {macd:.2f} - Signal Line: {signal:.2f} - Signal: {macd_signal}\n"
        f"RSI: {rsi:.2f} - Signal: {rsi_signal}\n"
        f"Ma Crossover: {ma_signal}"
    )

    # Send response to Discord
    await interaction.response.send_message(response_message)


@tree.command(name="clear", description="Clear messages from the chat")
async def clear(ctx, amount: int):
    """Clears a specified number of messages."""
    if amount <= 0:
        await ctx.respond("Please specify a number greater than 0.", ephemeral=True)
        return

    try:
        # Bulk delete messages
        deleted = await ctx.channel.purge(limit=amount + 1)  # +1 includes the command message
        await ctx.respond(f"Cleared {len(deleted) - 1} messages!", ephemeral=True)  # Exclude the command message itself
    except discord.HTTPException as e:
        if "rate limited" in str(e).lower():
            await ctx.respond("The bot is being rate-limited. Please wait and try again later.", ephemeral=True)
        else:
            await ctx.respond(f"An error occurred: {e}", ephemeral=True)
    except Exception as e:
        await ctx.respond(f"An unexpected error occurred: {e}", ephemeral=True)


# Event to sync commands when bot is ready
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    await tree.sync()


# Run the bot
bot.run(TOKEN)
