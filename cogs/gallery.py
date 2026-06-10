import discord
from discord import app_commands, ui
from discord.ext import commands
import random

class GalleryView(ui.View):
    def __init__(self, messages: list[discord.Message], user_id: int):
        super().__init__(timeout=120)
        self.data_list = messages
        self.index = 0
        self.user_id = user_id

    def make_embed(self):
        return self.data_list[self.index].embeds[0]

    @ui.button(label="◀ 前へ", style=discord.ButtonStyle.gray)
    async def prev(self, interaction: discord.Interaction, button: ui.Button):
        self.index = (self.index - 1) % len(self.data_list)
        await interaction.response.edit_message(embed=self.make_embed())

    @ui.button(label="次へ ▶", style=discord.ButtonStyle.gray)
    async def next(self, interaction: discord.Interaction, button: ui.Button):
        self.index = (self.index + 1) % len(self.data_list)
        await interaction.response.edit_message(embed=self.make_embed())

    @ui.button(label="🗑️ 削除", style=discord.ButtonStyle.danger)
    async def delete_entry(self, interaction: discord.Interaction, button: ui.Button):
        msg = self.data_list[self.index]
        if f"AuthorID: {interaction.user.id}" not in msg.embeds[0].footer.text:
            return await interaction.response.send_message("自分の作品以外は削除できません。", ephemeral=True)

        # 保管庫から削除。OriginalMsgIDが同じものは一括削除
        orig_id_str = msg.embeds[0].footer.text.split("|")[-1].strip()
        vault_ch = msg.channel
        async for m in vault_ch.history(limit=100):
            if m.embeds and orig_id_str in m.embeds[0].footer.text:
                await m.delete()
        
        await interaction.response.edit_message(content="✅ この作品をコレクションから削除しました。", embed=None, view=None)
        self.stop()

    @ui.button(label="閉じる", style=discord.ButtonStyle.secondary)
    async def close_gallery(self, interaction: discord.Interaction, button: ui.Button):
        await interaction.response.edit_message(content="ギャラリーを閉じました。", embed=None, view=None)
        self.stop()

class ShowView(ui.View):
    def __init__(self, messages: list[discord.Message], user_id: int):
        super().__init__(timeout=60)
        self.data_list = messages
        self.user_id = user_id

    def make_embed(self):
        return random.choice(self.data_list).embeds[0]

    @ui.button(label="もう一度引く 🎲", style=discord.ButtonStyle.primary)
    async def reroll(self, interaction: discord.Interaction, button: ui.Button):
        await interaction.response.edit_message(embed=self.make_embed(), view=self)


class Gallery(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def channel_check(self, interaction, name):
        if interaction.channel.name != name:
            await interaction.response.send_message(f"❌ このコマンドは `{name}` で実行してください。", ephemeral=True)
            return False
        return True

    @app_commands.command(name="show", description="自分の作品からランダム表示")
    async def show(self, interaction: discord.Interaction):
        if not await self.channel_check(interaction, "マイギャラリー"): return
        vault_ch = discord.utils.get(interaction.guild.text_channels, name="保管庫")
        if not vault_ch:
            return await interaction.response.send_message("❌ 保管庫チャンネルが見つかりません。先に `/setup` を実行してください。", ephemeral=True)

        my_works = [m async for m in vault_ch.history(limit=500) if m.embeds and f"AuthorID: {interaction.user.id}" in m.embeds[0].footer.text]
        if not my_works: return await interaction.response.send_message("作品がありません。")
        
        entry = random.choice(my_works)
        await interaction.response.send_message(embed=entry.embeds[0], view=ShowView(my_works, interaction.user.id))

    @app_commands.command(name="gallery", description="自分のギャラリーを表示")
    async def gallery(self, interaction: discord.Interaction):
        if not await self.channel_check(interaction, "マイギャラリー"): return
        vault_ch = discord.utils.get(interaction.guild.text_channels, name="保管庫")
        if not vault_ch:
            return await interaction.response.send_message("❌ 保管庫チャンネルが見つかりません。先に `/setup` を実行してください。", ephemeral=True)

        my_works = [m async for m in vault_ch.history(limit=500) if m.embeds and f"AuthorID: {interaction.user.id}" in m.embeds[0].footer.text]
        if not my_works: return await interaction.response.send_message("作品がありません。")

        view = GalleryView(my_works, interaction.user.id)
        await interaction.response.send_message(embed=view.make_embed(), view=view)

    @app_commands.command(name="search", description="全体から検索")
    async def search(self, interaction: discord.Interaction, user: discord.Member = None, keyword: str = None):
        if not await self.channel_check(interaction, "全体ギャラリー"): return
        
        await interaction.response.defer() # 処理に時間がかかることを伝えるアクション
        vault_ch = discord.utils.get(interaction.guild.text_channels, name="保管庫")
        if not vault_ch:
            return await interaction.followup.send("❌ 保管庫チャンネルが見つかりません。先に `/setup` を実行してください。")

        results = []
        async for m in vault_ch.history(limit=500):
            if not m.embeds: continue
            embed = m.embeds[0]
            if user and f"AuthorID: {user.id}" not in embed.footer.text: continue
            if keyword and keyword not in (embed.description or ""): continue
            results.append(m)

        if not results: return await interaction.followup.send("見つかりませんでした。")
        view = GalleryView(results, interaction.user.id)
        await interaction.followup.send(embed=view.make_embed(), view=view)

async def setup(bot):
    await bot.add_cog(Gallery(bot))
