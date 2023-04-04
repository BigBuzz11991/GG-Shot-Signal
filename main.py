import discord
from discord import Intents
import requests
import asyncio

# Bitquery API key
api_key = 'BQYk5AsQt2U3cENI4CoOqxXHLptg3hLR'

# Discord bot token and channel ID
TOKEN = 'MTA5MjI5NjM4OTQxMDcwNTQ1MQ.GoXscN.9WIwyHGQ5EhRTZ_tqAgEVZY3BwkIOE2VBhx1fA'
CHANNEL_ID = 1092300306391511101

# Discord client object
intents = Intents.all()
client = discord.Client(intents=intents)

# Bitquery API URL
url = 'https://graphql.bitquery.io/'

# Query to get live trading signals
query = '''
{
  ethereum {
    dexTrades(options: {limit: 1, desc: "timeInterval.minute"}) {
      buyCurrency {
        symbol
      }
      sellCurrency {
        symbol
      }
      buyAmount
      sellAmount
      timeInterval {
        minute(count: 5)
      }
    }
  }
}
'''

# Function to post trading signal to Discord channel
async def post_signal():
    # Make API request to Bitquery
    headers = {'X-API-KEY': api_key}
    response = requests.post(url, json={'query': query}, headers=headers)

    # Parse the response for signal information
    data = response.json()['data']['ethereum']['dexTrades'][0]
    coin = data['buyCurrency']['symbol']
    signal_type = 'Long' if data['buyAmount'] > data['sellAmount'] else 'Short'
    leverage_cross_amount = '10x'
    entry_targets = f'{data["sellAmount"]} - {data["buyAmount"]}'
    take_profit_targets = [f'{data["buyAmount"] * (1 + i / 100)}' for i in range(2, 18, 2)]
    stop_loss_amount = data['sellAmount'] * 0.95

    # Format the message and post to Discord channel
    message = f'{coin}\n{signal_type}\n{leverage_cross_amount}\n{entry_targets}\nTake Profit Targets (Top 8):\n'
    message += '\n'.join([f'{i+1}. {target}' for i, target in enumerate(take_profit_targets[:8])])
    message += f'\n\nStop Loss: {stop_loss_amount}'
    channel = client.get_channel(CHANNEL_ID)
    await channel.send(message)

# Event handler for when the bot is ready
@client.event
async def on_ready():
    print(f'Logged in as {client.user} (ID: {client.user.id})')

    # Wait for 5 minutes before posting the first signal
    await asyncio.sleep(5)

    # Post a trading signal immediately on startup
    await post_signal()

    # Schedule trading signals to be posted every hour
    while True:
        await asyncio.sleep(3600)  # Wait for an hour
        await post_signal()

# Start the bot
client.run(TOKEN)
