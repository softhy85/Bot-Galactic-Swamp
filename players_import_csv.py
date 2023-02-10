import csv
from typing import List
from models.Player_Model import Player_Model
from src.DataBase import DataBase

header: List[str] = []
db = DataBase()

with open('players.csv', newline='') as csvfile:
    spamreader = csv.reader(csvfile, delimiter=';')
    it_row: int = 0
    for row in spamreader:
        it_col: int = 0
        columns: List[str]
        if it_row == 0:
            header = columns
        else:
            player: Player_Model = {}
            for column in columns:
                if column.strip() != "" and column is not None:
                    player[header[it_col]] = column
                it_col += 1
            if player["pseudo"] != "" and player["pseudo"] is not None:
                db.push_new_player(player)
        it_row += 1