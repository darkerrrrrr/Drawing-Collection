import discord
from discord import app_commands
from discord.ext import commands

class Manager(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.required_channels = {
            "post": "イラスト投稿所",
            "my_gallery": "マイギャラリー",
            "all_gallery": "全体ギャラリー",
            "vault": "保管庫"
        }

    @app_commands.command(name="setup", description="必要なチャンネルを自動生成・同期します")
    async def setup(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        guild = interaction.guild

        for key, name in self.required_channels.items():
            existing = discord.utils.get(guild.text_channels, name=name)
            if not existing:
                overwrites = {}
                if key == "vault":
                    overwrites = {
                        guild.default_role: discord.PermissionOverwrite(read_messages=False),
                        guild.me: discord.PermissionOverwrite(read_messages=True)
                    }
                existing = await guild.create_text_channel(name, overwrites=overwrites)
        
        await interaction.followup.send("✅ チャンネルの同期が完了しました。")

async def setup(bot):
    await bot.add_cog(Manager(bot))
