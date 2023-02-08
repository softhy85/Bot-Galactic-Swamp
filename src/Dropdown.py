import discord
from discord.ext import commands
import datetime
import time
from models.Player_Model import Player_Model
from models.Colony_Model import Colony_Model
from typing import List
from pymongo.cursor import Cursor
from models.Emoji import Emoji


def convert_to_unix_time(date: datetime.datetime) -> str:
    return f'<t:{int(time.mktime(date.timetuple()))}:R>'


class Select(discord.ui.Select):
    def __init__(self, player: Player_Model, colonies: Cursor[Colony_Model]):
        it: int = 1
        act_date: datetime.datetime = datetime.datetime.now()
        act_five_date: datetime.datetime = act_date + datetime.timedelta(minutes=5)
        act_fifteen_date: datetime.datetime = act_date + datetime.timedelta(minutes=15)
        act_thirty_date: datetime.datetime = act_date + datetime.timedelta(minutes=30)
        act_forty_five_date: datetime.datetime = act_date + datetime.timedelta(minutes=45)
        player_drop_down: List[discord.SelectOption] = []
        menu_label: str = f"Niveau {player['lvl']} : {player['pseudo']}"
        menu_label += " " + Emoji.down.value if player["MB_status"] == "Down" else " " + Emoji.SB.value
        for colony in colonies:
            menu_label += Emoji.down.value if colony["colo_status"] == "Down" else Emoji.colo.value
        colonies.rewind()
        player_drop_down.append(discord.SelectOption(label = menu_label, emoji = "💫",description = "", value = str(it), default = True))
        it += 1
        if player["MB_status"] == "Down":
            MB_refresh_date: datetime.datetime = player['MB_refresh_time']
            if MB_refresh_date.date() == act_date.date() and MB_refresh_date.time() > act_date.time():
                if MB_refresh_date < act_five_date:
                    menu_emoji = Emoji.five_min.value
                elif MB_refresh_date < act_fifteen_date:
                    menu_emoji = Emoji.fifteen_min.value
                elif MB_refresh_date < act_thirty_date:
                    menu_emoji = Emoji.thirty_min.value
                elif MB_refresh_date < act_forty_five_date:
                    menu_emoji = Emoji.forty_five_min.value
                else:
                    menu_emoji = Emoji.down.value
            else:
                menu_emoji = Emoji.down.value
            menu_label = "Base Principale"
            menu_description = f"SB ({player['MB_lvl']}) (Retour {convert_to_unix_time(player['MB_refresh_time'])})"
        else :
            menu_label = "Base Principale"
            menu_description = f"SB ({player['MB_lvl']})"
            menu_emoji = Emoji.SB.value

        player_drop_down.append(discord.SelectOption(label = menu_label, emoji = menu_emoji, description = menu_description, value = str(it)))
        it += 1
        for colony in colonies:
            if colony["colo_status"] == "Down" :
                colo_refresh_date: datetime.datetime = player['MB_refresh_time']
                if colo_refresh_date.date() == act_date.date() and colo_refresh_date.time() > act_date.time():
                    if colo_refresh_date < act_five_date:
                        menu_emoji = Emoji.five_min.value
                    elif colo_refresh_date < act_fifteen_date:
                        menu_emoji = Emoji.fifteen_min.value
                    elif colo_refresh_date < act_thirty_date:
                        menu_emoji = Emoji.thirty_min.value
                    elif colo_refresh_date < act_forty_five_date:
                        menu_emoji = Emoji.forty_five_min.value
                    else:
                        menu_emoji = Emoji.down.value
                else:
                    menu_emoji = Emoji.down.value
                menu_label = f"{colony['colo_sys_name']}"
                menu_description = f"({colony['colo_coord']['x']} ; {colony['colo_coord']['y']}) - SB ({colony['colo_lvl']}) (Retour {convert_to_unix_time(colony['colo_refresh_time'])})"
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

class DropView(discord.ui.View):
    error: bool = False
    def __init__(self, bot: commands.Bot, players: Cursor[Player_Model], timeout: int = 180):
        super().__init__(timeout=timeout)
        for player in players:
            obj: dict = {"_player_id", player["_id"]}
            colonies: List[Colony_Model] = bot.db.get_colonies(obj)
            self.add_item(Select(player, colonies))
