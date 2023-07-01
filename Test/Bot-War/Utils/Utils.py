
import time

import discord
from discord import app_commands
from discord.ext import commands
from discord.ui import Button

from Models.Alliance_Model import Alliance_Model


#empty space -> Cog_player, Cog_Alliance
#button alliance -> Cog_player, Cog_Alliance
#button details -> Cog_player
#has alliance -> Cog_player, Cog_Alliance
class Utils:
    bot: commands.Bot = None

    def __init__(self, bot: commands.Bot):
        self.bot = bot
                      
    def empty_space(self, left_word, right_word, width):
            it = 0
            empty_space = ""
            empty_space_length = width - len(right_word) - len(left_word)
            while it < empty_space_length:
                empty_space = empty_space + " "
                it += 1
            return empty_space
    
    def has_alliance(self, alliance: str):
        return_value: dict = {}
        alliance_state: list = ["Add","Adding"]
        button_style = discord.ButtonStyle.green
        alliance_db: dict = self.bot.db.get_one_alliance("name", alliance.upper())
        if alliance_db is not None:
            button_style = discord.ButtonStyle.blurple
            alliance_state: list = ["Update", "Updating"]
        return_value['alliance_state'] = alliance_state
        return_value['button_style'] = button_style
        return return_value
    
    def button_alliance(self, alliance, alliance_check: list, display):
        if alliance != None and alliance != "":
            button = Button(label = f"{alliance_check['alliance_state'][0]} Alliance", style=alliance_check['button_style'], emoji="🔒")       
            async def button_callback_alliance(interaction):
                button = Button(label = f"{alliance_check['alliance_state'][0]} Alliance ", style=discord.ButtonStyle.gray)
                display[1].clear_items()
                display[1].add_item(button)
                await interaction.response.edit_message(embed=display[0], view=display[1])
                if not self.bot.spec_role.admin_role(interaction.guild, interaction.user) and not self.bot.spec_role.assistant_role(interaction.guild, interaction.user):
                    await interaction.followup.send("You don't have the permission to use this command.")
                    return
                act_alliance: Alliance_Model = self.bot.db.get_one_alliance("name", alliance.upper())
                loading_message = await interaction.followup.send(f"> Loading the alliance... (started <t:{int(time.time())}:R>)")
                await self.bot.alliance.update_alliance(alliance.upper())
                await loading_message.edit(content="> Alliance Loaded ✅")
            button.callback = button_callback_alliance
            display[1].add_item(button)
        return display
    
    def button_details(self, display, field: list, no_alliance):
        button_details = Button(label = f"+", style=discord.ButtonStyle.blurple)      
        async def button_callback_more(interaction):
            button_details_2 = Button(label = f"-", style=discord.ButtonStyle.gray,  custom_id= "less")
            if no_alliance == True:
                display[1].remove_item(display[1].children[1])
            else:
                display[1].remove_item(display[1].children[2])
            display[1].add_item(button_details_2)
            display[0].add_field(name=field[1],value=field[2], inline=False)
            if no_alliance == False:
                display[0].add_field(name=field[3], value=field[4], inline=False)
            button_details_2.callback = button_callback_less
            await interaction.response.edit_message(embed=display[0], view=display[1])
        
        async def button_callback_less(interaction):
            button_details = Button(label = f"+", style=discord.ButtonStyle.blurple,  custom_id= "less")
            if no_alliance == True:
                display[1].remove_item(display[1].children[1])
            else:
                display[1].remove_item(display[1].children[2])
            display[1].add_item(button_details)
            display[0].clear_fields()
            button_details.callback = button_callback_more
            await interaction.response.edit_message(embed=display[0], view=display[1])
        button_details.callback = button_callback_more       
        display[1].add_item(button_details)
        return display