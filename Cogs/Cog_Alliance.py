import discord
from discord import app_commands
from discord.ext import commands
from Models.Alliance_Model import Alliance_Model
from Models.Player_Model import Player_Model
from Models.Colony_Model import Colony_Model
from discord.ui import Button, View
from Models.Colors import Colors
from Models.Emoji import Emoji
from typing import List
import os
import re
import time

class Cog_Alliance(commands.Cog):
    bot: commands.Bot = None
    war_channel_id: int = None
    war_channel: discord.abc.GuildChannel | discord.Thread | discord.abc.PrivateChannel | None = None

    def __init__(self, bot: commands.Bot):
        super().__init__()
        self.bot = bot
        self.war_channel_id: int = int(os.getenv("WAR_CHANNEL"))
        self.war_channel = self.bot.get_channel(self.war_channel_id)
        self.backup_channel_id: int = int(os.getenv("COLO_BACKUP_CHANNEL"))
        self.backup_channel = self.bot.get_channel(self.backup_channel_id)
        self.command_channel_id: int = int(os.getenv("COMMAND_CHANNEL"))
        self.command_channel = self.bot.get_channel(self.command_channel_id)
        self.ally_alliance_name = os.getenv("ALLY_ALLIANCE_NAME")

    #<editor-fold desc="listener">

    @commands.Cog.listener()
    async def on_ready(self):
        print("Cog Loaded: Cog_Alliance")

    #</editor-fold>

    #<editor-fold desc="autocomplete">

    async def alliance_autocomplete(self, interaction: discord.Interaction, current: str) -> List[app_commands.Choice[str]]:
        obj: dict = {}
        if current != "":
            obj: dict = {"name": {"$regex": re.compile(current, re.IGNORECASE)}}
        alliances: List[Alliance_Model] = list(self.bot.db.get_alliances(obj))
        alliances = alliances[0:25]
        return [
            app_commands.Choice(name=alliance["name"], value=alliance["name"])
            for alliance in alliances
        ]

    def button_alliance(self, alliance, alliance_check: list, display):
        if alliance != None and alliance != "":
            button = Button(label = f"{alliance_check['alliance_state'][0]} Alliance", style=alliance_check['button_style'], emoji="🔒")       
            async def button_callback_alliance(interaction):
                button = Button(label = f"{alliance_check['alliance_state'][0]} Alliance ", style=discord.ButtonStyle.gray)
                display[1].clear_items()
                display[1].add_item(button)
                await interaction.response.edit_message(embed=display[0], view=display[1])
                if not self.bot.spec_role.admin_role(interaction.guild, interaction.user):
                    await interaction.followup.send("You don't have the permission to use this command.")
                    return
                act_alliance: Alliance_Model = self.bot.db.get_one_alliance("name", alliance.upper())
                loading_message = await interaction.followup.send(f"> Loading the alliance... (started <t:{int(time.time())}:R>)")
                await self.bot.alliance.update_alliance(alliance.upper())
                await loading_message.edit(content="> Alliance Loaded ✅")
            button.callback = button_callback_alliance
            display[1].add_item(button)
        return display    
    # en double: cog?
    def has_alliance(self, alliance: str):
        return_value: dict = {}
        alliance_state: list = ["Add","Added"]
        button_style = discord.ButtonStyle.green
        alliance_db: dict = self.bot.db.get_one_alliance("name", alliance.upper())
        if alliance_db is not None:
            button_style = discord.ButtonStyle.blurple
            alliance_state: list = ["Update", "Updated"]
        return_value['alliance_state'] = alliance_state
        return_value['button_style'] = button_style
        return return_value

    # optimisable? mettre dans dashboard
    def empty_space(self, alliance_api_info: dict):
        it = 0
        return_value: list = []
        empty_space_length = 11        
        empty_space_score = ""
        empty_space_lvl = ""
        empty_space_length_lvl = empty_space_length - len(alliance_api_info['alliance_lvl'])
        empty_space_length_score = empty_space_length - len(alliance_api_info['alliance_formatted_score'])
        while it < empty_space_length_score:
            empty_space_score = empty_space_score + " "
            it += 1
        it = 0
        while it < empty_space_length_lvl:
            empty_space_lvl = empty_space_lvl + " "
            it += 1
        return_value = [empty_space_score, empty_space_lvl]
        return return_value
        
    #</editor-fold>

    #<editor-fold desc="command">

    @app_commands.command(name="alliance_add", description="Add a new Cog_Alliance to the db")
    @app_commands.describe(alliance="The name of the alliance")
    @app_commands.checks.has_role('Admin')
    @app_commands.default_permissions()
    async def alliance_add(self, interaction: discord.Interaction, alliance: str):
        await interaction.response.defer(ephemeral=True)
        if not self.bot.spec_role.admin_role(interaction.guild, interaction.user):
            await interaction.followup.send("You don't have the permission to use this command.")
            return
        if alliance.strip() == "":
            await interaction.followup.send(f"Cannot create alliances with a name composed only of whitespace.")
            return
        act_alliance: Alliance_Model = self.bot.db.get_one_alliance("name", alliance.upper())
        if act_alliance is None:
            await interaction.followup.send("> Loading the new alliance.")
        else:
            await interaction.followup.send("> Updating the alliance.")
        await self.bot.alliance.update_alliance(alliance)

    @app_commands.command(name="alliance_update", description="Update an existent Cog_Alliance")
    @app_commands.describe(alliance="Alliance's name")
    @app_commands.autocomplete(alliance=alliance_autocomplete)
    @app_commands.checks.has_role('Admin')
    async def alliance_update(self, interaction: discord.Interaction, alliance: str, alliance_lvl: int):
        if not self.bot.spec_role.admin_role(interaction.guild, interaction.user):
            await interaction.response.send_message("You don't have the permission to use this command.")
            return
        if alliance.strip() == "":
            await interaction.response.send_message(f"Cannot update Alliances with a name composed only of whitespace.")
            return
        return_alliance: Alliance_Model = self.bot.db.get_one_alliance("name", alliance)
        if return_alliance is None:
            await interaction.response.send_message(f"Alliance named {alliance} does not exist.")
        else:
            return_alliance["alliance_lvl"] = alliance_lvl
            self.bot.db.update_alliance(return_alliance)
            await interaction.response.send_message(f"Alliance named {alliance} updated.")

    @app_commands.command(name="alliance_remove", description="Remove an existent Cog_Alliance")
    @app_commands.describe(alliance="Alliance's name")
    @app_commands.autocomplete(alliance=alliance_autocomplete)
    @app_commands.checks.has_role('Admin')
    async def alliance_remove(self, interaction: discord.Interaction, alliance: str):
        return_alliance: Alliance_Model = self.bot.db.get_one_alliance("name", alliance)
        if not self.bot.spec_role.admin_role(interaction.guild, interaction.user):
            await interaction.response.send_message("You don't have the permission to use this command.")
            return
        if alliance.strip() == "":
            await interaction.response.send_message(f"Cannot remove Alliances with a name composed only of whitespace.")
            return
        if return_alliance is None:
            await interaction.response.send_message(f"Alliance named {alliance} does not exist.")
        else:
            self.bot.db.remove_alliance(return_alliance)
            await interaction.response.send_message(f"Alliance named {alliance} as been removed.")
       
    @app_commands.command(name="alliance_colonies", description="Get all colonies from an alliance")
    @app_commands.describe(alliance="Alliance's name")
    @app_commands.autocomplete(alliance=alliance_autocomplete)
    @app_commands.checks.has_any_role('Admin')
    async def alliance_colonies(self, interaction: discord.Interaction,  alliance: str): 
        alliance_info: Alliance_Model = self.bot.db.get_one_alliance("name", alliance)
        alliance_api_info = self.bot.galaxyLifeAPI.get_alliance(alliance_info["name"])
        obj: dict = {"_alliance_id": alliance_info["_id"]}
        players: List[Player_Model] = self.bot.db.get_players(obj)
        await interaction.response.send_message(f"Here's the database for {alliance_info['name']}:")
        embed: discord.Embed = discord.Embed(title=f"➖➖➖➖ {alliance_info['name']} ➖➖➖➖", description=" \n ", color=discord.Color.from_rgb(8, 1, 31))
        embed.set_thumbnail(url=alliance_api_info["emblem_url"])
        total_size: int = 0
        field_count: int = 0
        for player in players:
            value: str = ""
            obj: dict = {"_player_id": player["_id"]}
            colonies: List[Colony_Model] = list(self.bot.db.get_colonies(obj))
            for colo in colonies:
                if colo['colo_coord']['x'] != -1:
                    value = value + f"\n🪐 **__(SB{colo['colo_lvl']}):__**\n/colo_update pseudo:{player['pseudo']} colo_number:{colo['number']} colo_sys_name:{colo['colo_sys_name']} colo_coord_x:{colo['colo_coord']['x']} colo_coord_y:{colo['colo_coord']['y']}\n"
            if value != "": 
                embed.add_field(name=f"\n✅ {player['pseudo']}",value=value, inline=False)
                field_count += 1
        
            total_size += len(value) + len(player) + 5
            if total_size >= 2500 or field_count >= 20:
                await self.backup_channel.send(embed=embed)
                embed: discord.Embed = discord.Embed(title="", description="", color=discord.Color.from_rgb(8, 1, 31)) 
                total_size: int = 0
                field_count: int = 0
        if total_size != 0:
            await self.backup_channel.send(embed=embed)

    @app_commands.command(name="alliance_infos", description="Get all colonies from an alliance")
    @app_commands.describe(alliance="Alliance's name")
    @app_commands.autocomplete(alliance=alliance_autocomplete)
    @app_commands.checks.has_any_role('Admin')
    async def alliance_infos(self, interaction: discord.Interaction,  alliance: str): 
        alliance_api_info = self.bot.galaxyLifeAPI.get_alliance(alliance)
        if not alliance_api_info:
            await interaction.response.send_message(f"**{alliance.upper()}** doesn't exist as an alliance.")
            return 
        empty_space = self.empty_space(alliance_api_info)
        description = f"```💫 Score:{empty_space[0]}{alliance_api_info['alliance_formatted_score']}\n📈 WR:        {alliance_api_info['alliance_winrate'] if alliance_api_info['alliance_winrate'] != -1 else 'xx.xx'}% \n⭐ Level:{empty_space[1]}{alliance_api_info['alliance_lvl']}\n👤 Members:       {len(alliance_api_info['members_list'])}```"
        alliance_check = self.has_alliance(alliance)
        embed: discord.Embed = discord.Embed(title=f"{alliance.upper()}", description=description, color=discord.Color.from_rgb(130, 255, 128))
        embed.add_field(name=f"",value=alliance_api_info['alliance_description'], inline=False)
        embed.set_thumbnail(url=alliance_api_info["emblem_url"])
        view = View()
        display: list = [embed, view]
        self.button_alliance(alliance, alliance_check, display)
        await interaction.response.send_message(embed=display[0], view=display[1])
    
    
    @app_commands.command(name="alliance_team_mates", description="Spy your mates because they don't answer you")
    @app_commands.checks.has_any_role('Admin')
    async def alliance_team_mates(self, interaction: discord.Interaction): 
        await interaction.response.defer(ephemeral=True)
        embed: discord.Embed = discord.Embed(title=f"<:empty:1088454928474841108>Crew Overview", description="Use the bot or you will be \n*smashed* 🔨 by Diablo.", color=discord.Color.from_rgb(255, 100, 100))
        obj: dict = {"name", "GALACTIC SWAMP"}
        alliance: Alliance_Model = self.bot.db.get_one_alliance("name", "GALACTIC SWAMP")
        obj: dict = {"_alliance_id": alliance['_id']}
        alliance_players: List[Player_Model] = list(self.bot.db.get_players(obj))
        value = ">>> "
        alliance_players.sort(key=lambda item: item.get("lvl"), reverse=True)
        it = 0
        for player in alliance_players:
            status = self.bot.galaxyLifeAPI.get_player_status(player["id_gl"])
            if status == None:
                status = 0
            alliance_players[it]["status_steam"] = status
            it += 1
        alliance_players.sort(key=lambda item: item.get("status_steam"), reverse=True)
        for player in alliance_players:    
            if player["status_steam"] == 0:
                emoji = Emoji.offline.value
            elif player["status_steam"] == 1:
                emoji = Emoji.maybe.value
            else:
                emoji = Emoji.online.value
            value = value + emoji + " " + player["pseudo"] + "\n"
        embed.add_field(name="Members:",value=value, inline=False)
        # embed.set_thumbnail(url=alliance_api_info["emblem_url"])
        view = View()
        await interaction.followup.send(embed=embed, view=view)
        
        
    @app_commands.command(name="alliance_leaderboard", description="Leaderboard")
    async def alliance_leaderboard(self, interaction: discord.Interaction): 
        leaderboard: dict = self.bot.galaxyLifeAPI.get_alliance_leaderboard()
        embed =discord.Embed(title=f"️Leaderboard", description="", color=Colors.dark_magenta)
        name: str = f"📈 Current Rank: "
        value: str = (f"```ansi\n\u001b[0;0m{leaderboard['3']-2}# ⏫ {leaderboard['-2']['Name']}:    +\u001b[0;31m{leaderboard['-2']['Warpoints']-leaderboard['0']['Warpoints']}\u001b[0;0m"+
                      f"\n{leaderboard['3']-1}# 🔼 {leaderboard['-1']['Name']}:    +\u001b[0;31m{leaderboard['-1']['Warpoints']-leaderboard['0']['Warpoints']}\u001b[0;0m"+
                      f"\n{leaderboard['3']}# ✅ {leaderboard['0']['Name']}:    {leaderboard['0']['Warpoints']}"+
                      f"\n{leaderboard['3']+1}# 🔽 {leaderboard['1']['Name']}:    -\u001b[0;30m{abs(leaderboard['1']['Warpoints']-leaderboard['0']['Warpoints'])}\u001b[0;0m"+
                      f"\n{leaderboard['3']+2}# ⏬ {leaderboard['2']['Name']}:    -\u001b[0;30m{abs(leaderboard['2']['Warpoints']-leaderboard['0']['Warpoints'])}\u001b[0;0m```")
        embed.add_field(name=name, value=value, inline=False)
        embed.set_thumbnail(url="https://cdn.discordapp.com/icons/943168885333581886/a_12f99da94b70ba0624195d65327f33ce.gif")
        await interaction.response.send_message(embed=embed)
        
    #</editor-fold>

async def setup(bot: commands.Bot):
    await bot.add_cog(Cog_Alliance(bot), guilds=[discord.Object(id=os.getenv("SERVER_ID"))])