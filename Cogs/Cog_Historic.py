import discord
from discord import File, Embed
from discord.ext import commands
import requests
from io import BytesIO
import os
from Image.Image import arrived_image, leave_image


class Cog_Historic(commands.Cog):
    bot: commands.Bot = None
    historic_channel_id: int = None
    historic_channel: discord.abc.GuildChannel | discord.Thread | discord.abc.PrivateChannel | None = None

    def __init__(self, bot: commands.Bot):
        super().__init__()
        self.bot = bot
        self.historic_channel_id = int(os.getenv("HISTORIC_CHANNEL"))
        self.historic_channel = bot.get_channel(self.historic_channel_id)

    #<editor-fold desc="listener">

    @commands.Cog.listener()
    async def on_ready(self):
        print("Cog Loaded: Cog_Historic")

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        print(f"Info: New member - {member.display_name}")
        avatar: discord.User.avatar = member.avatar
        if avatar is None:
            avatar = member.display_avatar
        response = requests.get(avatar.url)
        return_image = arrived_image(member.display_name, BytesIO(response.content))

        file = File(fp=return_image, filename=f'{member.display_name}.png')
        await self.historic_channel.send(file=file)
        embed: Embed = Embed(title=f'{member.display_name} a rejoint nos rangs !')
        await self.historic_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        print(f"Info: Member leave - {member.display_name}")
        avatar: discord.User.avatar = member.avatar
        if avatar is None:
            avatar = member.display_avatar
        response = requests.get(avatar.url)
        return_image = leave_image(member.display_name, BytesIO(response.content))

        file = File(fp=return_image, filename=f'{member.display_name}.png')
        await self.historic_channel.send(file=file)
        embed: Embed = Embed(title=f'{member.display_name} a déserté !')
        await self.historic_channel.send(embed=embed)

    #</editor-fold>

async def setup(bot: commands.Bot):
    await bot.add_cog(Cog_Historic(bot))