import discord
from discord.ext import commands

class Collection(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot: return
        if message.channel.name != "イラスト投稿所" or not message.attachments:
            return

        vault_ch = discord.utils.get(message.guild.text_channels, name="保管庫")
        if not vault_ch: return

        vault_msg_ids = []
        for attachment in message.attachments:
            if not attachment.content_type or not attachment.content_type.startswith("image/"):
                continue
                
            embed = discord.Embed(description=message.content or "No caption", color=discord.Color.blue())
            embed.set_author(name=message.author.display_name, icon_url=message.author.display_avatar.url)
            embed.set_image(url=attachment.url)
            embed.set_footer(text=f"AuthorID: {message.author.id} | OriginalMsgID: {message.id}")
            
            vault_msg = await vault_ch.send(embed=embed)
            vault_msg_ids.append(vault_msg.id)

        if vault_msg_ids:
            # 保存完了の合図としてリアクションを追加
            await message.add_reaction("✅")
            print(f"Archived drawing from {message.author.display_name}")

    @commands.Cog.listener()
    async def on_raw_message_delete(self, payload):
        guild = self.bot.get_guild(payload.guild_id)
        if not guild: return
        vault_ch = discord.utils.get(guild.text_channels, name="保管庫")
        if not vault_ch: return

        async for msg in vault_ch.history(limit=500):
            if msg.embeds and f"OriginalMsgID: {payload.message_id}" in msg.embeds[0].footer.text:
                await msg.delete()

async def setup(bot):
    await bot.add_cog(Collection(bot))
