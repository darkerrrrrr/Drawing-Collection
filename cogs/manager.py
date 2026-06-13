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

    @commands.Cog.listener()
    async def on_ready(self):
        await self.bot.change_presence(activity=discord.Game(name="作:@darker_days (musuke)"))

    @app_commands.command(name="setup", description="必要なチャンネルを自動生成・同期します")
    async def setup(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        guild = interaction.guild

        # カテゴリーの取得または作成
        category_name = "お絵描きコレクション"
        category = discord.utils.get(guild.categories, name=category_name)
        if not category:
            category = await guild.create_category(category_name)

        for key, name in self.required_channels.items():
            existing = discord.utils.get(guild.text_channels, name=name)
            if not existing:
                overwrites = {}
                if key == "vault":
                    overwrites = {
                        guild.default_role: discord.PermissionOverwrite(read_messages=False),
                        guild.me: discord.PermissionOverwrite(
                            read_messages=True, 
                            send_messages=True, 
                            embed_links=True, 
                            attach_files=True
                        )
                    }
                await guild.create_text_channel(name, overwrites=overwrites, category=category)
            else:
                # 既存のチャンネルがカテゴリーに入っていない場合は移動させる
                if existing.category != category:
                    await existing.edit(category=category)
        
        await interaction.followup.send("✅ チャンネルの同期が完了しました。")

async def setup(bot):
    await bot.add_cog(Manager(bot))
