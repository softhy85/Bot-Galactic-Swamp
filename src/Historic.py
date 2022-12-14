import discord
from discord import File, Embed
from discord.ext import commands
import requests
from io import BytesIO
import os
from Image.Image import arrived_image, leave_image


class Historic(commands.Cog):
    historic_channel_id: int = None
    historic_channel: discord.TextChannel = None
    bot: commands.Bot = None

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.historic_channel_id = int(os.getenv("HISTORIC_CHANNEL"))
        self.historic_channel = bot.get_channel(self.historic_channel_id)

    @commands.Cog.listener()
    async def on_ready(self):
        print("Historic cog loaded.")

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        print(f"New member : {member.display_name}")
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
        print(f"Member leave : {member.display_name}")
        avatar: discord.User.avatar = member.avatar
        if avatar is None:
            avatar = member.display_avatar
        response = requests.get(avatar.url)
        return_image = leave_image(member.display_name, BytesIO(response.content))

        file = File(fp=return_image, filename=f'{member.display_name}.png')
        await self.historic_channel.send(file=file)
        embed: Embed = Embed(title=f'{member.display_name} a deserté !')
        await self.historic_channel.send(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(Historic(bot))