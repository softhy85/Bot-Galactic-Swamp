from typing import List
from dotenv import load_dotenv
from Utils.DataBase import DataBase
import math
from matplotlib.colors import ListedColormap
import re
import matplotlib
import matplotlib as mpl
import matplotlib.pyplot as plt
from discord.ext import commands
from Models.Alliance_Model import Alliance_Model
from Models.Colony_Model import Colony_Model
from Models.Player_Model import Player_Model
from Models.Colonies_List_Model import Colonies_List_Model
import os
from matplotlib.patches import Rectangle

import discord
from discord.ext import commands
import datetime
import time
from Utils.Dropdown import DropView
from Models.War_Model import War_Model
from Models.Alliance_Model import Alliance_Model
from Models.Player_Model import Player_Model
from Models.Colony_Model import Colony_Model
from Models.InfoMessage_Model import InfoMessage_Model
from pymongo.cursor import Cursor
from typing import List
from Models.Colors import Colors
import math
import asyncio
import random as random
load_dotenv()

class GalaxyCanvas:

  def __init__(self, bot: commands.Bot):
    self.bot = bot
    self.list_x = list()
    self.list_y = list()
    self.list_x_player = list()
    self.list_y_player = list()   

  def plot_scouted_colonies(self, size_x, size_y):  
      for it in range(0, len(self.all_colonies)):
        if "x" in self.all_colonies[it]['colo_coord']:
          if self.all_colonies[it]["updated"] == True:
            if self.all_colonies[it]["colo_coord"]["x"] != -1 and self.all_colonies[it]["colo_coord"]["x"] != "-1" and self.all_colonies[it]["colo_coord"]["y"] != -1 and self.all_colonies[it]["colo_coord"]["y"] != "-1":
              if self.all_colonies[it]["colo_coord"]["x"] <=  size_x and  self.all_colonies[it]["colo_coord"]["y"] <= size_y:
                self.list_x.append(self.all_colonies[it]['colo_coord']['x'])
                self.list_y.append(self.all_colonies[it]['colo_coord']['y'])
            
  def plot_found_colonies(self, size_x, size_y):
      it = 0
      for it in range(len(self.colo_db)):
        if self.colo_db[it]["X"] != -1:
          if self.colo_db[it]["X"] <=  size_x and self.colo_db[it]["Y"] <=  size_y:
            self.list_x.append(self.colo_db[it]["X"])
            self.list_y.append(self.colo_db[it]["Y"])

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

            
  def alliance_colonies(self): 
    alliance = 'JE SUIS TON FILS'
    alliance_info: Alliance_Model = self.bot.db.get_one_alliance("name", alliance)
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
    
  def update_lists(self):
    self.all_colonies = list(self.bot.db.get_all_updated_colonies())
    self.colo_db: List = list(self.bot.db.get_all_found_colonies())
    size_y = 1002
    size_x = 1008
    self.list_x: list = []
    self.list_y: list = []
    self.plot_found_colonies( size_x, size_y) # fix that, freezing/
    self.plot_scouted_colonies( size_x, size_y)
    list_x_store: Colonies_List_Model = {"name": "x", "list": self.list_x}
    list_y_store: Colonies_List_Model = {"name": "y", "list": self.list_y}
    self.bot.db.push_colonies_list(list_x_store)
    self.bot.db.push_colonies_list(list_y_store)
    
  def draw_map(self, zoom, pos_x, pos_y, players_list=None):
    obj = None
    list = self.bot.db.get_colonies_list(obj)
    size_x: int = max(list[0]["list"]) / zoom
    size_y: int = max(list[1]["list"]) / zoom
    fig,ax = plt.subplots(1)
    ax.xaxis.tick_top()
    ax.tick_params(axis='x', colors='white', direction="in", pad=-12)
    ax.tick_params(axis='y', colors='white', direction="in", pad=-27)
    ax.locator_params(axis='x', nbins=5)
    ax.locator_params(axis='y', nbins=5)
    cmap = ListedColormap(["#000000","#00163e","#012c79","#012c79", "#0140b0", "#0140b0", "#0244ba", "#0244ba", "#0244ba", "#0244ba"])
    cmap_black = ListedColormap(["#000000"])
    
    

    myHist, xedges, yedges, image  = plt.hist2d(list[0]["list"], list[1]["list"], bins=[84,167], cmap="inferno",  norm = mpl.colors.Normalize(vmin=0, vmax=10)) #, range=[[0, 100], [0, 100]] #,  norm = mpl.colors.Normalize(vmin=0, vmax=10)
    # Empty_zone_locator:
    x: int = 0
    y: int = 0
    it: int = 0
    for hist_column in myHist:
      for hist_line in hist_column:
        y = 0
        while y <= 10: 
          if hist_line == 0:
            
            it = 0
            while it < 3:
              if myHist[x][y] == 0:
                it += 1
                x += 1
              else: 
                break
          if it >= 3:
            print(x*12 - (it+1)*12,y*6 - (it+1)*6)
            ax.add_patch(Rectangle((x*12- (it+1)*12, y*6- (it+1)*6), (it+1)*12, 6, facecolor='none', edgecolor='white', linewidth=3))
            break
          
          y += 1
        if it >= 3:
            break
          
      x += 1
      
      if it >= 3:
        break
    # else:
    #   myHist, xedges, yedges, image  = plt.hist2d(list[0]["list"], list[1]["list"], bins=[84,167], cmap=cmap_black,  norm = mpl.colors.Normalize(vmin=0, vmax=10)) #, range=[[0, 100], [0, 100]] #,  norm = mpl.colors.Normalize(vmin=0, vmax=10)

    
    # previous blue: c2e4ff
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
      # prendre le max de longueur relative a pos_x et pos_y: il faut refaire la liste
      for it in range(0, len(total_list_x)):
        total_list_x[it] = abs(int(total_list_x[it]) - pos_x)
      for it in range(0, len(total_list_y)):
        total_list_y[it] = abs(int(total_list_y[it]) - pos_y)
      temp_size_x: int = max(total_list_y + total_list_x) #- int(min(total_list_x))
      temp_size_y: int = max(total_list_y + total_list_x) #- int(min(total_list_y))
      print(f"pos_x: {pos_x} - temp_size_x :{temp_size_x} - total_list_x :{total_list_x}\npos y : {pos_y} - temp_size_y :{temp_size_y} - total_list_y :{total_list_y}")
      ax.add_patch(Rectangle(((pos_x - temp_size_x - 40), (pos_y - temp_size_y - 40)), 2*temp_size_x + 80, 2*temp_size_y + 80, facecolor='none', edgecolor='white', linewidth=3))
      or_x = pos_x - temp_size_x - 40
      or_y = pos_y - temp_size_y - 40
      max_x = pos_x + temp_size_x + 40
      max_y = pos_y + temp_size_y + 40
      win_size = 2*temp_size_x + 80
      zoom = max(list[0]["list"] + list[1]["list"])/win_size
      print(zoom)
      if or_x < 0:
        or_x = 0
      if or_y < 0:
        or_y = 0
      if max_x > max(list[0]["list"]):
        max_x = max(list[0]["list"])
      if max_y > max(list[1]["list"]):
        max_y = max(list[1]["list"])
    
      
      print(f"window: ({pos_x - temp_size_x - 40};{pos_y - temp_size_y - 40} - ({pos_x + temp_size_x + 40};{pos_y + temp_size_y + 40}")
    else:
      or_x = pos_x - 0.5*size_x
      or_y = pos_y - 0.5*size_y
      max_x = pos_x + 0.5*size_x
      max_y = pos_y + 0.5*size_y

    
       
    plt.axis([or_x, max_x, max_y, or_y])
      # if int(pos_x) < 0.5*size_x :
      #     pos_x =  0.5*size_x
      # if int(pos_y) < 0.5*size_y :
      #   pos_y =  0.5*size_y
      # if int(pos_x) > 1008 - 0.5*size_x :
      #   pos_x =  1008 - 0.5*size_x
      # if int(pos_y) > 1002 - 0.5*size_y :
      #   pos_y =  1002 - 0.5*size_y
    plt.scatter(list[0]["list"], list[1]["list"], color = '#c88944', alpha=1, s=1*zoom)
    plt.plot(pos_x, pos_y, 'w+', markersize=25)
    plt.yticks(fontsize=8)
    plt.xticks(fontsize=8)
    plt.savefig('./Image/scout_map.png', bbox_inches='tight', dpi=100, edgecolor="black", facecolor="#2b2e31")
    return int(zoom)