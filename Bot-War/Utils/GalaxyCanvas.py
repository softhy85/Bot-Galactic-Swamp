import asyncio
import datetime
import math
import os
import random as random
import re
import time
from datetime import datetime
from typing import List

import discord
import matplotlib
import matplotlib as mpl
import matplotlib.dates as mdates
import matplotlib.image as mpimg
import matplotlib.pyplot as plt
from discord.ext import commands
from dotenv import load_dotenv
from matplotlib.colors import ListedColormap
from matplotlib.patches import Rectangle
from pymongo.cursor import Cursor
from config.definitions import ROOT_DIR
from Models.Alliance_Model import Alliance_Model
from Models.Colonies_List_Model import Colonies_List_Model
from Models.Colony_Model import Colony_Model
from Models.Colors import Colors
from Models.Completed_List_Model import Completed_List_Model
from Models.InfoMessage_Model import InfoMessage_Model
from Models.Player_Model import Player_Model
from Models.War_Model import War_Model
from Utils.DataBase import DataBase
from Utils.Dropdown import DropView

load_dotenv()
print("root dir for gl canvas:", ROOT_DIR)
class GalaxyCanvas:

  def __init__(self, bot: commands.Bot):
    self.bot = bot
    self.list_x_found = list()
    self.list_y_found = list()
    self.list_x_scouted = list()
    self.list_y_scouted = list()
    self.list_x_player = list()
    self.list_y_player = list()
    self.ally_alliance_name = os.getenv("ALLY_ALLIANCE_NAME")  
    self.program_path: str = os.getenv("PROGRAM_PATH") 

  def plot_scouted_colonies(self, size_x, size_y):  
      for it in range(0, len(self.all_colonies)):
        if "x" in self.all_colonies[it]['colo_coord']:
          if self.all_colonies[it]["updated"] == True:
            if self.all_colonies[it]["colo_coord"]["x"] != -1 and self.all_colonies[it]["colo_coord"]["x"] != "-1" and self.all_colonies[it]["colo_coord"]["y"] != -1 and self.all_colonies[it]["colo_coord"]["y"] != "-1":
              if self.all_colonies[it]["colo_coord"]["x"] <=  size_x and  self.all_colonies[it]["colo_coord"]["y"] <= size_y:
                self.list_x_scouted.append(self.all_colonies[it]['colo_coord']['x'])
                self.list_y_scouted.append(self.all_colonies[it]['colo_coord']['y'])
            
  def plot_found_colonies(self, size_x, size_y):
      it = 0
      for it in range(len(self.colo_db)):
        if self.colo_db[it]["X"] != -1:
          if self.colo_db[it]["X"] <=  size_x and self.colo_db[it]["Y"] <=  size_y:
            self.list_x_found.append(self.colo_db[it]["X"])
            self.list_y_found.append(self.colo_db[it]["Y"])
          

  def my_colonies(self, zoom, color, player=None):
    list_x_player = []
    list_y_player = []   
    return_value: dict = {} 
    list_x_player = list_x_player + list(player["x"])
    list_y_player = list_y_player + list(player["y"])
    plt.scatter(list_x_player, list_y_player, color = color, alpha=0.8, s=30*zoom)
    return_value["x"] = list_x_player
    return_value["y"] = list_y_player
    return return_value

  def scout_player(self, scout_player_step, pos_x, pos_y, zoom):
    list_step = {'x': [0, -1, -1, -1, 0, 0, 1, 1, 1, -2, -2, -2, -2, -2, -1, -1, 0, 0, 1, 1, 2, 2, 2, 2, 2 ],
                 'y': [0, -1, 0, 1, -1, 1, -1, 0, 1, -2, -1, 0, 1, 2, -2, 2, -2, 2, -2, 2, -2, -1, 0, 1, 2]
                 }
    screen_width = 12
    screen_height = 6
    scout_player: dict = {}
    scout_player['list_x'] = []
    scout_player['list_y'] = []
    for it in range(0, scout_player_step + 1):
      scout_player['list_x'].append(pos_x + list_step["x"][it]* screen_width)
      scout_player['list_y'].append(pos_y + list_step["y"][it]* screen_height)
    scout_player['step'] = scout_player_step + 1
    return scout_player
            
  def alliance_colonies(self): 
    api_info = self.bot.galaxyLifeAPI.get_alliance(self.ally_alliance_name)
    if api_info['war_status'] != False:
      alliance_info: Alliance_Model = self.bot.db.get_one_alliance("name", api_info["enemy_name"].upper())
      obj: dict = {"_alliance_id": alliance_info["_id"]}
      players: List[Player_Model] = self.bot.db.get_players(obj)
      alliance_dict: list = []
      for player in players:
        list_x= list()
        list_y= list()
        obj: dict = {"_player_id": player["_id"]}
        colonies: List[Colony_Model] = list(self.bot.db.get_colonies(obj))
        for colo in colonies:
            if colo['colo_coord']['x'] != -1:
              list_x.append(colo['colo_coord']['x'])
              list_y.append(colo['colo_coord']['y'])
        if list_x != []:
          dict_player = {"pseudo":player["pseudo"], "x":list_x, "y":list_y}
          alliance_dict.append(dict_player)
      return alliance_dict
    else:
      return None
  
  def locate_area(self, ax, myHist):
    x: int = 0
    y: int = 0
    x_found: int = 0
    y_found: int = 0
    limit_x: int = 21
    limit_y: int = 42
    scout_size: int = 1
    colo_number_threshold = 2.
    found = False
    obj = {"name":"completed_list"}
    completed_list: dict = self.bot.db.get_completed_list(obj)
    if limit_x > len(myHist) - 1 or limit_y > len(myHist[0]) - 1:
      return
    for x in range(0, limit_x):
        for y in range(0,  limit_y):
            for size in range(0, scout_size):
                if len(myHist) - 1 > x + size:
                    if myHist[x + size][y] > colo_number_threshold:
                        break
                    else:
                      completed = False
                      if completed_list:
                        x_index = 0
                        for x_check in completed_list['list_x']:
                          if x == x_check:
                            if y == completed_list['list_y'][x_index]:
                              completed = True
                              break
                          if completed:
                            break
                          x_index += 1  
                      if completed: 
                        break
                else:
                    break
                if size == scout_size - 1:
                    found = True
                    x_found = x
                    y_found = y
            if found:
                break
        if found:
            break
    if found:
        print("(", x_found, " ,", y_found, ")", sep="")
        ax.add_patch(Rectangle((x_found*12, y_found*6), scout_size*12, 6, facecolor='none', edgecolor='white', linewidth=3))
    if scout_size < 3:
      scout_size = 3
    return (x_found*12, y_found*6, scout_size, x_found*12 + 6, y_found*6 + 3)

  def update_lists(self):
    self.all_colonies = list(self.bot.db.get_all_updated_colonies())
    self.colo_db: List = list(self.bot.db.get_all_found_colonies())
    size_y = 1002
    size_x = 1008
    self.list_x: list = []
    self.list_y: list = []
    self.plot_found_colonies( size_x, size_y) # fix that, freezing/
    self.plot_scouted_colonies( size_x, size_y)
    list_x_store: Colonies_List_Model = {"name": "x", "list_found": self.list_x_found, "list_scouted": self.list_x_scouted}
    list_y_store: Colonies_List_Model = {"name": "y", "list_found": self.list_y_found, "list_scouted": self.list_y_scouted}
    self.bot.db.push_colonies_list(list_x_store)
    self.bot.db.push_colonies_list(list_y_store)
    
  def mark_area_complete(self, screen_x, screen_y):
    obj = {"name":"completed_list"}
    completed_list: dict = self.bot.db.get_completed_list(obj)
    if completed_list:
      completed_list['list_x'].append(screen_x)
      completed_list['list_y'].append(screen_y)
      self.bot.db.update_completed_list(completed_list)
    else:
      completed_list: Completed_List_Model = {'name':'completed_list', 'list_x': [screen_x], 'list_y':[screen_y]}
      self.bot.db.push_completed_list(completed_list)
  
  def number_formatter(self, data_value, indx):
      if data_value >= 1_000:
        formatter = '{:1.0f}K'.format(data_value/1000)
      else:
        formatter = '{:1.0f}'.format(data_value)
      return formatter
    
  def draw_recap(self):
    fig,ax = plt.subplots(1)
    ax.tick_params(axis='y', colors='white', bottom=False)
    ax.spines['right'].set_color('#222224')
    ax.spines['left'].set_color('#222224')
    ax.spines['top'].set_color('#222224')
    ax.spines['bottom'].set_color('#222224')
    ax.yaxis.tick_right()
    ax.yaxis.set_major_formatter(self.number_formatter)
    ax.yaxis.set_major_locator(plt.MaxNLocator(3))
    ax.set_facecolor("#222224")
    fig.set_figwidth(4)
    fig.set_figheight(1)
    ax.axes.get_xaxis().set_ticks([])
    ax.axes.get_yaxis().set_ticks([])
    list_diff = []
    red_list_timestamp = []
    red_list = []
    threshold = 0
    list = self.bot.db.get_warlog()  
    it: int = 0
    for it in range (0, len(list['timestamp'])):
      list['timestamp'][it] = datetime.strftime(list['timestamp'][it],  "%m/%d-%H:%M")
    for i, j in zip(list['ally_score'], list['enemy_score']):
      list_diff.append(i - j)
    for index, it in enumerate(list_diff):
      if it < threshold:
        red_list.append(list_diff[index])
        red_list_timestamp.append(list['timestamp'][index])
    plt.plot(list['timestamp'], list_diff, color='#5eff79', label='ally')
    if red_list != []:
      plt.plot(red_list_timestamp, red_list, label='ally', color='r', marker='o',markersize=1) #
      ax.axhline(y=threshold, color='#222224')
      ax.axhline(y=threshold, color='w', linestyle=":")
    plt.subplots_adjust(bottom=0, right=1, top=1, left=0)
    filename = 'war_recap.png'
    plt.savefig(f'{os.path.join(ROOT_DIR, "Image", filename)}', bbox_inches='tight', dpi=300, facecolor="#222224")
    plt.close('all')
  
  def draw_map(self, zoom, pos_x, pos_y, players_list=None, scout=False, scout_player_step=None, radius=None):
    obj = None
    list = self.bot.db.get_colonies_list(obj)
    list_all = {"x": list[0]['list_found'] + list[0]['list_scouted'], "y": list[1]['list_found'] + list[1]['list_scouted']}
    obj = {"name":"completed_list"}
    completed_list: dict = self.bot.db.get_completed_list(obj)
    size_x: int = max(list_all["x"]) / zoom
    size_y: int = max(list_all["y"]) / zoom
    fig,ax = plt.subplots(1)
    ax.xaxis.tick_top()
    ax.tick_params(axis='x', colors='white', direction="in", pad=-12)
    ax.tick_params(axis='y', colors='white', direction="in", pad=-27)
    ax.locator_params(axis='x', nbins=5)
    ax.locator_params(axis='y', nbins=5)
    cmap = ListedColormap(["#000000","#00163e","#012c79","#012c79", "#0140b0", "#0140b0", "#0244ba", "#0244ba", "#0244ba", "#0244ba"])
    cmap_black = ListedColormap(["#000000"])
    if scout_player_step is None:
      myHist, xedges, yedges, image  = plt.hist2d(list_all['x'], list_all["y"], bins=[84,167], cmap='inferno',  norm = mpl.colors.Normalize(vmin=0, vmax=10)) #, range=[[0, 100], [0, 100]] #,  norm = mpl.colors.Normalize(vmin=0, vmax=10)
      for it in range(0, len(completed_list['list_x'])):
        ax.add_patch(Rectangle((completed_list['list_x'][it]*12, completed_list['list_y'][it]*6), 12, 6, facecolor='#130136'))
    else:
      ax.add_patch(Rectangle((0, 0), 1008, 1004, facecolor='black'))
    if scout == True:
      pos_x, pos_y, scout_size, scout_x, scout_y = self.locate_area(ax, myHist)
    else:
      scout_x = 0
      scout_y = 0
    if scout_player_step is not None:
      scout_player = self.scout_player(scout_player_step, pos_x, pos_y, zoom)
    else:
      scout_player = None
    if players_list != None:
      total_list_x: list = []
      total_list_y: list = []
      color: list = ["#ff080c","#10ff08","#7f03fc","#036bfc","#fc5603"]
      for player in range(0, len(players_list)):
        list_players: list = self.my_colonies(zoom, color[player%5], players_list[player])
        total_list_x +=  list_players['x']
        total_list_y +=  list_players['y'] 
      pos_x: int = int((max(total_list_x)+min(total_list_x))/2)
      pos_y: int = int((max(total_list_y)+min(total_list_y))/2)
      for it in range(0, len(total_list_x)):
        total_list_x[it] = abs(int(total_list_x[it]) - pos_x)
      for it in range(0, len(total_list_y)):
        total_list_y[it] = abs(int(total_list_y[it]) - pos_y)
      temp_size_x: int = max(total_list_y + total_list_x) 
      temp_size_y: int = max(total_list_y + total_list_x) 
      # print(f"pos_x: {pos_x} - temp_size_x :{temp_size_x} - total_list_x :{total_list_x}\npos y : {pos_y} - temp_size_y :{temp_size_y} - total_list_y :{total_list_y}")
      # ax.add_patch(Rectangle(((pos_x - temp_size_x - 40), (pos_y - temp_size_y - 40)), 2*temp_size_x + 80, 2*temp_size_y + 80, facecolor='none', edgecolor='white', linewidth=3))
      or_x = pos_x - temp_size_x - 40
      or_y = pos_y - temp_size_y - 40
      max_x = pos_x + temp_size_x + 40
      max_y = pos_y + temp_size_y + 40
      win_size = 2*temp_size_x + 80
      zoom = max(list_all["x"] + list_all["y"])/win_size
      if or_x < 0:
        or_x = 0
      if or_y < 0:
        or_y = 0
      if max_x > max(list_all["x"]):
        max_x = max(list_all["x"])
      if max_y > max(list_all["y"]):
        max_y = max(list_all["y"])
    elif scout == True:
      or_x = pos_x - scout_size*12
      max_x = pos_x + scout_size*12
      if or_x < 0:
        or_x = 0
      if max_x > max(list_all["x"]):
        max_x = max(list_all["x"])
      win_size = max_x - or_x 
      or_y = pos_y - int(win_size/2)
      max_y = pos_y + int(win_size/2)
      if or_y < 0:
        or_y = 0
        max_y = win_size
      if max_y > max(list_all["y"]):
        or_y = max(list_all["y"]) - win_size
        max_y = max(list_all["y"])
      pos_x = (or_x + max_x)/2
      pos_y = (or_y + max_y)/2
      zoom = max(list_all["x"] + list_all["y"])/(win_size)  
    else:
      or_x = pos_x - 0.5*max(list_all["x"] + list_all["y"])/zoom
      or_y = pos_y - 0.5*max(list_all["y"] + list_all["y"])/zoom
      max_x = pos_x + 0.5*max(list_all["x"] + list_all["y"])/zoom
      max_y = pos_y + 0.5*max(list_all["y"] + list_all["y"])/zoom
      if or_x < 0:
        or_x = 0
      if or_y < 0:
        or_y = 0
      if max_x > max(list_all["x"]):
        max_x = max(list_all["x"])
      if max_y > max(list_all["y"]):
        max_y = max(list_all["y"])
      pos_x = (or_x + max_x)/2
      pos_y = (or_y + max_y)/2
    if scout_player_step is not None:
      if len(scout_player['list_x']) > 1:
        for it in range(0, len(scout_player["list_x"])-1):
          ax.add_patch(Rectangle(((scout_player["list_x"][it] - 6), scout_player["list_y"][it] - 3), 12, 6, facecolor='#25b373'))
      ax.add_patch(Rectangle(((scout_player["list_x"][-1] - 6), scout_player["list_y"][-1] - 3), 12, 6, facecolor='none', edgecolor='white', linewidth=3))  
    plt.axis([or_x, max_x, max_y, or_y])
    plt.scatter(list[0]["list_scouted"], list[1]["list_scouted"], color = '#c88944', alpha=1, s=1*zoom)
    plt.scatter(list[0]["list_found"], list[1]["list_found"], color = '#49b02c', alpha=1, s=1*zoom)
    plt.plot(pos_x, pos_y, 'w+', markersize=25)
    plt.yticks(fontsize=8)
    plt.xticks(fontsize=8)
    filename =  'scout_map.png'
    plt.savefig(f'{os.path.join(ROOT_DIR, "Image", filename)}', bbox_inches='tight', dpi=100, edgecolor="black", facecolor="#2b2e31")
    plt.close('all')
    return (int(zoom), pos_x, pos_y, scout_x, scout_y, scout_player)