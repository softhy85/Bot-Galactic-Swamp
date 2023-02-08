import discord 
import datetime
import time
import os
from dotenv import load_dotenv
from discord.ext import commands
from models.Player_Model import Player_Model
from models.War_Model import War_Model
from models.Colony_Model import Colony_Model
from src.DataBase import DataBase
from typing import List
from pymongo.cursor import Cursor

from enum import Enum

load_dotenv()
token: str = os.getenv("BOT_TOKEN")
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
db = DataBase()
bot: commands.Bot = commands.Bot(command_prefix=".", intents=intents, application_id=os.getenv("APP_ID"), allowed_mentions = discord.AllowedMentions(everyone = True))
bot.db = db

def convert_to_unix_time(date: datetime.datetime) -> str:
    return f'<t:{int(time.mktime(date.timetuple()))}:R>'

class Emoji(Enum):
    SB: str = "🌎"
    colo: str = "🪐"
    down: str = "💥"

class Select(discord.ui.Select):
    def __init__(self, player: Player_Model, colonies: Cursor[Colony_Model]):
        it: int = 1
        player_drop_down: List[discord.SelectOption] = []
        menu_label: str = f"Niveau {player['lvl']} : {player['pseudo']}"
        menu_label += " " + Emoji.down.value if player["MB_status"] == "Down" else " " + Emoji.SB.value
        for colony in colonies:
           menu_label += Emoji.down.value if colony["colo_status"] == "Down" else Emoji.colo.value
        colonies.rewind()
        player_drop_down.append(discord.SelectOption(label = menu_label, emoji = "💫",description = "", value = str(it), default = True))
        it += 1
        if player["MB_status"] == "Down" :
            menu_label = "Base Principale"
            menu_description = f"SB ({player['MB_lvl']}) (Retour {convert_to_unix_time(player['SB_refresh_time'])})"
            menu_emoji = Emoji.down.value
        else :
            menu_label = "Base Principale"
            menu_description = f"SB ({player['MB_lvl']})"
            menu_emoji = Emoji.SB.value

        player_drop_down.append(discord.SelectOption(label = menu_label, emoji = menu_emoji, description = menu_description, value = str(it)))
        it += 1
        for colony in colonies:
            if colony["colo_status"] == "Down" :
                menu_label = f"{colony['colo_sys_name']}"
                menu_description = f"({colony['colo_coord']['x']} ; {colony['colo_coord']['y']}) - SB ({colony['colo_lvl']}) (Retour {convert_to_unix_time(colony['colo_refresh_time'])})"
                menu_emoji = Emoji.down.value
            else :
                menu_label = f"{colony['colo_sys_name']}"
                menu_description = f"({colony['colo_coord']['x']} ; {colony['colo_coord']['y']}) - SB ({colony['colo_lvl']})"
                menu_emoji = Emoji.colo.value
                
            player_drop_down.append(discord.SelectOption(label = menu_label, emoji = menu_emoji, description = menu_description, value = str(it)))
            it += 1

        options = player_drop_down
        super().__init__(placeholder="Select an option",max_values=1,min_values=1,options=options)


#    async def callback(self, interaction: discord.Interaction):
#        if self.values[0] == "Option 1":
#            await interaction.response.edit_message(content="This is the first option from the entire list!")
#        elif self.values[0] == "Option 2":
#            await interaction.response.send_message("This is the second option from the list entire wooo!",ephemeral=False)
#        elif self.values[0] == "Option 3":
#            await interaction.response.send_message("Third One!",ephemeral=True)

class SelectView(discord.ui.View):
    error: bool = False
    def __init__(self, bot, timeout = 180):
        super().__init__(timeout=timeout)
        actual_war: War_Model = bot.db.get_one_war("status", "InProgress")
        if actual_war is None:
            self.error = True
            return
        obj: dict = {"_alliance_id", actual_war["_alliance_id"]}
        players: List[Player_Model] = bot.db.get_players(obj)
        for player in players:
            colonies: List[Colony_Model] = bot.db.get_colonies({"_player_id", player["_id"]})
            self.add_item(Select(player, colonies))

@bot.command()
async def menu(ctx):
    view: SelectView = SelectView(bot)
    if view.error:
        await ctx.send("No wars in progress")
    else:
        await ctx.send("Menus!", view=view)

bot.run(token)