import discord 
import datetime
import time
from dotenv import load_dotenv
from discord.ext import commands
from models.Alliance_Model import Alliance_Model
from models.Player_Model import Player_Model
from models.War_Model import War_Model
from models.Colony_Model import Colony_Model
from src.DataBase import DataBase
from typing import List

from enum import Enum

load_dotenv()
token: str = os.getenv("BOT_TOKEN")
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
db = DataBase()
bot: commands.Bot = commands.Bot(command_prefix=".", intents=intents, application_id=os.getenv("APP_ID"), allowed_mentions = discord.AllowedMentions(everyone = True))

client=commands.Bot(command_prefix=commands.when_mentioned_or("."))

def convert_to_unix_time(date: datetime.datetime) -> str:
    return f'<t:{int(time.mktime(date.timetuple()))}:R>'

class Emoji(Enum):
    SB: str = "🌎"
    colo: str = "🪐"
    down: str = "💥"

class Select(discord.ui.Select):
    def __init__(self, player: Player_Model, colonies: List[Colony_Model]):
        it: int = 1
        player_drop_down: List[discord.SelectOption] = []
        
        player_drop_down.append(discord.SelectOption(label = f"Niveau {player['lvl']} : {player['pseudo']} ➖➖➖➖➖➖➖➖ ", emoji = "💫",description = "", value = it, defaut = True))
        it += 1
        if Player_Model.SB_status == "Down" :
            menu_label = f"Base Principale (Retour {convert_to_unix_time(player['SB_refresh_time'])})"
            menu_emoji = Emoji.down
        else :
            menu_label = "Base Principale"
            menu_emoji = Emoji.SB
        
        player_drop_down.append(discord.SelectOption(label = menu_label, emoji = menu_emoji, description = f"SB ({player['SB_lvl']})", value = it))
        it += 1
                
        for colony in colonies:
            menu_description = f"{colony['colo_coord']['x']} {colony['colo_coord']['y']} SB ({colony['colo_lvl']})"
            if Colony_Model.colo_status == "Down" :
                menu_label = f"{colony['colo_sys_name']} (Retour {convert_to_unix_time(colony['colo_refresh_time'])})"
                menu_emoji = Emoji.down
                
            else :
                menu_label = f"{colony['colo_sys_name']}"
                menu_emoji = Emoji.colo
                
            player_drop_down.append(discord.SelectOption(label = menu_label, emoji = menu_emoji, description = menu_description, value = it))
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
    def __init__(self, bot, timeout = 180):
        super().__init__(timeout=timeout)
        actual_war: War_Model = bot.db.get_one_war("status", "InProgress")
        if actual_war is None:
            return -1
        players: List[Player_Model] = bot.db.get_players("_id", actual_war["_alliance_id"])
        for player in players:
            colonies: List[Colony_Model] = bot.db.get_colonies("_id", player["_id"])
            self.add_item(Select(player, colonies))

@bot.command()
async def menu(ctx):
    await ctx.send("Menus!",view=SelectView())



bot.db = db
bot.spec_role = Role()

bot.run(token)