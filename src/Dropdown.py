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
import asyncio

class Select(discord.ui.Select):
    bot: commands.Bot
    log_channel_id: int = None
    log_channel: discord.abc.GuildChannel | discord.Thread | discord.abc.PrivateChannel | None = None
    date: datetime.datetime = datetime.datetime.now()
    
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
        if player["player_online"] == 1:
            status_emoji = Emoji.online.value 
            player["MB_refresh_time"] = self.date
            player["MB_last_attack_time"] = self.date
            player["MB_status"] = "Up"
            self.bot.db.update_player(player)
            obj: dict = {"_player_id": player["_id"]}
            colonies: List[Colony_Model] = list(self.bot.db.get_colonies(obj))
            for colony in colonies:
                colony["colo_refresh_time"] = self.date
                colony["colo_last_attack_time"] = self.date
                colony["colo_status"] = "Up"
                self.bot.db.update_colony(colony)
        else:
            if player["player_online"] == 2:
                status_emoji = Emoji.maybe.value
            else:
                if "state" in player:
                    if player["state"] == "MB_full":
                        status_emoji = Emoji.bouclier_MB.value
                    elif player["state"] == "everything_full":
                        status_emoji = Emoji.bouclier_tout.value
                    elif player["state"] == "afk":
                        status_emoji = Emoji.afk.value
                    elif player["state"] == "unknown":
                        status_emoji = Emoji.unknown.value
                    else:   
                        status_emoji = Emoji.offline.value
        player_temp: dict = self.bot.galaxylifeapi.get_player_infos(player["id_gl"])
        player_lvl: str = player_temp["player_lvl"]
        player_MB_lvl: str = player_temp["mb_lvl"]
        menu_label: str = f"{player_lvl if player_lvl != -1 else 'Non connue'}: {player['pseudo']}"
        
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
        menu_label += " " + menu_emoji if player["MB_status"] == "Down" else " " + Emoji.SB.value
        
        # modification pour mettre les colos non complétées
        
        for colony in colonies:
            if colony["number"] >= 10:
                break
            if colony["updated"] == True:
                if colony["colo_status"] == "Down" :
                    colo_refresh_date: datetime.datetime = colony['colo_refresh_time']
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
                    menu_label += menu_emoji 
                else:
                    if "gift_state" in colony:
                        if colony["gift_state"] != "Not Free":  
                            menu_emoji = Emoji.gift.value
                        else:
                            menu_emoji = Emoji.colo.value 
                    else:
                        menu_emoji = Emoji.colo.value
                    menu_label += menu_emoji 
            else:
                menu_label += Emoji.colo_empty.value
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
            menu_label = "Base Principale "
            date_refresh: datetime.datetime = player['MB_refresh_time']
            menu_description = f"SB ({player_MB_lvl}) - (Retour à {date_refresh.strftime('%H:%M:%S')})"
        else :
            menu_label = "Base Principale"
            menu_description = f"SB ({player_MB_lvl})"
            menu_emoji = Emoji.SB.value
        player_drop_down.append(discord.SelectOption(label = menu_label, emoji = menu_emoji, description = menu_description, value = str(it) + ";" + "player" + ";" + str(player["_id"])))
        it += 1
        for colony in colonies: 
            if colony["updated"] == True:
                if colony["colo_status"] == "Down" :
                    colo_refresh_date: datetime.datetime = colony['colo_refresh_time']
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
                    menu_description = f"({colony['colo_coord']['x']} ; {colony['colo_coord']['y']}) - SB ({colony['colo_lvl']}) - (Retour à {date_refresh.strftime('%H:%M:%S')})"
                else :
                    menu_label = f"{colony['colo_sys_name']}"
                    menu_description = f"({colony['colo_coord']['x']} ; {colony['colo_coord']['y']}) - SB ({colony['colo_lvl']})"
                    if "gift_state" in colony:
                        if colony["gift_state"] != "Not Free":  
                            menu_emoji = Emoji.gift.value
                        else:
                            menu_emoji = Emoji.colo.value
                    else:
                        menu_emoji = Emoji.colo.value
            else:
                menu_label = f" ?????"
                menu_description = f"( ? ; ? ) - SB ({colony['colo_lvl']})"
                menu_emoji = Emoji.colo_empty.value
            if colony["number"] <= 12:
                player_drop_down.append(discord.SelectOption(label = menu_label, emoji = menu_emoji, description = menu_description, value = str(it) + ";" + "colony" + ";" + str(colony["_id"])))
            it += 1
        menu_label = "Reset"
        menu_emoji = Emoji.Reset.value
        player_drop_down.append(discord.SelectOption(label = menu_label, emoji = menu_emoji, description = '', value = "Reset;" + str(player["_id"])))
        options = player_drop_down
        super().__init__(placeholder="Select an option", max_values=1, min_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        date = datetime.datetime.now()
        await interaction.response.defer(ephemeral=True)
        if self.values[0] == "":
            return
        refresh_duration: float = 6.0
        date_resfresh: datetime.datetime = date + datetime.timedelta(hours=refresh_duration)

        
        values: List[str] = self.values[0].split(";")
        self.values[0] = ""
        if len(values) == 2 and values[0] == "Reset":
            player: Player_Model = self.bot.db.get_one_player("_id", ObjectId(values[1]))
            if player is None:
                await interaction.response.send_message(f"Something goes wrong while updating the database.\nPlease report this bug to Softy.")
                await self.bot.dashboard.update_Dashboard()
                return
            player["MB_refresh_time"] = self.date
            player["MB_last_attack_time"] = self.date
            player["MB_status"] = "Up"
            self.bot.db.update_player(player)
            obj: dict = {"_player_id": player["_id"]}
            colonies: List[Colony_Model] = list(self.bot.db.get_colonies(obj))
            for colony in colonies:
                colony["colo_refresh_time"] = self.date
                colony["colo_last_attack_time"] = self.date
                colony["colo_status"] = "Up"
                self.bot.db.update_colony(colony)
            await self.log_channel.send(f"Reset player : {player['pseudo']} by {interaction.user.display_name}")
            
            await self.bot.dashboard.update_Dashboard()
            return
        if len(values) != 3:
            await interaction.response.send_message(f"Something goes wrong while updating the database.\nPlease report this bug to Softy.")
            #await interaction.response.defer(ephemeral=True)
            await self.bot.dashboard.update_Dashboard()
            return
        
        if values[1] == "player":
            player: Player_Model = self.bot.db.get_one_player("_id", ObjectId(values[2]))
            if player is None:
                await interaction.response.send_message(f"Something goes wrong while updating the database.\nPlease report this bug to Softy.")
                await self.bot.dashboard.update_Dashboard()
                return
            player["MB_refresh_time"] = date_resfresh
            player["MB_last_attack_time"] = self.date
            player["MB_status"] = "Down"
            self.bot.db.update_player(player)
            player_temp: dict = self.bot.galaxylifeapi.get_player_infos(player["id_gl"])
            player_lvl: str = player_temp["player_lvl"]
            await self.log_channel.send(f"> 💥 __Level {player_lvl}__ **{player['pseudo'].upper()}**: 🌍 main base destroyed by {interaction.user.display_name}")
        elif values[1] == "colony":
            colony: Colony_Model = self.bot.db.get_one_colony("_id", ObjectId(values[2]))
            if colony is None:
                await interaction.response.send_message(f"Something goes wrong while updating the database.\nPlease report this bug to Softy.")
                await self.bot.dashboard.update_Dashboard()
                return
            # pas d'attaque si la colo n'est pas updated
            if colony["updated"] == True:
                if "gift_state" in colony:
                    if colony['gift_state'] == "Free Once":
                        colony['gift_state'] = "Not Free"
                colony["colo_refresh_time"] = date_resfresh
                colony["colo_last_attack_time"] = self.date
                colony["colo_status"] = "Down"
                self.bot.db.update_colony(colony)
                player: Player_Model = self.bot.db.get_one_player("_id", colony["_player_id"])
                player_temp: dict = self.bot.galaxylifeapi.get_player_infos(player["id_gl"])
                player_lvl: str = player_temp["player_lvl"]
                await self.log_channel.send(f"> 💥 __Level {player_lvl}__ **{player['pseudo'].upper()}**: 🪐 colony number **{colony['number']}**  destroyed by {interaction.user.display_name}")
            else: 
                return
        #await interaction.response.defer(ephemeral=True)
        # await self.bot.dashboard.update_Dashboard()


class DropView(discord.ui.View):
    error: bool = False

    def __init__(self, bot: commands.Bot, players: Cursor[Player_Model], timeout: int = 180) -> None:
        super().__init__(timeout=timeout)
        for player in players:
            obj: dict = {"_player_id": player["_id"]}
            colonies: List[Colony_Model] = list(bot.db.get_colonies(obj))
            self.add_item(Select(bot, player, colonies))
