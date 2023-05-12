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
from Models.Completed_List_Model import Completed_List_Model
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
from datetime import datetime
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
    self.ally_alliance_name = os.getenv("ALLY_ALLIANCE_NAME")   

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
    limit_x: int = 10
    limit_y: int = 15
    scout_size: int = 1
    colo_number_threshold = 1.
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
                        for x_check in completed_list['list_x']:
                          if x == x_check:
                            for y_check in completed_list['list_y']:
                              if y == y_check:
                                completed = True
                                break
                          if completed:
                            break
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
    list_x_store: Colonies_List_Model = {"name": "x", "list": self.list_x}
    list_y_store: Colonies_List_Model = {"name": "y", "list": self.list_y}
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
  
  def draw_recap(self):
    fig,ax = plt.subplots(1)
    ax.tick_params(axis='x', colors='white')
    ax.tick_params(axis='y', colors='white')
    plt.yticks(fontsize=5)
    plt.xticks(fontsize=5, )
    list = self.bot.db.get_warlog()  
    
    def number_formatter(data_value, indx):
      if data_value >= 1_000:
        formatter = '{:1.0f}K'.format(data_value/1000)
      else:
        formatter = '{:1.0f}'.format(data_value)
      return formatter
        
    it: int = 0
    for it in range (0, len(list['timestamp'])):
      list['timestamp'][it] = datetime.strftime(list['timestamp'][it],  "%m/%d-%H:%M")
    fig.set_figwidth(4)
    fig.set_figheight(1)
    plt.plot(list['timestamp'], list['ally_score'], color='#5eff79', label='ally')
    plt.plot(list['timestamp'], list['enemy_score'], color='#d348fa', label='enemy')
    plt.legend(fontsize="5")
    ax.set_facecolor("#2b2e31")
    ax.yaxis.set_major_formatter(number_formatter)
    ax.xaxis.set_major_locator(plt.MaxNLocator(3))
    ax.yaxis.set_major_locator(plt.MaxNLocator(5))
    # plt.draw()
    plt.savefig('./Image/war_recap.png', bbox_inches='tight', dpi=300, facecolor="#424549", edgecolor="black")
    # plt.show()
  
  def draw_map(self, zoom, pos_x, pos_y, players_list=None, scout=False):
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
    if scout == True:
      pos_x, pos_y, scout_size, scout_x, scout_y = self.locate_area(ax, myHist)
    else:
      scout_x = 0
      scout_y = 0
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
      ax.add_patch(Rectangle(((pos_x - temp_size_x - 40), (pos_y - temp_size_y - 40)), 2*temp_size_x + 80, 2*temp_size_y + 80, facecolor='none', edgecolor='white', linewidth=3))
      or_x = pos_x - temp_size_x - 40
      or_y = pos_y - temp_size_y - 40
      max_x = pos_x + temp_size_x + 40
      max_y = pos_y + temp_size_y + 40
      win_size = 2*temp_size_x + 80
      zoom = max(list[0]["list"] + list[1]["list"])/win_size
      if or_x < 0:
        or_x = 0
      if or_y < 0:
        or_y = 0
      if max_x > max(list[0]["list"]):
        max_x = max(list[0]["list"])
      if max_y > max(list[1]["list"]):
        max_y = max(list[1]["list"])
      # print(f"window: ({pos_x - temp_size_x - 40};{pos_y - temp_size_y - 40} - ({pos_x + temp_size_x + 40};{pos_y + temp_size_y + 40}")
    elif scout == True:
      or_x = pos_x - scout_size*12
      max_x = pos_x + scout_size*12
      if or_x < 0:
        or_x = 0
      if max_x > max(list[0]["list"]):
        max_x = max(list[0]["list"])
      win_size = max_x - or_x 
      or_y = pos_y - int(win_size/2)
      max_y = pos_y + int(win_size/2)
      if or_y < 0:
        or_y = 0
        max_y = win_size
      if max_y > max(list[1]["list"]):
        or_y = max(list[1]["list"]) - win_size
        max_y = max(list[1]["list"])
      pos_x = (or_x + max_x)/2
      pos_y = (or_y + max_y)/2
      zoom = max(list[0]["list"] + list[1]["list"])/(win_size)  
    else:
      or_x = pos_x - 0.5*max(list[0]["list"] + list[1]["list"])/zoom
      or_y = pos_y - 0.5*max(list[1]["list"] + list[1]["list"])/zoom
      max_x = pos_x + 0.5*max(list[0]["list"] + list[1]["list"])/zoom
      max_y = pos_y + 0.5*max(list[1]["list"] + list[1]["list"])/zoom
      if or_x < 0:
        or_x = 0
      if or_y < 0:
        or_y = 0
      if max_x > max(list[0]["list"]):
        max_x = max(list[0]["list"])
      if max_y > max(list[1]["list"]):
        max_y = max(list[1]["list"])
      pos_x = (or_x + max_x)/2
      pos_y = (or_y + max_y)/2
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
    return (int(zoom), pos_x, pos_y, scout_x, scout_y)