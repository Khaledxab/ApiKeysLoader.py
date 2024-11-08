import os
import discord
from discord.ext import commands, tasks
import aiohttp
import datetime
from dotenv import load_dotenv

load_dotenv()

API_URL = os.getenv('STATS_API')
BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')


intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

API_URL = os.getenv('STATS_API')
REFRESH_INTERVAL = 300

async def fetch_api_stats():
    """Fetch statistics from the API"""
    print(f"Fetching stats from {API_URL}")

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get("http://flask_api:5000/api/stats") as response:
                if response.status == 200:
                    return await response.json()
                return None
        except Exception as e:
            print(f"Error fetching stats: {e}")
            return None

def create_stats_embed(stats):
    """Create a Discord embed with the API statistics"""
    embed = discord.Embed(
        title="API Statistics Dashboard",
        color=discord.Color.blue(),
        timestamp=datetime.datetime.now()
    )
    
    plant_keys = stats['keys']['plantid']['keys_available']
    health_keys = stats['keys']['healthid']['keys_available']
    
    embed.add_field(
        name="🌱 Plant ID Keys",
        value=f"Available: {plant_keys}\nStatus: {stats['keys']['plantid']['status']}",
        inline=True
    )
    
    embed.add_field(
        name="❤️ Health ID Keys",
        value=f"Available: {health_keys}\nStatus: {stats['keys']['healthid']['status']}",
        inline=True
    )
    
    embed.add_field(
        name="🔄 Requests Until Rotation",
        value=f"Plant ID: {stats['requests']['plantid']['requests_until_rotation']}\n"
              f"Health ID: {stats['requests']['healthid']['requests_until_rotation']}",
        inline=False
    )
    
    embed.set_footer(text="Last Updated")
    return embed

@bot.event
async def on_ready():
    print(f'Bot is ready! Logged in as {bot.user.name}')
    update_stats.start()

@bot.command(name='stats')
async def show_stats(ctx):
    """Command to show current API statistics"""
    stats = await fetch_api_stats()
    if stats:
        embed = create_stats_embed(stats)
        await ctx.send(embed=embed)
    else:
        await ctx.send("❌ Unable to fetch API statistics. Please try again later.")

@tasks.loop(seconds=REFRESH_INTERVAL)
async def update_stats():
    """Background task to update statistics periodically"""
    stats = await fetch_api_stats()
    if stats:
        plant_keys = stats['keys']['plantid']['keys_available']
        health_keys = stats['keys']['healthid']['keys_available']
        await bot.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name=f"🌱 {plant_keys} Plant | ❤️ {health_keys} Health"
            )
        )

def run_bot(token):
    bot.run(token)

if __name__ == "__main__":
    BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')
    run_bot(BOT_TOKEN)