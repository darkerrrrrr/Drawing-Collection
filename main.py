import discord
import asyncio
from discord.ext import commands
import os
from dotenv import load_dotenv

load_dotenv()

class DrawingBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        # Cogsの読み込み
        for filename in os.listdir('./cogs'):
            if filename.endswith('.py'):
                await self.load_extension(f'cogs.{filename[:-3]}')
        await self.tree.sync()
        asyncio.create_task(self.shutdown_timer())
        print("Bot is ready and commands synced.")

    async def shutdown_timer(self):
        # 6時間 (21600秒) 経過後にボットを終了させる
        await asyncio.sleep(21600)
        print("6 hours passed. Shutting down...")
        await self.close()

bot = DrawingBot()

if __name__ == "__main__":
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        print("Error: DISCORD_TOKEN environment variable is not set.")
        print("Please ensure you have added it to GitHub Secrets or your .env file.")
        exit(1)
    
    bot.run(token)
