import discord
from discord.ext import commands
import datetime
import time
from models.Player_Model import Player_Model
from models.Colony_Model import Colony_Model
from typing import List
from pymongo.cursor import Cursor
from bson.objectid import ObjectId
from models.Emoji import Emoji
import os


class Select(discord.ui.Select):
    bot: commands.Bot
    log_channel_id: int = None
    log_channel: discord.abc.GuildChannel | discord.Thread | discord.abc.PrivateChannel | None = None

    def __init__(self, bot: commands.Bot, player: Player_Model, colonies: List[Colony_Model]) -> None:
        self.bot = bot
        it: int = 1
        self.log_channel_id: int = int(os.getenv("LOG_CHANNEL"))
        self.log_channel = self.bot.get_channel(self.log_channel_id)
        act_date: datetime.datetime = datetime.datetime.now()
        act_five_date: datetime.datetime = act_date + datetime.timedelta(minutes=5)
        act_fifteen_date: datetime.datetime = act_date + datetime.timedelta(minutes=15)
        act_thirty_date: datetime.datetime = act_date + datetime.timedelta(minutes=30)
        act_forty_five_date: datetime.datetime = act_date + datetime.timedelta(minutes=45)
        player_drop_down: List[discord.SelectOption] = []
        status_emoji: str = Emoji.offline.value
        if player["player_online"]:
            status_emoji = Emoji.online.value 
        menu_label: str = f"Niv {player['lvl'] if player['lvl'] != -1 else 'Non connue'} : {player['pseudo']}"
        menu_label += " " + Emoji.down.value if player["MB_status"] == "Down" else " " + Emoji.SB.value
        #modification pour mettre les colos non complétées
        #if colony["updated"] == True:
        for colony in colonies:
            menu_label += Emoji.down.value if colony["colo_status"] == "Down" else Emoji.colo.value
        #else:
               # menu_label += Emoji.colo_empty.value
        player_drop_down.append(discord.SelectOption(label = menu_label, emoji = status_emoji ,description = "", value = "", default = True))
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
            date_refresh: datetime.datetime = player['MB_refresh_time']
            menu_description = f"SB ({player['MB_lvl']}) (Retour {date_refresh.strftime('%m/%d/%Y, %H:%M:%S')})"
        else :
            menu_label = "Base Principale"
            menu_description = f"SB ({player['MB_lvl']})"
            menu_emoji = Emoji.SB.value
        print("OK 7")
        player_drop_down.append(discord.SelectOption(label = menu_label, emoji = menu_emoji, description = menu_description, value = str(it) + ";" + "player" + ";" + str(player["_id"])))
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
                date_refresh: datetime.datetime = colony['colo_refresh_time']
                menu_description = f"({colony['colo_coord']['x']} ; {colony['colo_coord']['y']}) - SB ({colony['colo_lvl']}) (Retour {date_refresh.strftime('%m/%d/%Y, %H:%M:%S')})"
            else :
                menu_label = f"{colony['colo_sys_name']}"
                menu_description = f"({colony['colo_coord']['x']} ; {colony['colo_coord']['y']}) - SB ({colony['colo_lvl']})"
                menu_emoji = Emoji.colo.value
            player_drop_down.append(discord.SelectOption(label = menu_label, emoji = menu_emoji, description = menu_description, value = str(it) + ";" + "colony" + ";" + str(colony["_id"])))
            it += 1
        menu_label = "Reset"
        menu_emoji = Emoji.Reset.value
        player_drop_down.append(discord.SelectOption(label = menu_label, emoji = menu_emoji, description = '', value = "Reset;" + str(player["_id"])))
        options = player_drop_down
        super().__init__(placeholder="Select an option", max_values=1, min_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        if self.values[0] == "":
            return
        date: datetime.datetime = datetime.datetime.now()
        date_resfresh: datetime.datetime = date + datetime.timedelta(hours=5.0)
        values: List[str] = self.values[0].split(";")
        self.values[0] = ""
        if len(values) == 2 and values[0] == "Reset":
            player: Player_Model = self.bot.db.get_one_player("_id", ObjectId(values[1]))
            if player is None:
                await interaction.response.send_message(f"Something goes wrong while updating the database.\nPlease report this bug to Softy.")
                await self.bot.dashboard.update_Dashboard()
                return
            player["MB_refresh_time"] = date
            player["MB_last_attack_time"] = date
            player["MB_status"] = "Up"
            self.bot.db.update_player(player)
            obj: dict = {"_player_id": values[1]}
            colonies: List[Colony_Model] = list(self.bot.db.get_colonies(obj))
            for colony in colonies:
                colony["colo_refresh_time"] = date
                colony["colo_last_attack_time"] = date
                colony["colo_status"] = "Up"
                self.bot.db.update_colony(colony)
            await self.log_channel.send(f"Reset player : {player['pseudo']} by {interaction.user.name}")
            await interaction.response.defer(ephemeral=True)
            await self.bot.dashboard.update_Dashboard()
            return
        if len(values) != 3:
            await interaction.response.send_message(f"Something goes wrong while updating the database.\nPlease report this bug to Softy.")
            await interaction.response.defer(ephemeral=True)
            await self.bot.dashboard.update_Dashboard()
            return
        if values[1] == "player":
            player: Player_Model = self.bot.db.get_one_player("_id", ObjectId(values[2]))
            if player is None:
                print(values)
                await interaction.response.send_message(f"Something goes wrong while updating the database.\nPlease report this bug to Softy.")
                await self.bot.dashboard.update_Dashboard()
                return
            player["MB_refresh_time"] = date_resfresh
            player["MB_last_attack_time"] = date
            player["MB_status"] = "Down"
            self.bot.db.update_player(player)
            await self.log_channel.send(f"Attaque main base : {player['pseudo']} by {interaction.user.name}")
        elif values[1] == "colony":
            colony: Colony_Model = self.bot.db.get_one_colony("_id", ObjectId(values[2]))
            if colony is None:
                await interaction.response.send_message(f"Something goes wrong while updating the database.\nPlease report this bug to Softy.")
                await self.bot.dashboard.update_Dashboard()
                return
            # pas d'attaque si la colo n'est pas updated
            if colony["updated"] == True:
                colony["colo_refresh_time"] = date_resfresh
                colony["colo_last_attack_time"] = date
                colony["colo_status"] = "Down"
                self.bot.db.update_colony(colony)
                player: Player_Model = self.bot.db.get_one_player("_id", colony["_player_id"])
                await self.log_channel.send(f"Attaque colony {colony['number']} : {player['pseudo']} by {interaction.user.name}")
            else: 
                return
        await interaction.response.defer(ephemeral=True)
        await self.bot.dashboard.update_Dashboard()


class DropView(discord.ui.View):
    error: bool = False

    def __init__(self, bot: commands.Bot, players: Cursor[Player_Model], timeout: int = 180) -> None:
        super().__init__(timeout=timeout)
        for player in players:
            obj: dict = {"_player_id": player["_id"]}
            colonies: List[Colony_Model] = list(bot.db.get_colonies(obj))
            self.add_item(Select(bot, player, colonies))
