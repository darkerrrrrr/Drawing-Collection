import discord
import asyncio
from discord.ext import commands

class Collection(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot: return
        if not message.attachments or message.channel.name != "イラスト投稿所":
            return

        vault_ch = discord.utils.get(message.guild.text_channels, name="保管庫")
        if not vault_ch: return

        vault_msg_ids = []
        for attachment in message.attachments:
            if not attachment.content_type or not attachment.content_type.startswith("image/"):
                continue
                
            # 画像をファイルとして取得（再アップロード用）
            file = await attachment.to_file()
            embed = discord.Embed(description=message.content or "No caption", color=discord.Color.blue())
            embed.set_author(name=message.author.display_name, icon_url=message.author.display_avatar.url)
            # アップロードするファイルをEmbedの画像として指定
            embed.set_image(url=f"attachment://{attachment.filename}")
            embed.set_footer(text=f"AuthorID: {message.author.id} | OriginalMsgID: {message.id}")
            
            # ファイルとEmbedをセットで送信
            vault_msg = await vault_ch.send(file=file, embed=embed)
            vault_msg_ids.append(vault_msg.id)

        if vault_msg_ids:
            # 3秒間だけメッセージを残して、ユーザーが送信を確認できるようにする
            await asyncio.sleep(3)
            # 元のメッセージを削除して「保管庫に移動した」状態にする
            try:
                await message.delete()
            except discord.Forbidden:
                print(f"Error: メッセージを削除する権限がありません（{message.channel.name}）")
            except discord.NotFound:
                print(f"Notice: メッセージが既に削除されています")
            print(f"Moved drawing from {message.author.display_name} to Vault")

async def setup(bot):
    await bot.add_cog(Collection(bot))
