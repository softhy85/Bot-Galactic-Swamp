import os
from typing import List

import discord
import matplotlib.pyplot as plt
from discord import app_commands, ui
from discord.ext import commands, tasks
from discord.ui import Button, Select, View
from config.definitions import ROOT_DIR
from Models.Colony_Model import Colony_Model
print('root dir for cofg scout:', ROOT_DIR)

class Cog_Scout(commands.Cog):
    guild: discord.Guild = None
    bot: commands.bot = None

    def __init__(self, bot: commands.Bot):
        super().__init__()
        self.bot = bot

    #<editor-fold desc="listener">

    @commands.Cog.listener()
    async def on_ready(self):
        print("Cog Loaded: Cog_Scout")

    def button_right(self, view, embed):
            button_right = Button(label = f"⇨", style=discord.ButtonStyle.blurple)
            view.add_item(button_right)
            async def button_callback_right(interaction):
                await interaction.response.defer()
                self.retrieve_embed(embed)
                if self.new_pos_x + 0.5*int(1000/self.new_zoom) <= 1000 - 0.5*int(1000/self.new_zoom):
                    self.new_pos_x = self.new_pos_x + 0.5*int(1000/self.new_zoom)
                else: 
                    self.new_pos_x = 1000 - 0.5*int(1000/self.new_zoom)
                self.new_zoom, self.new_pos_x, self.new_pos_y, scout_x, scout_y, self.scout_player = self.bot.galaxyCanvas.draw_map(self.new_zoom, self.new_pos_x, self.new_pos_y)
                filename = "scout_map.png"
                new_file = discord.File(f"{os.path.join(ROOT_DIR, 'Image', filename)}", filename=filename)
                button_right.callback = button_callback_right
                embed.clear_fields()
                embed.add_field(name=f"🔍 Zoom: `{int(self.new_zoom)}`   -   🎯  X: `{int(self.new_pos_x)}`   -   🎯  Y: `{int(self.new_pos_y)}`       ", value='')
                await interaction.edit_original_response(embed=embed, view=view, attachments=[new_file]) 
            button_right.callback = button_callback_right

    def button_left(self, view, embed):
        button_left = Button(label = f"⇦", style=discord.ButtonStyle.blurple)
        view.add_item(button_left)
        async def button_callback_left(interaction):
            await interaction.response.defer()
            self.retrieve_embed(embed)
            if self.new_pos_x - 0.5*int(1000/self.new_zoom) >= 0.5*int(1000/self.new_zoom):
                self.new_pos_x = self.new_pos_x - 0.5*int(1000/self.new_zoom)
            else: 
                self.new_pos_x = 0.5*int(1000/self.new_zoom)
            self.new_zoom, self.new_pos_x, self.new_pos_y, scout_x, scout_y, self.scout_player = self.bot.galaxyCanvas.draw_map(self.new_zoom, self.new_pos_x, self.new_pos_y)
            filename = "scout_map.png"
            new_file = discord.File(f"{os.path.join(ROOT_DIR, 'Image', filename)}", filename=filename)
            button_left.callback = button_callback_left
            embed.clear_fields()
            embed.add_field(name=f"🔍 Zoom: `{int(self.new_zoom)}`   -   🎯  X: `{int(self.new_pos_x)}`   -   🎯  Y: `{int(self.new_pos_y)}`       ", value='')
            await interaction.edit_original_response(embed=embed, view=view, attachments=[new_file]) 
        button_left.callback = button_callback_left
    
    def button_down(self, view, embed):
        button_down = Button(label = f"⇩", style=discord.ButtonStyle.blurple)
        view.add_item(button_down)
        async def button_callback_down(interaction):
            await interaction.response.defer()
            self.retrieve_embed(embed)
            if self.new_pos_y + 0.5*int(1000/self.new_zoom) <= 1000 - 0.5*int(1000/self.new_zoom):
                self.new_pos_y = self.new_pos_y + 0.5*int(1000/self.new_zoom)
            else: 
                self.new_pos_y = 1000 - 0.5*int(1000/self.new_zoom)
            self.new_zoom, self.new_pos_x, self.new_pos_y, scout_x, scout_y, self.scout_player = self.bot.galaxyCanvas.draw_map(self.new_zoom, self.new_pos_x, self.new_pos_y)
            filename = "scout_map.png"
            new_file = discord.File(f"{os.path.join(ROOT_DIR, 'Image', filename)}", filename=filename)
            embed.clear_fields()
            button_down.callback = button_callback_down
            embed.add_field(name=f"🔍 Zoom: `{int(self.new_zoom)}`   -   🎯  X: `{int(self.new_pos_x)}`   -   🎯  Y: `{int(self.new_pos_y)}`       ", value='')
            await interaction.edit_original_response(embed=embed, view=view, attachments=[new_file]) 
        button_down.callback = button_callback_down

    def button_up(self, view, embed):
        button_up = Button(label = f"⇧", style=discord.ButtonStyle.blurple)
        view.add_item(button_up)
        async def button_callback_up(interaction):
            await interaction.response.defer()
            self.retrieve_embed(embed)
            if self.new_pos_y - 0.5*int(1000/self.new_zoom) >= 0.5*int(1000/self.new_zoom):
                self.new_pos_y = self.new_pos_y - 0.5*int(1000/self.new_zoom)
            else: 
                self.new_pos_y = 0.5*int(1000/self.new_zoom)
            self.new_zoom, self.new_pos_x, self.new_pos_y, scout_x, scout_y, self.scout_player = self.bot.galaxyCanvas.draw_map(self.new_zoom, self.new_pos_x, self.new_pos_y)
            filename = "scout_map.png"
            new_file = discord.File(f"{os.path.join(ROOT_DIR, 'Image', filename)}", filename=filename)
            embed.clear_fields()
            button_up.callback = button_callback_up
            embed.add_field(name=f"🔍 Zoom: `{int(self.new_zoom)}`   -   🎯  X: `{int(self.new_pos_x)}`   -   🎯  Y: `{int(self.new_pos_y)}`       ", value='')
            await interaction.edit_original_response(embed=embed, view=view, attachments=[new_file]) 
        button_up.callback = button_callback_up     
        
    def retrieve_embed(self, embed):
        name_str = str(embed.fields[0].name)
        splitted_name = name_str.split('`')   
        self.new_zoom = int(splitted_name[1])
        self.new_pos_x = int(splitted_name[3])
        self.new_pos_y = int(splitted_name[5])
        if embed.fields[0].value:
            value_str = str(embed.fields[0].value)
            splitted_value = value_str.split('`') 
            if len(splitted_value) > 5:
                self.scout_player_step = int(splitted_value[5])
           
    def button_zoom_in(self, view, embed):    
        button_zoom_in = Button(label = f"＋", style=discord.ButtonStyle.green)
        view.add_item(button_zoom_in)
        async def button_callback_zoom_in(interaction):
            await interaction.response.defer()
            self.retrieve_embed(embed)
            if self.new_zoom <= 100:
                self.new_zoom = self.new_zoom * 2
            self.new_zoom, self.new_pos_x, self.new_pos_y, scout_x, scout_y, self.scout_player = self.bot.galaxyCanvas.draw_map(self.new_zoom, self.new_pos_x, self.new_pos_y)
            filename = "scout_map.png"
            new_file = discord.File(f"{os.path.join(ROOT_DIR, 'Image', filename)}", filename=filename)
            button_zoom_in.callback = button_callback_zoom_in
            embed.clear_fields()
            embed.add_field(name=f"🔍 Zoom: `{int(self.new_zoom)}`   -   🎯  X: `{int(self.new_pos_x)}`   -   🎯  Y: `{int(self.new_pos_y)}`       ", value='')
            await interaction.edit_original_response(embed=embed, view=view, attachments=[new_file])     
        button_zoom_in.callback = button_callback_zoom_in
        
    def button_zoom_out(self, view, embed):  
        button_zoom_out = Button(label = f"-", style=discord.ButtonStyle.green)
        view.add_item(button_zoom_out)  
        async def button_callback_zoom_out(interaction):
            await interaction.response.defer()
            self.retrieve_embed(embed)
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
            self.new_zoom, self.new_pos_x, self.new_pos_y, scout_x, scout_y, self.scout_player = self.bot.galaxyCanvas.draw_map(self.new_zoom, self.new_pos_x, self.new_pos_y)
            filename = "scout_map.png"
            new_file = discord.File(f"{os.path.join(ROOT_DIR, 'Image', filename)}", filename=filename)
            button_zoom_out.callback = button_callback_zoom_out
            embed.clear_fields()
            embed.add_field(name=f"🔍 Zoom: `{int(self.new_zoom)}`   -   🎯  X: `{int(self.new_pos_x)}`   -   🎯  Y: `{int(self.new_pos_y)}`       ", value='')
            await interaction.edit_original_response(embed=embed, view=view, attachments=[new_file])     
        button_zoom_out.callback = button_callback_zoom_out

    def button_change_coords(self, view, embed): 
        button_change_coords = Button(label = f"🎯", style=discord.ButtonStyle.grey)  
        view.add_item(button_change_coords)
        async def button_callback_change_coords(interaction):
            self.retrieve_embed(embed)
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
                        self.new_zoom, self.new_pos_x, self.new_pos_y, scout_x, scout_y, self.scout_player = self.bot.galaxyCanvas.draw_map(self.new_zoom, int(canvas.pos_x.value), int(canvas.pos_y.value))         
                async def on_submit(canvas, interaction):
                    await interaction.response.defer()
                    canvas.update()
                    filename = "scout_map.png"
                    new_file = discord.File(f"{os.path.join(ROOT_DIR, 'Image', filename)}", filename=filename)
                    embed.clear_fields()
                    self.new_zoom = canvas.display_zoom
                    embed.add_field(name=f"🔍 Zoom: `{int(self.new_zoom)}`   -   🎯  X: `{int(self.new_pos_x)}`   -   🎯  Y: `{int(self.new_pos_y)}`       ", value='')
                    
                    await interaction.edit_original_response(embed=embed, view=view, attachments=[new_file]) 
            await interaction.response.send_modal(my_modal())
        button_change_coords.callback = button_callback_change_coords  

    def button_scout_player(self, view, embed): 
        button_change_coords = Button(label = f"", style=discord.ButtonStyle.grey)  
        view.add_item(button_change_coords)
        async def button_callback_change_coords(interaction):
            self.retrieve_embed(embed)
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
                        self.new_zoom, self.new_pos_x, self.new_pos_y, scout_x, scout_y = self.bot.galaxyCanvas.draw_map(new_zoom_adapted, int(canvas.pos_x.value), int(canvas.pos_y.value)) 
                        canvas.display_zoom = self.new_zoom
                        self.new_pos_x = int(canvas.pos_x.value)
                        self.new_pos_y = int(canvas.pos_y.value)
                    else:
                        self.new_zoom, self.new_pos_x, self.new_pos_y, scout_x, scout_y = self.bot.galaxyCanvas.draw_map(self.new_zoom, int(canvas.pos_x.value), int(canvas.pos_y.value))         
                async def on_submit(canvas, interaction):
                    await interaction.response.defer()
                    canvas.update()
                    filename = "scout_map.png"
                    new_file = discord.File(f"{os.path.join(ROOT_DIR, 'Image', filename)}", filename=filename)
                    embed.clear_fields()
                    embed.add_field(name=f"🔍 Zoom: `{int(self.new_zoom)}`   -   🎯  X: `{int(self.new_pos_x)}`   -   🎯  Y: `{int(self.new_pos_y)}`       ", value='')
                    self.new_zoom = canvas.display_zoom
                    await interaction.edit_original_response(embed=embed, view=view, attachments=[new_file]) 
            await interaction.response.send_modal(my_modal())
        button_change_coords.callback = button_callback_change_coords  
    
    def button_refresh(self, view, embed):
        button_refresh = Button(label = f"🔄️", style=discord.ButtonStyle.grey)
        view.add_item(button_refresh)
        async def button_callback_refresh(interaction):
            await interaction.response.defer()
            self.retrieve_embed(embed)
            self.bot.galaxyCanvas.update_lists() 
            if self.scout_player_step:
                self.scout_player_step = self.scout_player_step - 1
            self.new_zoom, self.new_pos_x, self.new_pos_y, scout_x, scout_y, self.scout_player = self.bot.galaxyCanvas.draw_map(self.new_zoom, self.new_pos_x, self.new_pos_y, scout_player_step=self.scout_player_step)
            filename = "scout_map.png"
            new_file = discord.File(f"{os.path.join(ROOT_DIR, 'Image', filename)}", filename=filename)
            embed.clear_fields()
            button_refresh.callback = button_callback_refresh
            embed.add_field(name=f"🔍 Zoom: `{int(self.new_zoom)}`   -   🎯  X: `{int(self.new_pos_x)}`   -   🎯  Y: `{int(self.new_pos_y)}`       ", value='')
            await interaction.edit_original_response(embed=embed, view=view, attachments=[new_file]) 
        button_refresh.callback = button_callback_refresh
        
    def button_scout(self, view, embed):
        button_scout = Button(label = f"🔍", style=discord.ButtonStyle.grey)
        view.add_item(button_scout)
        async def button_callback_scout(interaction):
            await interaction.response.defer()
            self.retrieve_embed(embed)
            self.bot.galaxyCanvas.update_lists() 
            self.new_zoom, self.new_pos_x, self.new_pos_y, scout_x, scout_y, self.scout_player  = self.bot.galaxyCanvas.draw_map(self.new_zoom, self.new_pos_x, self.new_pos_y, scout=True)
            filename = "scout_map.png"
            new_file = discord.File(f"{os.path.join(ROOT_DIR, 'Image', filename)}", filename=filename)
            embed.clear_fields()
            button_scout.callback = button_callback_scout
            embed.add_field(name=f"🔍 Zoom: `{int(self.new_zoom)}`   -   🎯  X: `{int(self.new_pos_x)}`   -   🎯  Y: `{int(self.new_pos_y)}`       ", value=f'Coords to enter: `{scout_x}` : `{scout_y}`')
            await interaction.edit_original_response(embed=embed, view=view, attachments=[new_file]) 
        button_scout.callback = button_callback_scout

    def button_complete_general(self, view, embed):
        button_complete = Button(label = f"✅", style=discord.ButtonStyle.grey)
        view.add_item(button_complete)
        async def button_callback_complete(interaction):
            await interaction.response.defer()
            self.retrieve_embed(embed)
            value_str = str(embed.fields[0].value)
            splitted_value = value_str.split('`')   
            self.bot.galaxyCanvas.mark_area_complete((int(splitted_value[1])-6)/12, (int(splitted_value[3])-3)/6) 
            self.new_zoom, self.new_pos_x, self.new_pos_y, scout_x, scout_y, self.scout_player  = self.bot.galaxyCanvas.draw_map(self.new_zoom, self.new_pos_x, self.new_pos_y, scout=True)
            filename = "scout_map.png"
            new_file = discord.File(f"{os.path.join(ROOT_DIR, 'Image', filename)}", filename=filename)
            embed.clear_fields()
            button_complete.callback = button_callback_complete
            embed.add_field(name=f"🔍 Zoom: `{int(self.new_zoom)}`   -   🎯  X: `{int(self.new_pos_x)}`   -   🎯  Y: `{int(self.new_pos_y)}`       ", value=f'Coords to enter: `{scout_x}` : `{scout_y}`')
            await interaction.edit_original_response(embed=embed, view=view, attachments=[new_file]) 
        button_complete.callback = button_callback_complete

    def button_complete_player(self, view, embed):
        button_complete = Button(label = f"✅", style=discord.ButtonStyle.grey)
        view.add_item(button_complete)
        async def button_callback_complete_player(interaction):
            await interaction.response.defer()
            self.retrieve_embed(embed)
            #self.bot.galaxyCanvas.update_lists() 
            zoom, pos_x, pos_y, scout_x, scout_y, self.scout_player = self.bot.galaxyCanvas.draw_map(self.new_zoom, self.new_pos_x, self.new_pos_y, scout_player_step=self.scout_player_step)
            filename = "scout_map.png"
            new_file = discord.File(f"{os.path.join(ROOT_DIR, 'Image', filename)}", filename=filename)
            embed.clear_fields()
            button_complete.callback = button_callback_complete_player
            embed.add_field(name=f"🔍 Zoom: `{int(self.new_zoom)}`   -   🎯  X: `{int(self.new_pos_x)}`   -   🎯  Y: `{int(self.new_pos_y)}`       ", value=f"Coords to enter: `{int(self.scout_player['list_x'][-1])}` : `{int(self.scout_player['list_y'][-1])}` - Step: `{len(self.scout_player['list_x'])}` / `25`")
            await interaction.edit_original_response(embed=embed, view=view, attachments=[new_file]) 
        button_complete.callback = button_callback_complete_player

    def button_render(self, view, embed):
        button_render = Button(label = f"📹", style=discord.ButtonStyle.grey)
        view.add_item(button_render)
        async def button_callback_render(interaction):
            await interaction.response.defer()
            self.retrieve_embed(embed)
            self.new_zoom, self.new_pos_x, self.new_pos_y, scout_x, scout_y, self.scout_player = self.bot.galaxyCanvas.draw_map(self.new_zoom, self.new_pos_x, self.new_pos_y, render=True)
            filename = "scout_map.png"
            new_file = discord.File(f"{os.path.join(ROOT_DIR, 'Image', filename)}", filename=filename)
            button_render.callback = button_callback_render
            embed.clear_fields()
            embed.add_field(name=f"🔍 Zoom: `{int(self.new_zoom)}`   -   🎯  X: `{int(self.new_pos_x)}`   -   🎯  Y: `{int(self.new_pos_y)}`       ", value='')
            await interaction.edit_original_response(embed=embed, view=view, attachments=[new_file]) 
        button_render.callback = button_callback_render
    
    @app_commands.command(name="scout_player", description="Search around a player's main base to find colonies. This acts as a tool")
    @app_commands.describe(pos_x="x position", pos_y="y position", player="player username (used as a reminder)")
    async def scout_player(self, interaction: discord.Interaction, pos_x: int, pos_y: int, player: str = ""):
        await interaction.response.defer()
        self.bot.galaxyCanvas.update_lists() 
        zoom = int(1008/(2*2*12+12+12))
        scout_player: dict = {'list_x': [], 'list_y': []}
        self.scout_player = scout_player
        zoom, pos_x, pos_y, scout_x, scout_y, scout_player = self.bot.galaxyCanvas.draw_map(zoom, pos_x, pos_y, scout_player_step=0)
        self.new_zoom = zoom
        self.new_pos_x = pos_x
        self.new_pos_y = pos_y
        if player != "":
            title = "➡️ `" + player + "`"
            embed = discord.Embed(title=title)
        else:
            embed = discord.Embed()
        
        embed.add_field(name=f"🔍 Zoom: `{int(self.new_zoom)}`   -   🎯  X: `{int(self.new_pos_x)}`   -   🎯  Y: `{int(self.new_pos_y)}`       ", value=f"Coords to enter: `{int(scout_player['list_x'][-1])}` : `{int(scout_player['list_y'][-1])}` - Step: `{len(scout_player['list_x'])}` / `25`")
        view = View(timeout=None) 
        filename = "scout_map.png"
        file = discord.File(f"{os.path.join(ROOT_DIR, 'Image', filename)}", filename=filename)
        self.button_complete_player(view, embed)
        self.button_refresh(view, embed)
        await interaction.followup.send(embed=embed, file=file, view=view)
        
    @app_commands.command(name="scout", description="How many colonies have been scouted yet")
    @app_commands.describe(zoom="zoom factor", pos_x="x position", pos_y="y position")
    async def scout(self, interaction: discord.Interaction, zoom: int = 1, pos_x: int = 504, pos_y: int = 501  ):
        await interaction.response.defer()
        self.scout_player_step = None
        self.bot.galaxyCanvas.update_lists() 
        alliance_dict: list = self.bot.galaxyCanvas.alliance_colonies() 
        self.bot.galaxyCanvas.draw_map(zoom, pos_x, pos_y)
        self.new_zoom = zoom
        self.new_pos_x = pos_x
        self.new_pos_y = pos_y
        embed = discord.Embed()
        embed.add_field(name=f"🔍 Zoom: `{int(self.new_zoom)}`   -   🎯  X: `{int(self.new_pos_x)}`   -   🎯  Y: `{int(self.new_pos_y)}`       ", value='')
        view = View(timeout=None) 
        filename = "scout_map.png"
        file = discord.File(f"{os.path.join(ROOT_DIR, 'Image', filename)}", filename=filename)
        if alliance_dict is not None:
            options: List[discord.SelectOption] = [ 
                    discord.SelectOption(label=alliance_dict[0]["pseudo"], emoji="💫"),
                    discord.SelectOption(label=alliance_dict[1]["pseudo"], emoji="💫"),
                ]
            for player in range(2, len(alliance_dict)):   
                if player < 25:
                    options.append(discord.SelectOption(label=alliance_dict[player]["pseudo"], emoji="💫", default=False))
            async def my_callback(interaction):
                selected_players_list = []
                for player in range(0,len(alliance_dict)):  
                    if alliance_dict[player]["pseudo"] in select.values:
                        selected_players_list.append(alliance_dict[player])
                self.new_zoom, self.new_pos_x, self.new_pos_y, scout_x, scout_y, self.scout_player = self.bot.galaxyCanvas.draw_map(self.new_zoom, self.new_pos_x, self.new_pos_y, selected_players_list)
                filename = "scout_map.png"
                new_file = discord.File(f"{os.path.join(ROOT_DIR, 'Image', filename)}", filename=filename)
                embed.clear_fields()
                str_names: str = ""
                list_color: list = ["🔴 ","🟢 ","🟣 ","🔵 ","🟠 "]
                for name in range(0,len(select.values)):
                    str_names = str_names + list_color[name%5] + str(select.values[name] + ", ")
                embed.add_field(name=f"🔍 Zoom: `{int(self.new_zoom)}`   -   🎯  X: `{int(self.new_pos_x)}`   -   🎯  Y: `{int(self.new_pos_y)}`       ", value=f'**Players selected:** {str_names}')
                await interaction.response.edit_message(embed=embed, attachments=[new_file])    
            select = Select(min_values=1, max_values=len(alliance_dict), options = options, placeholder="Choose a war opponent")
            select.callback = my_callback
            view.add_item(select)
        self.button_left(view, embed)
        self.button_down(view, embed)
        self.button_up(view, embed)
        self.button_right(view, embed)
        self.button_change_coords(view, embed)
        self.button_zoom_in(view, embed)
        self.button_zoom_out(view, embed)
        self.button_refresh(view, embed)
        self.button_scout(view, embed)
        self.button_complete_general(view, embed)
        self.button_render(view, embed)
        await interaction.followup.send(embed=embed, file=file, view=view)
    
async def setup(bot: commands.Bot):
    await bot.add_cog(Cog_Scout(bot), guilds=[discord.Object(id=os.getenv("SERVER_ID"))])