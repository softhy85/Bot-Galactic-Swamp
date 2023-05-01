import datetime
import discord
from discord import app_commands, ui
from discord.ext import commands, tasks
from Models.War_Model import War_Model
from Models.Player_Model import Player_Model
from Models.Colony_Model import Colony_Model
from Models.Alliance_Model import Alliance_Model
from Utils.GalaxyCanvas import GalaxyCanvas
from Models.Emoji import Emoji
from Models.Colors import Colors
from typing import List
from discord.ui import Button, View, Select
from discord import File, Embed
import os
import re

class Cog_Colony(commands.Cog):
    guild: discord.Guild = None
    bot: commands.bot = None
    experiment_channel_id: int = 0
    experiment_channel: discord.abc.GuildChannel | discord.Thread | discord.abc.PrivateChannel | None = None
    war_channel_id: int = 0
    war_channel: discord.abc.GuildChannel | discord.Thread | discord.abc.PrivateChannel | None = None
    general_channel_id: int = 0
    general_channel: discord.abc.GuildChannel | discord.Thread | discord.abc.PrivateChannel | None = None

    def __init__(self, bot: commands.Bot):
        super().__init__()
        self.bot = bot
        self.experiment_channel_id = int(os.getenv("EXPERIMENT_CHANNEL"))
        self.experiment_channel = self.bot.get_channel(self.experiment_channel_id)
        self.war_channel_id  = int(os.getenv("WAR_CHANNEL"))
        self.war_channel = self.bot.get_channel(self.war_channel_id)
        self.general_channel_id = int(os.getenv("GENERAL_CHANNEL"))
        self.general_channel = self.bot.get_channel(self.war_channel_id)
        self.guild = self.bot.get_guild(int(os.getenv("SERVER_ID")))
        self.log_channel_id: int = int(os.getenv("LOG_CHANNEL"))
        self.log_channel = self.bot.get_channel(self.log_channel_id)


    #<editor-fold desc="listener">

    @commands.Cog.listener()
    async def on_ready(self):
        print("Cog Loaded: Cog_Colony")


    #</editor-fold>

    #<editor-fold desc="autocomplete">

    async def player_autocomplete(self, interaction: discord.Interaction, current: str) -> List[app_commands.Choice[str]]:
        obj: dict = {}
        if current != "":
            obj = {"pseudo": {"$regex": re.compile(current, re.IGNORECASE)}}
        players: List[Player_Model] = list(self.bot.db.get_players(obj))
        players = players[0:25]
        return [
            app_commands.Choice(name=player["pseudo"], value=player["pseudo"])
            for player in players
        ] 
            
    async def  colo_autocomplete(self, interaction: discord.Interaction, current: str) -> List[app_commands.Choice[str]]:
        pseudo = interaction.namespace.pseudo
        player_id: Player_Model = self.bot.db.get_one_player("pseudo", {"$regex": re.compile(pseudo, re.IGNORECASE)})  
        obj: dict = {"_player_id": player_id['_id']} 
        colos: List[Colony_Model] = list(self.bot.db.get_colonies(obj))
        colos.sort(key=lambda item: item.get("number"))
        colos = colos[0:25]
        return [
            app_commands.Choice(name=f'{Emoji.updated.value if colo["updated"] else Emoji.native.value} Colo n°{colo["number"]} (SB{colo["colo_lvl"]}) {colo["colo_sys_name"] if colo["updated"] else ""} {colo["colo_coord"]["x"] if colo["updated"] else ""} {colo["colo_coord"]["y"] if colo["updated"] else ""}', value=colo["number"])
            for colo in colos
        ]
            
    async def player_war_autocomplete(self, interaction: discord.Interaction, current: str) -> List[app_commands.Choice[str]]:
        act_war: War_Model = self.bot.db.get_one_war("status", "InProgress")
        return_player = self.bot.db.get_one_player("pseudo", "temp_player")
        temp_pseudo: list = [{"Name":"None"}]
        temp_pseudo[0]["Name"] = return_player["temp_pseudo"]
        if act_war is None:
            if len(current) >= 4:
                players = self.bot.galaxyLifeAPI.search_for_player(current)
                if players:
                    players = players + temp_pseudo
                    return [
                        app_commands.Choice(name=players[it]["Name"], value=players[it]["Name"])
                        for it in range(0, len(players))
                    ]
            else: 
                return [
                    app_commands.Choice(name=return_player["temp_pseudo"], value=return_player["temp_pseudo"])
                ]
        else:
            if current == "":
                obj: dict = {"_alliance_id": act_war["_alliance_id"]}
            else:
                obj: dict = {"_alliance_id": act_war["_alliance_id"], "pseudo": {"$regex": re.compile(current, re.IGNORECASE)}}
            players: List[Player_Model] = list(self.bot.db.get_players(obj))
            players = players[0:25]
            temp_pseudo[0]["pseudo"] = return_player["temp_pseudo"]
            print(list(players))
            players = players + list(temp_pseudo)
            return [
                app_commands.Choice(name=player["pseudo"], value=player["pseudo"])
                for player in players
            ]

    async def gift_state_autocomplete(self, interaction: discord.Interaction, current: str) -> List[app_commands.Choice[str]]: 
        data = []
        for choice in ["Always Free","Free Once", "Not Free"]:
            data.append(app_commands.Choice(name=choice, value=choice))
        return data

    #</editor-fold>
    
    #<editor-fold desc="functions">
    
    def button_right(self, view, embed):
            button_right = Button(label = f"⇨", style=discord.ButtonStyle.blurple)
            view.add_item(button_right)
            async def button_callback_right(interaction):
                if self.new_pos_x + 0.5*int(1000/self.new_zoom) <= 1000 - 0.5*int(1000/self.new_zoom):
                    self.new_pos_x = self.new_pos_x + 0.5*int(1000/self.new_zoom)
                else: 
                    self.new_pos_x = 1000 - 0.5*int(1000/self.new_zoom)
                self.bot.galaxyCanvas.draw_map(self.new_zoom, self.new_pos_x, self.new_pos_y)
                new_file = discord.File("./Image/scout_map.png", filename="scout_map.png")
                button_right.callback = button_callback_right
                embed.clear_fields()
                embed.add_field(name=f"🔍 Zoom: {int(self.new_zoom)}   -   🎯  X: {self.new_pos_x}   -   🎯  Y: {self.new_pos_y}       ", value='')
                await interaction.response.edit_message(embed=embed, view=view, attachments=[new_file]) 
            button_right.callback = button_callback_right

    def button_left(self, view, embed):
        button_left = Button(label = f"⇦", style=discord.ButtonStyle.blurple)
        view.add_item(button_left)
        async def button_callback_left(interaction):
            if self.new_pos_x - 0.5*int(1000/self.new_zoom) >= 0.5*int(1000/self.new_zoom):
                self.new_pos_x = self.new_pos_x - 0.5*int(1000/self.new_zoom)
            else: 
                self.new_pos_x = 0.5*int(1000/self.new_zoom)
            self.bot.galaxyCanvas.draw_map(self.new_zoom, self.new_pos_x, self.new_pos_y)
            new_file = discord.File("./Image/scout_map.png", filename="scout_map.png")
            button_left.callback = button_callback_left
            embed.clear_fields()
            embed.add_field(name=f"🔍 Zoom: {int(self.new_zoom)}   -   🎯  X: {self.new_pos_x}   -   🎯  Y: {self.new_pos_y}       ", value='')
            await interaction.response.edit_message(embed=embed, view=view, attachments=[new_file])    
        button_left.callback = button_callback_left
    
    def button_down(self, view, embed):
        button_down = Button(label = f"⇩", style=discord.ButtonStyle.blurple)
        view.add_item(button_down)
        async def button_callback_down(interaction):
            if self.new_pos_y + 0.5*int(1000/self.new_zoom) <= 1000 - 0.5*int(1000/self.new_zoom):
                self.new_pos_y = self.new_pos_y + 0.5*int(1000/self.new_zoom)
            else: 
                self.new_pos_y = 1000 - 0.5*int(1000/self.new_zoom)
            self.bot.galaxyCanvas.draw_map(self.new_zoom, self.new_pos_x, self.new_pos_y)
            new_file = discord.File("./Image/scout_map.png", filename="scout_map.png")
            embed.clear_fields()
            button_down.callback = button_callback_down
            embed.add_field(name=f"🔍 Zoom: {int(self.new_zoom)}   -   🎯  X: {self.new_pos_x}   -   🎯  Y: {self.new_pos_y}       ", value='')
            await interaction.response.edit_message(embed=embed, view=view, attachments=[new_file]) 
        button_down.callback = button_callback_down

    def button_up(self, view, embed):
        button_up = Button(label = f"⇧", style=discord.ButtonStyle.blurple)
        view.add_item(button_up)
        async def button_callback_up(interaction):
            if self.new_pos_y - 0.5*int(1000/self.new_zoom) >= 0.5*int(1000/self.new_zoom):
                self.new_pos_y = self.new_pos_y - 0.5*int(1000/self.new_zoom)
            else: 
                self.new_pos_y = 0.5*int(1000/self.new_zoom)
            self.bot.galaxyCanvas.draw_map(self.new_zoom, self.new_pos_x, self.new_pos_y)
            new_file = discord.File("./Image/scout_map.png", filename="scout_map.png")
            embed.clear_fields()
            button_up.callback = button_callback_up
            embed.add_field(name=f"🔍 Zoom: {int(self.new_zoom)}   -   🎯  X: {self.new_pos_x}   -   🎯  Y: {self.new_pos_y}       ", value='')
            await interaction.response.edit_message(embed=embed, view=view, attachments=[new_file]) 
        button_up.callback = button_callback_up     
        
    def button_zoom_in(self, view, embed):    
        button_zoom_in = Button(label = f"＋", style=discord.ButtonStyle.green)
        view.add_item(button_zoom_in)
        async def button_callback_zoom_in(interaction):
            if self.new_zoom <= 100:
                self.new_zoom = self.new_zoom * 2
            self.bot.galaxyCanvas.draw_map(self.new_zoom, self.new_pos_x, self.new_pos_y)
            new_file = discord.File("./Image/scout_map.png", filename="scout_map.png")
            button_zoom_in.callback = button_callback_zoom_in
            embed.clear_fields()
            embed.add_field(name=f"🔍 Zoom: {int(self.new_zoom)}   -   🎯  X: {self.new_pos_x}   -   🎯  Y: {self.new_pos_y}       ", value='')
            await interaction.response.edit_message(embed=embed, view=view, attachments=[new_file])    
        button_zoom_in.callback = button_callback_zoom_in
        
    def button_zoom_out(self, view, embed):  
        button_zoom_out = Button(label = f"-", style=discord.ButtonStyle.green)
        view.add_item(button_zoom_out)  
        async def button_callback_zoom_out(interaction):
            if self.new_zoom >= 2:
                self.new_zoom = int(self.new_zoom / 2)
                if self.new_pos_x < 0.5*1000/self.new_zoom:
                    self.new_pos_x = 0.5*1000/self.new_zoom
                if 1000 - self.new_pos_x < 0.5*1000/self.new_zoom:
                    self.new_pos_x = 1000 - 0.5*1000/self.new_zoom
                if self.new_pos_y < 0.5*1000/self.new_zoom:
                    self.new_pos_y = 0.5*1000/self.new_zoom
                if 1000 - self.new_pos_y < 0.5*1000/self.new_zoom:
                    self.new_pos_y = 1000 - 0.5*1000/self.new_zoom
            self.bot.galaxyCanvas.draw_map(self.new_zoom, self.new_pos_x, self.new_pos_y)
            new_file = discord.File("./Image/scout_map.png", filename="scout_map.png")
            button_zoom_out.callback = button_callback_zoom_out
            embed.clear_fields()
            embed.add_field(name=f"🔍 Zoom: {int(self.new_zoom)}   -   🎯  X: {self.new_pos_x}   -   🎯  Y: {self.new_pos_y}       ", value='')
            await interaction.response.edit_message(embed=embed, view=view, attachments=[new_file])    
        button_zoom_out.callback = button_callback_zoom_out

    def button_change_coords(self, view, embed): 
        button_change_coords = Button(label = f"🎯", style=discord.ButtonStyle.grey)  
        view.add_item(button_change_coords)
        async def button_callback_change_coords(interaction):
            class my_modal(ui.Modal, title='Change Coordinates 🔍'):
                pos_x=ui.TextInput(label='X coords', style=discord.TextStyle.short, placeholder='eg: 173', default="", required = True, max_length=3)
                pos_y=ui.TextInput(label='Y coords', style=discord.TextStyle.short, placeholder='eg: 62', default="", required = True, max_length=3)
                new_zoom = self.new_zoom
                display_zoom = self.new_zoom
                new_pos_x = self.new_pos_x
                new_pos_y = self.new_pos_y
                def update(canvas):    
                    size_x =  1000 / self.new_zoom
                    borders = [int(canvas.pos_x.value), 1000 - int(canvas.pos_x.value), int(canvas.pos_y.value), 1000 - int(canvas.pos_y.value)]
                    limit_size = min(borders)
                    if int(limit_size) < 0.5*size_x :
                        new_zoom_adapted = 1000 / (2*int(limit_size))
                        self.bot.galaxyCanvas.draw_map(new_zoom_adapted, int(canvas.pos_x.value), int(canvas.pos_y.value)) 
                        canvas.display_zoom = new_zoom_adapted
                        self.new_pos_x = int(canvas.pos_x.value)
                        self.new_pos_y = int(canvas.pos_y.value)
                    else:
                        self.bot.galaxyCanvas.draw_map(self.new_zoom, int(canvas.pos_x.value), int(canvas.pos_y.value))         
                async def on_submit(canvas, interaction):
                    canvas.update()
                    new_file = discord.File("./Image/scout_map.png", filename="scout_map.png")
                    embed.clear_fields()
                    embed.add_field(name=f"🔍 Zoom: {int(self.new_zoom)}   -   🎯  X: {self.new_pos_x}   -   🎯  Y: {self.new_pos_y}       ", value='')
                    self.new_zoom = canvas.display_zoom
                    await interaction.response.edit_message(embed=embed, view=view, attachments=[new_file])
            await interaction.response.send_modal(my_modal())
        button_change_coords.callback = button_callback_change_coords  
    
    def button_refresh(self, view, embed):
        button_refresh = Button(label = f"🔄️", style=discord.ButtonStyle.blurple)
        view.add_item(button_refresh)
        async def button_callback_refresh(interaction):
            self.bot.galaxyCanvas.update_lists() 
            self.bot.galaxyCanvas.draw_map(self.new_zoom, self.new_pos_x, self.new_pos_y)
            new_file = discord.File("./Image/scout_map.png", filename="scout_map.png")
            embed.clear_fields()
            button_refresh.callback = button_callback_refresh
            embed.add_field(name=f"🔍 Zoom: {int(self.new_zoom)}   -   🎯  X: {self.new_pos_x}   -   🎯  Y: {self.new_pos_y}       ", value='')
            await interaction.response.edit_message(embed=embed, view=view, attachments=[new_file]) 
        button_refresh.callback = button_callback_refresh
            
    #</editor-fold>

    #<editor-fold desc="command">

    @app_commands.command(name="colo_infos", description="Display the infos of the Colonies of a Cog_Player")
    @app_commands.describe(pseudo="Player's pseudo")
    @app_commands.autocomplete(pseudo=player_autocomplete)
    async def colo_infos(self, interaction: discord.Interaction, pseudo: str):
        if pseudo.strip() == "":
            await interaction.response.send_message(f"Cannot retreive infos of a Cog_Player with a pseudo composed only of whitespace.")
            return
        player: Player_Model = self.bot.galaxyLifeAPI.get_player_infos_from_name(pseudo)
        if player is None:
            await interaction.response.send_message(f"Player named {pseudo} not found.")
        else:
            colonies: List[Colony_Model] = list(self.bot.db.get_colonies({"id_gl": int(player['player_id_gl'])}))
            if len(colonies) == 0:
                await interaction.response.send_message(f"Colonies not found.")
            else:
                embed: discord.Embed
                embed = discord.Embed(title=f"Niv  : { pseudo }️", description="", color=Colors.gold, timestamp=datetime.datetime.now())
                it: int = 1
                for colony in colonies:
                    # colony['colo_sys_name'] != "-1" and colony['colo_sys_name'] != -1 and colony['colo_sys_name'] != "?" and 
                    if colony["updated"] != False or colony["colo_coord"]["x"] > -1:
                        embed.add_field(name=f"{ Emoji.colo.value if colony['colo_status'] == 'Up' else Emoji.down.value } Colonie {it} : {colony['colo_sys_name']}",value=f"({colony['colo_coord']['x']} ; {colony['colo_coord']['y']}) - SB ({colony['colo_lvl']})", inline=False)
                    it += 1
                await interaction.response.send_message(embed=embed)

    @app_commands.command(name="colo_update", description="Update an existent Cog_Colony")
    @app_commands.describe(pseudo="Player's pseudo", colo_number="if not found : ✅ run /player_infos and add its alliance ", colo_sys_name="Colony's system name (in CAPS)", colo_coord_x="Colony's x coordinate", colo_coord_y="Colony's y coordinate")
    @app_commands.autocomplete(pseudo=player_war_autocomplete, colo_number=colo_autocomplete)
    @app_commands.checks.has_any_role('Admin', 'Assistant')
    async def colo_update(self, interaction: discord.Interaction, pseudo: str, colo_number: int, colo_sys_name: str = "", colo_coord_x: int = -1, colo_coord_y: int = -1):
        if not self.bot.spec_role.admin_role(interaction.guild, interaction.user) and not self.bot.spec_role.assistant_role(interaction.guild, interaction.user):
            await interaction.response.send_message("You don't have the permission to use this command.")
            return
        if pseudo.strip() == "":
            await interaction.response.send_message(f"Cannot remove a Cog_Colony from Players with a pseudo composed only of whitespace.")
            return
        act_player: Player_Model = self.bot.db.get_one_player("pseudo", {"$regex": re.compile(pseudo, re.IGNORECASE)})
        if act_player is None:
            await interaction.response.send_message(f"Player named {pseudo} not found.")
        else:
            act_colony: List[Colony_Model] = list(self.bot.db.get_colonies({"_player_id": act_player['_id'], "number": colo_number}))
            if len(act_colony) == 0:
                await interaction.response.send_message(f"Colony not found.")
            else:
                act_colony = act_colony[0]
                act_colony["colo_sys_name"] = colo_sys_name.upper()
                act_colony["colo_coord"]["x"] = colo_coord_x
                act_colony["colo_coord"]["y"] = colo_coord_y
                if colo_coord_y != -1 and colo_coord_x != -1 and act_colony["colo_sys_name"] != "-1": 
                    act_colony["updated"] = True
                else:
                    act_colony["updated"] = False
                act_war: War_Model = self.bot.db.get_one_war("status", "InProgress")
                if act_war is not None:
                    act_colony["scouted"] = True
                self.bot.db.update_colony(act_colony)
                await interaction.response.send_message(f"Colony n°{colo_number} of {pseudo} updated.")
                # await self.bot.dashboard.update_Dashboard()

    # @app_commands.command(name="colony_remove", description="Remove an existent Cog_Colony")
    # @app_commands.describe(pseudo="Player's pseudo", colo_number="the number of the colony")
    # @app_commands.autocomplete(pseudo=player_autocomplete)
    # @app_commands.checks.has_any_role('Admin', 'Assistant')
    # async def colony_remove(self, interaction: discord.Interaction, pseudo: str, colo_number: int,):
    #     if not self.bot.spec_role.admin_role(interaction.guild, interaction.user) and not self.bot.spec_role.assistant_role(interaction.guild, interaction.user):
    #         await interaction.response.send_message("You don't have the permission to use this command.")
    #         return
    #     if pseudo.strip() == "":
    #         await interaction.response.send_message(f"Cannot remove a Cog_Colony from Players with a pseudo composed only of whitespace.")
    #         return
    #     act_player: Player_Model = self.bot.db.get_one_player("pseudo", pseudo)
    #     if act_player is None:
    #         await interaction.response.send_message(f"Player named {pseudo} not found.")
    #     else:
    #         obj: dict = {"_player_id": act_player['_id'], "number": colo_number}
    #         act_colony: List[Colony_Model] = list(self.bot.db.get_colonies(obj))
    #         if act_colony is None:
    #             await interaction.response.send_message(f"Colony not found.")
    #         else:
    #             self.bot.db.remove_colony(act_colony[0])
    #             await interaction.response.send_message(f"Player named {pseudo} as been removed.")
    #             await self.bot.dashboard.update_Dashboard()

    @app_commands.command(name="gift_colony", description="Gift colony to low level players / Or tell if a colony never has defenses")
    @app_commands.describe(pseudo="Player's pseudo", colo_number="Wich colony", gift_state="x")
    @app_commands.autocomplete(pseudo=player_war_autocomplete, colo_number=colo_autocomplete,  gift_state=gift_state_autocomplete)
    async def gift_colony(self, interaction: discord.Interaction, pseudo: str,colo_number: int, gift_state: str):
        act_player: Player_Model = self.bot.db.get_one_player("pseudo", pseudo)
        obj: dict = {"_player_id": act_player['_id'], "number": colo_number}
        act_colony: List[Colony_Model] = list(self.bot.db.get_colonies(obj))
        if act_player is None:
            await interaction.response.send_message(f"Player named {pseudo} does not exist.")
        else:
            act_colony = act_colony[0]
            act_colony["gift_state"]: str = gift_state
            self.bot.db.update_colony(act_colony)
            await self.log_channel.send(f"> <@&1089184438442786896> a new free colony has been added !! 🎁") #j'ai juste changé l'ordre 
            await interaction.response.send_message(f"The free state of colony n°{act_colony['number']} of {pseudo} has been updated.")
            
    @app_commands.command(name="colos_screened", description="How many colonies have been scouted yet")
    @app_commands.describe(zoom="zoom factor", pos_x="x position", pos_y="y position")
    async def colos_screened(self, interaction: discord.Interaction, zoom: int = 1, pos_x: int = 504, pos_y: int = 501  ):
        await interaction.response.defer()
        colo_number: List[Colony_Model] = list(self.bot.db.get_all_updated_colonies())
        colo_found_number: List[Colony_Model] = list(self.bot.db.get_all_found_colonies())
        self.bot.galaxyCanvas.update_lists() 
        alliance_dict: list =self.bot.galaxyCanvas.alliance_colonies() 
        self.bot.galaxyCanvas.draw_map(zoom, pos_x, pos_y)
        self.new_zoom = zoom
        self.new_pos_x = pos_x
        self.new_pos_y = pos_y
        embed = discord.Embed() #>>> **{len(colo_number)}** 🪐 colonies from enemy alliances have been updated yet.\n**{len(colo_found_number)}** 🪐 colonies found by screening \n**{len(colo_number)+len(colo_found_number)}** 🪐 colonies in total
        embed.add_field(name=f"🔍 Zoom: {int(self.new_zoom)}   -   🎯  X: {self.new_pos_x}   -   🎯  Y: {self.new_pos_y}       ", value='')
        view = View(timeout=None) 
        file = discord.File("./Image/scout_map.png", filename="scout_map.png")
        # embed.set_image(url="https://i.imgur.com/M0IqkRT.jpg")
        options: List[discord.SelectOption] = [ 
                discord.SelectOption(label=alliance_dict[0]["pseudo"], emoji="💫"),
                discord.SelectOption(label=alliance_dict[1]["pseudo"], emoji="💫"),
            ]
        for player in range(2,len(alliance_dict)):   
            if player < 25:
                options.append(discord.SelectOption(label=alliance_dict[player]["pseudo"], emoji="💫", default=False))
        async def my_callback(interaction):
            selected_players_list = []
            for player in range(0,len(alliance_dict)):  
                if alliance_dict[player]["pseudo"] in select.values:
                    selected_players_list.append(alliance_dict[player])
            self.new_zoom = self.bot.galaxyCanvas.draw_map(self.new_zoom, self.new_pos_x, self.new_pos_y, selected_players_list)
            new_file = discord.File("./Image/scout_map.png", filename="scout_map.png")
            embed.clear_fields()
            str_names: str = ""
            list_color: list = ["🔴 ","🟢 ","🟣 ","🔵 ","🟠 "]
            for name in range(0,len(select.values)):
                str_names = str_names + list_color[name%5] + str(select.values[name] + ", ")
            embed.add_field(name=f"🔍 Zoom: {int(self.new_zoom)}   -   🎯  X: {self.new_pos_x}   -   🎯  Y: {self.new_pos_y}       ", value=f'**Players selected:** {str_names}')
            await interaction.response.edit_message(embed=embed, attachments=[new_file])    
            # await interaction.response.send_message(f"callback working for {select.values[0]}")

        select = Select(min_values=1, max_values=len(alliance_dict), options = options)
        select.callback = my_callback
        view.add_item(select)
        self.button_zoom_in(view, embed)
        self.button_left(view, embed)
        self.button_down(view, embed)
        self.button_up(view, embed)
        self.button_right(view, embed)
        self.button_zoom_out(view, embed)
        self.button_change_coords(view, embed)
        self.button_refresh(view, embed)
        await interaction.followup.send(embed=embed, file=file, view=view)
    
    @app_commands.command(name="colo_founds_alliance", description="Find possible colonies in foundcolonies")
    @app_commands.describe(alliance="alliance name")
    async def colos_scouted(self, interaction: discord.Interaction, alliance: str):
        await interaction.response.defer()
        colo_found_number: List[Colony_Model] = list(self.bot.db.get_all_found_colonies())
        allianceDetails = self.bot.galaxyLifeAPI.get_alliance(alliance)
        for it_alliance in range(allianceDetails['alliance_size']):
            playerName = allianceDetails['members_list'][it_alliance]['Name']
            playerId = allianceDetails['members_list'][it_alliance]['Id']
            for it in range(len(colo_found_number)):
                if int(colo_found_number[it]["gl_id"]) == int(playerId): #renommer en id_gl dans db
                    await interaction.followup.send(f"🪐 **__(SB x):__**\n/colo_update pseudo:{playerName} colo_number:  colo_sys_name:  colo_coord_x:{colo_found_number[it]['X']} colo_coord_y:{colo_found_number[it]['Y']}\n")

        
        
    #</editor-fold>



async def setup(bot: commands.Bot):
    await bot.add_cog(Cog_Colony(bot), guilds=[discord.Object(id=os.getenv("SERVER_ID"))])