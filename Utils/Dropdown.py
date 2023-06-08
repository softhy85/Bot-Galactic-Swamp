import asyncio
import datetime
import os
import time
from typing import List
from threading import Thread 
import discord
from bson.objectid import ObjectId
from discord.ext import commands
from pymongo.cursor import Cursor

from Models.Colony_Model import Colony_Model
from Models.Emoji import Emoji
from Models.Player_Model import Player_Model
from Models.War_Model import War_Model


class Select(discord.ui.Select):
    bot: commands.Bot
    log_channel_id: int = None
    log_channel: discord.abc.GuildChannel | discord.Thread | discord.abc.PrivateChannel | None = None
    date: datetime.datetime = datetime.datetime.now()
    
    def __init__(self, bot: commands.Bot, player: Player_Model, colonies: List[Colony_Model], actual_war: Player_Model) -> None:
        self.bot = bot
        self.actual_war = actual_war
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
        troop_list = ["Falcons","Colossus", "Wasps", "Zepellins", "Falcons / Colossus","Colossus / Menders", "Unknown"]
        if player["online"] == 2:
            status_emoji = Emoji.online.value 
            player["MB_refresh_time"] = self.date
            player["MB_last_attack_time"] = self.date
            player["MB_status"] = "Up"
            self.bot.db.update_player(player)
            obj: dict = {"id_gl": player["id_gl"]}
            colonies: List[Colony_Model] = list(self.bot.db.get_colonies(obj))
            colonies.sort(key=lambda item: item.get("number"))
            for colony in colonies:
                colony["colo_refresh_time"] = self.date
                colony["colo_last_attack_time"] = self.date
                colony["colo_status"] = "Up"
                self.bot.db.update_colony(colony)
        else:
            if player["online"] == 1:
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
        player_lvl: str = player["lvl"]
        player_MB_lvl: str = player["MB_lvl"]
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
        scouted: bool = False
        for colony in colonies:
            length = len(menu_label) + (len(menu_label) - len(player["pseudo"] + " : "  + str(player["lvl"])))*2
            if length >= 39:
                menu_label += Emoji.more.value
                break
            else:
                if colony["updated"] or (colony["colo_coord"]["x"] > -1 and colony["colo_coord"]["y"] > -1):
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
                    if "scouted" in colony:
                        scouted: bool = True
                else:
                    menu_label += Emoji.colo_empty.value
        player_drop_down.append(discord.SelectOption(label = menu_label, emoji = status_emoji ,description = "", value = "", default = True))
        it += 1
        if "colonies_moved" in player:
            colonies_moved: int = player["colonies_moved"]
        else:
            colonies_moved: int = 0
        if scouted == True:
            scout_state: str = "- Player scouted ✅"
        else: 
            scout_state = ""
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
            menu_label = f"Main Base {scout_state}"
            date_refresh: datetime.datetime = player['MB_refresh_time']
            menu_description = f"SB {player_MB_lvl} - ♻️ Up: {date_refresh.strftime('%H:%M')} - 🪐 {colonies_moved} moved"
        else :
            menu_label = f"Main Base {scout_state}"
            menu_description = f"SB {player_MB_lvl} - 🪐 {colonies_moved} moved"
            if 'bunker_troops' in player:
                menu_description = menu_description + f" - 🛡️ {troop_list[player['bunker_troops']]}"
            menu_emoji = Emoji.SB.value
        player_drop_down.append(discord.SelectOption(label = menu_label, emoji = menu_emoji, description = menu_description, value = str(it) + ";" + "player" + ";" + str(player["_id"])))
        it += 1
        for colony in colonies:
            if colony["updated"] or colony["colo_coord"]["x"] > -1:
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
                    menu_label = f"{colony['colo_sys_name'].upper()}"
                    if colony['colo_sys_name'] == "?" or colony['colo_sys_name'] == "-1":
                        menu_label = "Unknown System"
                    date_refresh: datetime.datetime = colony['colo_refresh_time']
                    menu_description = f"SB {colony['colo_lvl']} - ({colony['colo_coord']['x']} ; {colony['colo_coord']['y']}) - ♻️ Up: {date_refresh.strftime('%H:%M')}"
                else :
                    menu_label = f"{colony['colo_sys_name'].upper()}"
                    if colony['colo_sys_name'] == "?" or colony['colo_sys_name'] == "-1":
                        menu_label = "Unknown System"
                    menu_description = f"SB {colony['colo_lvl']} - ({colony['colo_coord']['x']} ; {colony['colo_coord']['y']})"
                    if 'bunker_troops' in colony:
                        menu_description = menu_description + f" - 🛡️ {troop_list[colony['bunker_troops']]}"
                    if "gift_state" in colony:
                        if colony["gift_state"] != "Not Free":  
                            menu_emoji = Emoji.gift.value
                        else:
                            menu_emoji = Emoji.colo.value
                    else:
                        menu_emoji = Emoji.colo.value
            else:
                menu_label = f" ????? ( ? ; ? )"
                menu_description = f"SB {colony['colo_lvl']}"
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
        await interaction.response.defer(ephemeral=True)
        date = datetime.datetime.now()
        log_message = None     
        if self.values[0] == "":
            return
        date_resfresh: datetime.datetime = date + datetime.timedelta(hours=self.actual_war["refresh_duration"])
        values: List[str] = self.values[0].split(";")
        self.values[0] = ""
        if len(values) == 2 and values[0] == "Reset":
            player: Player_Model = self.bot.db.get_one_player("_id", ObjectId(values[1]))
            if player is None:
                await interaction.response.send_message(f"Something goes wrong while updating the database.\nPlease report this bug to Softy.")
                return
            player["MB_refresh_time"] = self.date
            player["MB_last_attack_time"] = self.date
            player["MB_status"] = "Up"
            self.bot.db.update_player(player)
            obj: dict = {"id_gl": player["id_gl"]}
            colonies: List[Colony_Model] = list(self.bot.db.get_colonies(obj))
            for colony in colonies:
                colony["colo_refresh_time"] = self.date
                colony["colo_last_attack_time"] = self.date
                colony["colo_status"] = "Up"
                self.bot.db.update_colony(colony)
            await interaction.response.send_message(f"Reset player : {player['pseudo']} by {interaction.user.display_name}")
            return
        if len(values) != 3:
            await interaction.response.send_message(f"Something goes wrong while updating the database.\nPlease report this bug to Softy.")
            return
        
        if values[1] == "player":
            player: Player_Model = self.bot.db.get_one_player("_id", ObjectId(values[2]))
            if player is None:
                await interaction.response.send_message(f"Something goes wrong while updating the database.\nPlease report this bug to Softy.")
                return
            player["MB_refresh_time"] = date_resfresh
            player["MB_last_attack_time"] = self.date
            player["MB_status"] = "Down"
            self.bot.db.update_player(player)
            player_lvl: str = player["lvl"]
            log_message = await self.log_channel.send(f"> 💥 __Level {player_lvl}__ **{player['pseudo'].upper()}**: 🌍 main base destroyed by {interaction.user.display_name}")
            
        elif values[1] == "colony":
            colony: Colony_Model = self.bot.db.get_one_colony("_id", ObjectId(values[2]))
            if colony is None:
                await interaction.response.send_message(f"Something goes wrong while updating the database.\nPlease report this bug to Softy.")
                # await self.bot.dashboard.update_Dashboard()
                return
            if colony["updated"] or colony["colo_coord"]["x"] > -1:
                if "gift_state" in colony:
                    if colony['gift_state'] == "Free Once":
                        colony['gift_state'] = "Not Free"
                colony["colo_refresh_time"] = date_resfresh
                colony["colo_last_attack_time"] = self.date
                colony["colo_status"] = "Down"
                self.bot.db.update_colony(colony)
                player: Player_Model = self.bot.db.get_one_player("_id", colony["_player_id"])
                player_lvl: str = player["lvl"]
                log_message = await self.log_channel.send(f"> 💥 __Level {player_lvl}__ **{player['pseudo'].upper()}**: 🪐 colony number **{colony['number']}**  destroyed by {interaction.user.display_name}")
            else:
                return
        
        if log_message:
            colo_leaked = self.bot.db.get_leaked_colonies()
            print(colo_leaked)
            reaction_list = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]
            for item in reaction_list:
                await log_message.add_reaction(f'{item}')
            # history = [message async for message in self.log_channel.history(before=date - datetime.timedelta(seconds=30), after=colo_leaked["last_update"])]
            # for message in history:
            #     for index in range(0, len(message.reactions)):
            #         await message.remove_reaction(emoji=message.reactions[index].emoji, member=message.author)
            # for message in history:
            #     username = message.content.split('**')[1]
            #     for index in range(0, len(message.reactions)):
            #         users = [user async for user in message.reactions[index].users()]
            #         for user in users:
            #             emoji = message.reactions[index].emoji
            #             if user.name in colo_leaked:
            #                 emoji = message.reactions[index].emoji
            #                 if not username in colo_leaked[user.name]:
            #                     colo_leaked[user.name][username] = {}
            #                 if emoji in colo_leaked[user.name][username]:
            #                     colo_leaked[user.name][username][emoji.name] += 1
            #                 else:
            #                     colo_leaked[user.name][username][emoji] = 1
            #             else: 
            #                 colo_leaked[user.name] = {}
            #                 colo_leaked[user.name][username] = {}
            #                 colo_leaked[user.name][username][emoji] = {}
            #                 colo_leaked[user.name][username][emoji] = 1
            # print(colo_leaked)
            # end_date = datetime.datetime.now()
            # colo_leaked["last_update"] = end_date - datetime.timedelta(minutes=1)
            # self.bot.db.update_leaked_colonies(colo_leaked)
            # print('updated')
        await interaction.response.defer(ephemeral=True)
        await self.bot.dashboard.update_Dashboard()


class DropView(discord.ui.View):
    error: bool = False

    def __init__(self, bot: commands.Bot, players: Cursor[Player_Model], actual_war: War_Model, timeout: int = 180) -> None:
        super().__init__(timeout=timeout)
        for player in players:
            # obj: dict = {"_player_id": ObjectId(player["_id"])}
            obj: dict = {"id_gl": player["id_gl"]}
            colonies: List[Colony_Model] = list(bot.db.get_colonies(obj))
            colonies.sort(key=lambda item: item.get("number"))
            self.add_item(Select(bot, player, colonies, actual_war))
