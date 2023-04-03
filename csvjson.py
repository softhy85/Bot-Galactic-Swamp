import requests
import json
import os
import datetime
from typing import List

import discord
from discord import app_commands
from discord.ext import commands
from discord.ext.commands import Context
from dotenv import load_dotenv

from Utils.Alliance import Alliance
from Utils.DataBase import DataBase
from Utils.GalaxyLifeAPI import GalaxyLifeAPI
from Models.Alliance_Model import Alliance_Model

steamToken = "B8D87A555C403CD7C16250A103F3A5E7"
colo_db: dict = [
  {
    "PlanetId": 35,
    "OwnerId": 146530,
    "X": 180,
    "Y": 187,
    "Info": "(sb4)"
  },
  {
    "PlanetId": 36,
    "OwnerId": 146530,
    "X": 190,
    "Y": 199,
    "Info": "(sb1)"
  },
  {
    "PlanetId": 47,
    "OwnerId": 53521,
    "X": 419,
    "Y": 184,
    "Info": "(sb4)"
  },
  {
    "PlanetId": 48,
    "OwnerId": 53521,
    "X": 415,
    "Y": 187,
    "Info": "(sb3)"
  },
  {
    "PlanetId": 49,
    "OwnerId": 53521,
    "X": 417,
    "Y": 187,
    "Info": "(sb3) (geen verdediging)"
  },
  {
    "PlanetId": 50,
    "OwnerId": 48295,
    "X": 362,
    "Y": 236,
    "Info": "(sb4) = main planet solar system"
  },
  {
    "PlanetId": 51,
    "OwnerId": 48295,
    "X": 364,
    "Y": 236,
    "Info": "(sb3)"
  },
  {
    "PlanetId": 52,
    "OwnerId": 60690,
    "X": 296,
    "Y": 335,
    "Info": "(sb4)"
  },
  {
    "PlanetId": 53,
    "OwnerId": 60690,
    "X": 295,
    "Y": 334,
    "Info": "(sb3)"
  },
  {
    "PlanetId": 54,
    "OwnerId": 58724,
    "X": 230,
    "Y": 247,
    "Info": "(sb5)"
  },
  {
    "PlanetId": 55,
    "OwnerId": 58724,
    "X": 233,
    "Y": 250,
    "Info": "(sb4)"
  },
  {
    "PlanetId": 56,
    "OwnerId": 107223,
    "X": 203,
    "Y": 462,
    "Info": "(sb3)"
  },
  {
    "PlanetId": 57,
    "OwnerId": 140407,
    "X": 224,
    "Y": 2,
    "Info": "(sb3)"
  },
  {
    "PlanetId": 58,
    "OwnerId": 40331,
    "X": 239,
    "Y": 396,
    "Info": "(sb2) = main planet solar system"
  },
  {
    "PlanetId": 59,
    "OwnerId": 40500,
    "X": 433,
    "Y": 346,
    "Info": "(sb3) (geen verdediging) = main planet solar system"
  },
  {
    "PlanetId": 60,
    "OwnerId": 40500,
    "X": 429,
    "Y": 346,
    "Info": "(sb3) (free starbase)"
  },
  {
    "PlanetId": 63,
    "OwnerId": 129142,
    "X": 180,
    "Y": 372,
    "Info": ""
  },
  {
    "PlanetId": 64,
    "OwnerId": 144645,
    "X": 115,
    "Y": 256,
    "Info": "(sb3) = main planet solar system"
  },
  {
    "PlanetId": 65,
    "OwnerId": 144645,
    "X": 120,
    "Y": 254,
    "Info": "(sb3)"
  },
  {
    "PlanetId": 66,
    "OwnerId": 144483,
    "X": 8,
    "Y": 97,
    "Info": "(sb4)"
  },
  {
    "PlanetId": 67,
    "OwnerId": 144507,
    "X": 448,
    "Y": 519,
    "Info": "(sb4) = main planet solar system"
  },
  {
    "PlanetId": 68,
    "OwnerId": 44775,
    "X": 530,
    "Y": 319,
    "Info": "(sb3)"
  },
  {
    "PlanetId": 69,
    "OwnerId": 122544,
    "X": 81,
    "Y": 413,
    "Info": "(sb3) = main planet solar system + free starbae"
  },
  {
    "PlanetId": 70,
    "OwnerId": 122544,
    "X": 80,
    "Y": 411,
    "Info": "(sb4) = free starbase"
  },
  {
    "PlanetId": 71,
    "OwnerId": 111302,
    "X": 297,
    "Y": 58,
    "Info": "(sb2)"
  },
  {
    "PlanetId": 75,
    "OwnerId": 100744,
    "X": 109,
    "Y": 164,
    "Info": "(sb5)"
  },
  {
    "PlanetId": 76,
    "OwnerId": 100744,
    "X": 106,
    "Y": 164,
    "Info": "(sb4)"
  },
  {
    "PlanetId": 77,
    "OwnerId": 100744,
    "X": 123,
    "Y": 175,
    "Info": "(sb4)"
  },
  {
    "PlanetId": 78,
    "OwnerId": 39538,
    "X": 105,
    "Y": 170,
    "Info": "(sb3)"
  },
  {
    "PlanetId": 79,
    "OwnerId": 39538,
    "X": 106,
    "Y": 172,
    "Info": "(sb4)"
  },
  {
    "PlanetId": 80,
    "OwnerId": 80444,
    "X": 219,
    "Y": 70,
    "Info": "(sb4)"
  },
  {
    "PlanetId": 81,
    "OwnerId": 141369,
    "X": 392,
    "Y": 527,
    "Info": "(sb4)"
  },
  {
    "PlanetId": 85,
    "OwnerId": 111027,
    "X": 418,
    "Y": 122,
    "Info": "1st"
  },
  {
    "PlanetId": 86,
    "OwnerId": 111027,
    "X": 432,
    "Y": 154,
    "Info": "2nd"
  },
  {
    "PlanetId": 87,
    "OwnerId": 165416,
    "X": 161,
    "Y": 165,
    "Info": "1st"
  },
  {
    "PlanetId": 88,
    "OwnerId": 39459,
    "X": -1,
    "Y": -1,
    "Info": "(witte / vectalite kristallen planeet, zie afbeelding) = 1ste of 2de colony"
  },
  {
    "PlanetId": 89,
    "OwnerId": 39459,
    "X": 392,
    "Y": 215,
    "Info": "3th colony"
  },
  {
    "PlanetId": 90,
    "OwnerId": 39459,
    "X": 415,
    "Y": 187,
    "Info": "4th colony"
  },
  {
    "PlanetId": 91,
    "OwnerId": 148189,
    "X": 109,
    "Y": 398,
    "Info": "- main"
  },
  {
    "PlanetId": 92,
    "OwnerId": 148189,
    "X": 109,
    "Y": 398,
    "Info": "- 1st"
  },
  {
    "PlanetId": 93,
    "OwnerId": 148189,
    "X": 107,
    "Y": 400,
    "Info": "- 2nd"
  },
  {
    "PlanetId": 94,
    "OwnerId": 148189,
    "X": 107,
    "Y": 400,
    "Info": "- 3rd"
  },
  {
    "PlanetId": 95,
    "OwnerId": 148189,
    "X": 108,
    "Y": 402,
    "Info": "- 4rd"
  },
  {
    "PlanetId": 96,
    "OwnerId": 148228,
    "X": 422,
    "Y": 130,
    "Info": "- main"
  },
  {
    "PlanetId": 97,
    "OwnerId": 148228,
    "X": 422,
    "Y": 130,
    "Info": "- 1st (lage defense, defense bunkers allemaal leeg)"
  },
  {
    "PlanetId": 98,
    "OwnerId": 148228,
    "X": 423,
    "Y": 128,
    "Info": "- 2nd (lage defense, defense bunkers allemaal leeg)"
  },
  {
    "PlanetId": 100,
    "OwnerId": 152990,
    "X": 162,
    "Y": 354,
    "Info": "- main"
  },
  {
    "PlanetId": 101,
    "OwnerId": 152990,
    "X": 166,
    "Y": 354,
    "Info": "- 1st"
  },
  {
    "PlanetId": 106,
    "OwnerId": 88193,
    "X": 334,
    "Y": 198,
    "Info": "- main (vriendbunker leeg andere bunkers vol, defense lvl 4-5)"
  },
  {
    "PlanetId": 108,
    "OwnerId": 88011,
    "X": 126,
    "Y": 340,
    "Info": "- main (vriendebunker leeg, andere bunkers half vol, top bunker unknown)"
  },
  {
    "PlanetId": 109,
    "OwnerId": 88011,
    "X": 130,
    "Y": 339,
    "Info": "- 4rd (no defense)"
  },
  {
    "PlanetId": 117,
    "OwnerId": 192789,
    "X": 340,
    "Y": 389,
    "Info": "- main (mixed defense lvls, bunkers half vol)"
  },
  {
    "PlanetId": 118,
    "OwnerId": 192789,
    "X": 340,
    "Y": 389,
    "Info": "- 1st (vriendenbunker)"
  },
  {
    "PlanetId": 119,
    "OwnerId": 192789,
    "X": 344,
    "Y": 387,
    "Info": "- 2nd (almost no defense)"
  },
  {
    "PlanetId": 120,
    "OwnerId": 192789,
    "X": 335,
    "Y": 338,
    "Info": "- 3rd (almost no defense)"
  },
  {
    "PlanetId": 121,
    "OwnerId": 88817,
    "X": 412,
    "Y": 527,
    "Info": "- main (defense lvl 3, bunkers leeg)"
  },
  {
    "PlanetId": 122,
    "OwnerId": 88817,
    "X": 411,
    "Y": 530,
    "Info": "- 1st (wel defense, no bunkers)"
  },
  {
    "PlanetId": 123,
    "OwnerId": 88817,
    "X": 412,
    "Y": 530,
    "Info": "- 2nd (some defense, no bunkers)"
  },
  {
    "PlanetId": 128,
    "OwnerId": 90564,
    "X": 407,
    "Y": 407,
    "Info": "- main (vriendenbunker leeg andere bunkers vol, defense lvl 5)"
  },
  {
    "PlanetId": 129,
    "OwnerId": 90564,
    "X": 407,
    "Y": 407,
    "Info": "- 1st (vriendebunker leeg, defense laag)"
  },
  {
    "PlanetId": 130,
    "OwnerId": 90564,
    "X": 406,
    "Y": 410,
    "Info": "- 2nd (lage defense)"
  },
  {
    "PlanetId": 131,
    "OwnerId": 90564,
    "X": 401,
    "Y": 407,
    "Info": "- 3rd (lage defense)"
  },
  {
    "PlanetId": 132,
    "OwnerId": 90564,
    "X": 402,
    "Y": 406,
    "Info": "- 4th (lvl 1)"
  },
  {
    "PlanetId": 134,
    "OwnerId": 90578,
    "X": 307,
    "Y": 513,
    "Info": "- main (defense lvl 1, bunkers leeg)"
  },
  {
    "PlanetId": 135,
    "OwnerId": 90578,
    "X": 305,
    "Y": 514,
    "Info": "- 3rd (some defense)"
  },
  {
    "PlanetId": 136,
    "OwnerId": 90578,
    "X": 305,
    "Y": 512,
    "Info": "- 4th (defense, no bunkers)"
  },
  {
    "PlanetId": 137,
    "OwnerId": 40176,
    "X": 414,
    "Y": 405,
    "Info": "main"
  },
  {
    "PlanetId": 138,
    "OwnerId": 40176,
    "X": 414,
    "Y": 405,
    "Info": "1st"
  },
  {
    "PlanetId": 141,
    "OwnerId": 55932,
    "X": 26,
    "Y": 281,
    "Info": "- main"
  },
  {
    "PlanetId": 142,
    "OwnerId": 55932,
    "X": 436,
    "Y": 321,
    "Info": "- 1st (bunkers zijn half vol)"
  },
  {
    "PlanetId": 143,
    "OwnerId": 77929,
    "X": 285,
    "Y": 189,
    "Info": "main"
  },
  {
    "PlanetId": 144,
    "OwnerId": 77929,
    "X": 45,
    "Y": 53,
    "Info": 1
  },
  {
    "PlanetId": 145,
    "OwnerId": 77929,
    "X": 82,
    "Y": 81,
    "Info": 2
  },
  {
    "PlanetId": 149,
    "OwnerId": 193082,
    "X": 20,
    "Y": 65,
    "Info": "main"
  },
  {
    "PlanetId": 150,
    "OwnerId": 193082,
    "X": 21,
    "Y": 64,
    "Info": 1
  },
  {
    "PlanetId": 151,
    "OwnerId": 193082,
    "X": 23,
    "Y": 66,
    "Info": 2
  },
  {
    "PlanetId": 152,
    "OwnerId": 193082,
    "X": 26,
    "Y": 65,
    "Info": 3
  },
  {
    "PlanetId": 155,
    "OwnerId": 82286,
    "X": 28,
    "Y": 357,
    "Info": "main"
  },
  {
    "PlanetId": 156,
    "OwnerId": 82286,
    "X": 28,
    "Y": 357,
    "Info": 1
  },
  {
    "PlanetId": 157,
    "OwnerId": 82286,
    "X": 46,
    "Y": 359,
    "Info": 2
  },
  {
    "PlanetId": 163,
    "OwnerId": 55296,
    "X": 26,
    "Y": 358,
    "Info": 2
  },
  {
    "PlanetId": 164,
    "OwnerId": 55296,
    "X": 77,
    "Y": 340,
    "Info": 5
  },
  {
    "PlanetId": 165,
    "OwnerId": 55296,
    "X": 95,
    "Y": 335,
    "Info": 6
  },
  {
    "PlanetId": 175,
    "OwnerId": 47672,
    "X": 377,
    "Y": 408,
    "Info": "main"
  },
  {
    "PlanetId": 176,
    "OwnerId": 47672,
    "X": 468,
    "Y": 327,
    "Info": 1
  },
  {
    "PlanetId": 177,
    "OwnerId": 47672,
    "X": 51,
    "Y": 247,
    "Info": 2
  },
  {
    "PlanetId": 178,
    "OwnerId": 47672,
    "X": 266,
    "Y": 249,
    "Info": 3
  },
  {
    "PlanetId": 179,
    "OwnerId": 47672,
    "X": 525,
    "Y": 47,
    "Info": 4
  },
  {
    "PlanetId": 180,
    "OwnerId": 47672,
    "X": 101,
    "Y": 15,
    "Info": 5
  },
  {
    "PlanetId": 181,
    "OwnerId": 47672,
    "X": 310,
    "Y": 334,
    "Info": 6
  },
  {
    "PlanetId": 182,
    "OwnerId": 47672,
    "X": 428,
    "Y": 17,
    "Info": 7
  },
  {
    "PlanetId": 183,
    "OwnerId": 47672,
    "X": 113,
    "Y": 229,
    "Info": 8
  },
  {
    "PlanetId": 184,
    "OwnerId": 192511,
    "X": 244,
    "Y": 410,
    "Info": "- main"
  },
  {
    "PlanetId": 185,
    "OwnerId": 192511,
    "X": 225,
    "Y": 225,
    "Info": "- 1e"
  },
  {
    "PlanetId": 186,
    "OwnerId": 192511,
    "X": 451,
    "Y": 450,
    "Info": "- 2e"
  },
  {
    "PlanetId": 187,
    "OwnerId": 192511,
    "X": 226,
    "Y": 449,
    "Info": "- 3e"
  },
  {
    "PlanetId": 188,
    "OwnerId": 192511,
    "X": 451,
    "Y": 675,
    "Info": "- 4e"
  },
  {
    "PlanetId": 189,
    "OwnerId": 219270,
    "X": 749,
    "Y": 611,
    "Info": 1
  },
  {
    "PlanetId": 190,
    "OwnerId": 169424,
    "X": 435,
    "Y": 189,
    "Info": 1
  },
  {
    "PlanetId": 191,
    "OwnerId": 167309,
    "X": 226,
    "Y": 182,
    "Info": 4
  },
  {
    "PlanetId": 192,
    "OwnerId": 169423,
    "X": 268,
    "Y": 379,
    "Info": 3
  },
  {
    "PlanetId": 193,
    "OwnerId": 194979,
    "X": 220,
    "Y": 67,
    "Info": "- main"
  },
  {
    "PlanetId": 194,
    "OwnerId": 194979,
    "X": 217,
    "Y": 68,
    "Info": "- 1st"
  },
  {
    "PlanetId": 195,
    "OwnerId": 194979,
    "X": 212,
    "Y": 67,
    "Info": "- 2nd"
  },
  {
    "PlanetId": 196,
    "OwnerId": 139237,
    "X": 340,
    "Y": 478,
    "Info": "- main"
  },
  {
    "PlanetId": 197,
    "OwnerId": 139237,
    "X": 340,
    "Y": 478,
    "Info": "- 1st"
  },
  {
    "PlanetId": 198,
    "OwnerId": 139237,
    "X": 344,
    "Y": 477,
    "Info": "- 2nd"
  },
  {
    "PlanetId": 199,
    "OwnerId": 139237,
    "X": 343,
    "Y": 477,
    "Info": "- 3rd"
  },
  {
    "PlanetId": 200,
    "OwnerId": 91163,
    "X": 150,
    "Y": 475,
    "Info": "- main"
  },
  {
    "PlanetId": 201,
    "OwnerId": 91163,
    "X": 150,
    "Y": 475,
    "Info": "- 1st"
  },
  {
    "PlanetId": 202,
    "OwnerId": 91163,
    "X": 152,
    "Y": 472,
    "Info": "- 2nd"
  },
  {
    "PlanetId": 203,
    "OwnerId": 91163,
    "X": 147,
    "Y": 473,
    "Info": "- 3rd"
  },
  {
    "PlanetId": 204,
    "OwnerId": 91163,
    "X": 148,
    "Y": 473,
    "Info": "- 4th"
  },
  {
    "PlanetId": 211,
    "OwnerId": 190368,
    "X": 164,
    "Y": 320,
    "Info": "- main"
  },
  {
    "PlanetId": 212,
    "OwnerId": 190368,
    "X": 99,
    "Y": 193,
    "Info": "- 1st"
  },
  {
    "PlanetId": 213,
    "OwnerId": 190368,
    "X": 169,
    "Y": 319,
    "Info": "- 3rd"
  },
  {
    "PlanetId": 214,
    "OwnerId": 190368,
    "X": 167,
    "Y": 320,
    "Info": "- 4th"
  },
  {
    "PlanetId": 215,
    "OwnerId": 191480,
    "X": 99,
    "Y": 193,
    "Info": "- main"
  },
  {
    "PlanetId": 216,
    "OwnerId": 191480,
    "X": 103,
    "Y": 198,
    "Info": "- 1st"
  },
  {
    "PlanetId": 217,
    "OwnerId": 191480,
    "X": 164,
    "Y": 320,
    "Info": "- 2nd"
  },
  {
    "PlanetId": 218,
    "OwnerId": 191480,
    "X": 96,
    "Y": 192,
    "Info": "- 3rd"
  },
  {
    "PlanetId": 219,
    "OwnerId": 191480,
    "X": 91,
    "Y": 195,
    "Info": "- 4th"
  },
  {
    "PlanetId": 220,
    "OwnerId": 118325,
    "X": 252,
    "Y": 398,
    "Info": "- main"
  },
  {
    "PlanetId": 221,
    "OwnerId": 118325,
    "X": 252,
    "Y": 398,
    "Info": "- 1st"
  },
  {
    "PlanetId": 222,
    "OwnerId": 118325,
    "X": 253,
    "Y": 397,
    "Info": "- 2nd"
  },
  {
    "PlanetId": 225,
    "OwnerId": 134197,
    "X": 41,
    "Y": 217,
    "Info": "- main"
  },
  {
    "PlanetId": 226,
    "OwnerId": 134197,
    "X": 41,
    "Y": 217,
    "Info": "- 1st"
  },
  {
    "PlanetId": 227,
    "OwnerId": 134197,
    "X": 41,
    "Y": 216,
    "Info": "- 2nd"
  },
  {
    "PlanetId": 228,
    "OwnerId": 134197,
    "X": 40,
    "Y": 220,
    "Info": "- 3rd"
  },
  {
    "PlanetId": 230,
    "OwnerId": 198954,
    "X": 402,
    "Y": 519,
    "Info": "- main"
  },
  {
    "PlanetId": 231,
    "OwnerId": 198954,
    "X": 399,
    "Y": 519,
    "Info": "- 1st"
  },
  {
    "PlanetId": 232,
    "OwnerId": 198954,
    "X": 399,
    "Y": 520,
    "Info": "- 2nd"
  },
  {
    "PlanetId": 233,
    "OwnerId": 113790,
    "X": 10,
    "Y": 467,
    "Info": "- main"
  },
  {
    "PlanetId": 234,
    "OwnerId": 113790,
    "X": 10,
    "Y": 467,
    "Info": "- 5th"
  },
  {
    "PlanetId": 235,
    "OwnerId": 61170,
    "X": 251,
    "Y": 532,
    "Info": "- main"
  },
  {
    "PlanetId": 236,
    "OwnerId": 61170,
    "X": 246,
    "Y": 531,
    "Info": "- 2nd"
  },
  {
    "PlanetId": 247,
    "OwnerId": 189032,
    "X": 43,
    "Y": 20,
    "Info": 1
  },
  {
    "PlanetId": 250,
    "OwnerId": 96308,
    "X": 476,
    "Y": 387,
    "Info": "- main"
  },
  {
    "PlanetId": 251,
    "OwnerId": 96308,
    "X": 46,
    "Y": 132,
    "Info": 2
  },
  {
    "PlanetId": 252,
    "OwnerId": 49546,
    "X": 39,
    "Y": 32,
    "Info": 1
  },
  {
    "PlanetId": 253,
    "OwnerId": 49546,
    "X": 29,
    "Y": 31,
    "Info": 2
  },
  {
    "PlanetId": 254,
    "OwnerId": 49546,
    "X": 3,
    "Y": 19,
    "Info": 7
  },
  {
    "PlanetId": 255,
    "OwnerId": 49546,
    "X": 17,
    "Y": 19,
    "Info": 5
  },
  {
    "PlanetId": 261,
    "OwnerId": 148996,
    "X": 351,
    "Y": 122,
    "Info": "- main"
  },
  {
    "PlanetId": 262,
    "OwnerId": 148996,
    "X": 354,
    "Y": 132,
    "Info": "- 1st"
  },
  {
    "PlanetId": 263,
    "OwnerId": 148996,
    "X": 363,
    "Y": 129,
    "Info": "- 2nd"
  },
  {
    "PlanetId": 264,
    "OwnerId": 55375,
    "X": 124,
    "Y": 119,
    "Info": "- 5th"
  },
  {
    "PlanetId": 265,
    "OwnerId": 103288,
    "X": 66,
    "Y": 66,
    "Info": "- 3rd"
  },
  {
    "PlanetId": 266,
    "OwnerId": 59823,
    "X": 61,
    "Y": 42,
    "Info": "- main"
  },
  {
    "PlanetId": 267,
    "OwnerId": 59823,
    "X": 61,
    "Y": 44,
    "Info": "- 1st"
  },
  {
    "PlanetId": 268,
    "OwnerId": 59823,
    "X": 64,
    "Y": 43,
    "Info": "- 2nd"
  },
  {
    "PlanetId": 269,
    "OwnerId": 59823,
    "X": 66,
    "Y": 43,
    "Info": "- 3rd"
  },
  {
    "PlanetId": 270,
    "OwnerId": 59823,
    "X": 59,
    "Y": 39,
    "Info": "- 4th"
  },
  {
    "PlanetId": 271,
    "OwnerId": 196015,
    "X": 394,
    "Y": 435,
    "Info": "- main"
  },
  {
    "PlanetId": 272,
    "OwnerId": 196015,
    "X": 653,
    "Y": 371,
    "Info": "- 1st"
  },
  {
    "PlanetId": 273,
    "OwnerId": 196015,
    "X": 345,
    "Y": 453,
    "Info": "- 2nd"
  },
  {
    "PlanetId": 274,
    "OwnerId": 196015,
    "X": 313,
    "Y": 429,
    "Info": "- 3rd"
  },
  {
    "PlanetId": 275,
    "OwnerId": 195843,
    "X": 217,
    "Y": 339,
    "Info": "- main"
  },
  {
    "PlanetId": 276,
    "OwnerId": 195843,
    "X": 96,
    "Y": 130,
    "Info": "- 1e"
  },
  {
    "PlanetId": 277,
    "OwnerId": 195843,
    "X": 449,
    "Y": 149,
    "Info": "- 2nd"
  },
  {
    "PlanetId": 292,
    "OwnerId": 144094,
    "X": 435,
    "Y": 506,
    "Info": "- main"
  },
  {
    "PlanetId": 293,
    "OwnerId": 144094,
    "X": 544,
    "Y": 369,
    "Info": "- 1st"
  },
  {
    "PlanetId": 294,
    "OwnerId": 144094,
    "X": 709,
    "Y": 673,
    "Info": "- 2nd"
  },
  {
    "PlanetId": 295,
    "OwnerId": 144094,
    "X": 608,
    "Y": 195,
    "Info": "- 3rd"
  },
  {
    "PlanetId": 296,
    "OwnerId": 144094,
    "X": 311,
    "Y": 704,
    "Info": "- 5th"
  },
  {
    "PlanetId": 297,
    "OwnerId": 100459,
    "X": 152,
    "Y": 58,
    "Info": "main"
  },
  {
    "PlanetId": 298,
    "OwnerId": 100459,
    "X": 6,
    "Y": 351,
    "Info": 1
  },
  {
    "PlanetId": 299,
    "OwnerId": 100459,
    "X": 93,
    "Y": 338,
    "Info": 2
  },
  {
    "PlanetId": 300,
    "OwnerId": 100459,
    "X": 306,
    "Y": 291,
    "Info": 3
  },
  {
    "PlanetId": 301,
    "OwnerId": 100459,
    "X": 389,
    "Y": 91,
    "Info": 5
  },
  {
    "PlanetId": 302,
    "OwnerId": 100459,
    "X": 132,
    "Y": 58,
    "Info": 7
  },
  {
    "PlanetId": 303,
    "OwnerId": 100171,
    "X": 6,
    "Y": 351,
    "Info": 1
  },
  {
    "PlanetId": 304,
    "OwnerId": 100171,
    "X": 10,
    "Y": 4,
    "Info": 3
  },
  {
    "PlanetId": 316,
    "OwnerId": 119747,
    "X": 88,
    "Y": 90,
    "Info": "main"
  },
  {
    "PlanetId": 317,
    "OwnerId": 119747,
    "X": 296,
    "Y": 135,
    "Info": 1
  },
  {
    "PlanetId": 318,
    "OwnerId": 119747,
    "X": 505,
    "Y": 300,
    "Info": 3
  },
  {
    "PlanetId": 319,
    "OwnerId": 119747,
    "X": 349,
    "Y": 597,
    "Info": 4
  },
  {
    "PlanetId": 320,
    "OwnerId": 119747,
    "X": 381,
    "Y": 800,
    "Info": 5
  },
  {
    "PlanetId": 321,
    "OwnerId": 119747,
    "X": 606,
    "Y": 600,
    "Info": 6
  },
  {
    "PlanetId": 326,
    "OwnerId": 71937,
    "X": 22,
    "Y": 158,
    "Info": "main"
  },
  {
    "PlanetId": 327,
    "OwnerId": 71937,
    "X": 857,
    "Y": 425,
    "Info": 1
  },
  {
    "PlanetId": 328,
    "OwnerId": 71937,
    "X": 768,
    "Y": 193,
    "Info": 2
  },
  {
    "PlanetId": 329,
    "OwnerId": 71937,
    "X": 637,
    "Y": 842,
    "Info": 3
  },
  {
    "PlanetId": 330,
    "OwnerId": 90108,
    "X": 252,
    "Y": 463,
    "Info": "main"
  },
  {
    "PlanetId": 331,
    "OwnerId": 90108,
    "X": 104,
    "Y": 109,
    "Info": 1
  },
  {
    "PlanetId": 332,
    "OwnerId": 90108,
    "X": 398,
    "Y": 400,
    "Info": 2
  },
  {
    "PlanetId": 333,
    "OwnerId": 80746,
    "X": 130,
    "Y": 521,
    "Info": 1
  },
  {
    "PlanetId": 344,
    "OwnerId": 110456,
    "X": 346,
    "Y": 392,
    "Info": 1
  },
  {
    "PlanetId": 345,
    "OwnerId": 110456,
    "X": 346,
    "Y": 390,
    "Info": 2
  },
  {
    "PlanetId": 346,
    "OwnerId": 110456,
    "X": 326,
    "Y": 383,
    "Info": 3
  },
  {
    "PlanetId": 347,
    "OwnerId": 110456,
    "X": 320,
    "Y": 386,
    "Info": 4
  },
  {
    "PlanetId": 348,
    "OwnerId": 110456,
    "X": 336,
    "Y": 381,
    "Info": 5
  },
  {
    "PlanetId": 349,
    "OwnerId": 110456,
    "X": 335,
    "Y": 383,
    "Info": 6
  },
  {
    "PlanetId": 350,
    "OwnerId": 207982,
    "X": 7,
    "Y": 108,
    "Info": 1
  },
  {
    "PlanetId": 351,
    "OwnerId": 207982,
    "X": 9,
    "Y": 102,
    "Info": 2
  },
  {
    "PlanetId": 352,
    "OwnerId": 207982,
    "X": 6,
    "Y": 103,
    "Info": 3
  },
  {
    "PlanetId": 353,
    "OwnerId": 207982,
    "X": 4,
    "Y": 107,
    "Info": 4
  },
  {
    "PlanetId": 354,
    "OwnerId": 207982,
    "X": 13,
    "Y": 110,
    "Info": 5
  },
  {
    "PlanetId": 355,
    "OwnerId": 207982,
    "X": 19,
    "Y": 117,
    "Info": 6
  },
  {
    "PlanetId": 356,
    "OwnerId": 207982,
    "X": 14,
    "Y": 118,
    "Info": 7
  },
  {
    "PlanetId": 357,
    "OwnerId": 58224,
    "X": 149,
    "Y": 84,
    "Info": "main"
  },
  {
    "PlanetId": 358,
    "OwnerId": 58224,
    "X": 46,
    "Y": 722,
    "Info": 1
  },
  {
    "PlanetId": 359,
    "OwnerId": 58224,
    "X": 316,
    "Y": 333,
    "Info": 2
  },
  {
    "PlanetId": 360,
    "OwnerId": 58224,
    "X": 350,
    "Y": 891,
    "Info": 3
  },
  {
    "PlanetId": 361,
    "OwnerId": 58224,
    "X": 403,
    "Y": 410,
    "Info": 4
  },
  {
    "PlanetId": 362,
    "OwnerId": 58224,
    "X": 211,
    "Y": 902,
    "Info": 5
  },
  {
    "PlanetId": 363,
    "OwnerId": 58224,
    "X": 548,
    "Y": 350,
    "Info": 6
  },
  {
    "PlanetId": 364,
    "OwnerId": 58224,
    "X": 178,
    "Y": 601,
    "Info": 7
  },
  {
    "PlanetId": 365,
    "OwnerId": 58224,
    "X": 398,
    "Y": 624,
    "Info": 8
  },
  {
    "PlanetId": 366,
    "OwnerId": 58224,
    "X": 548,
    "Y": 864,
    "Info": 9
  },
  {
    "PlanetId": 367,
    "OwnerId": 21721,
    "X": 146,
    "Y": 294,
    "Info": "main"
  },
  {
    "PlanetId": 368,
    "OwnerId": 21721,
    "X": 501,
    "Y": 405,
    "Info": 1
  },
  {
    "PlanetId": 369,
    "OwnerId": 21721,
    "X": 254,
    "Y": 331,
    "Info": 2
  },
  {
    "PlanetId": 370,
    "OwnerId": 21721,
    "X": 146,
    "Y": 294,
    "Info": 3
  },
  {
    "PlanetId": 371,
    "OwnerId": 21721,
    "X": 145,
    "Y": 293,
    "Info": 4
  },
  {
    "PlanetId": 372,
    "OwnerId": 21721,
    "X": 150,
    "Y": 292,
    "Info": 5
  },
  {
    "PlanetId": 373,
    "OwnerId": 21721,
    "X": 150,
    "Y": 291,
    "Info": 6
  },
  {
    "PlanetId": 374,
    "OwnerId": 21721,
    "X": 152,
    "Y": 290,
    "Info": 7
  },
  {
    "PlanetId": 375,
    "OwnerId": 21721,
    "X": 132,
    "Y": 285,
    "Info": 8
  },
  {
    "PlanetId": 376,
    "OwnerId": 21721,
    "X": 152,
    "Y": 289,
    "Info": 9
  },
  {
    "PlanetId": 377,
    "OwnerId": 21721,
    "X": 152,
    "Y": 289,
    "Info": 10
  },
  {
    "PlanetId": 378,
    "OwnerId": 21721,
    "X": 152,
    "Y": 289,
    "Info": 11
  },
  {
    "PlanetId": 379,
    "OwnerId": 74258,
    "X": 526,
    "Y": 111,
    "Info": "main"
  },
  {
    "PlanetId": 380,
    "OwnerId": 74258,
    "X": 453,
    "Y": 121,
    "Info": 1
  },
  {
    "PlanetId": 381,
    "OwnerId": 74258,
    "X": 414,
    "Y": 59,
    "Info": 2
  },
  {
    "PlanetId": 382,
    "OwnerId": 74258,
    "X": 705,
    "Y": 90,
    "Info": 3
  },
  {
    "PlanetId": 383,
    "OwnerId": 74258,
    "X": 603,
    "Y": 70,
    "Info": 4
  },
  {
    "PlanetId": 384,
    "OwnerId": 74258,
    "X": 621,
    "Y": 151,
    "Info": 5
  },
  {
    "PlanetId": 385,
    "OwnerId": 74258,
    "X": 543,
    "Y": 1,
    "Info": 6
  },
  {
    "PlanetId": 386,
    "OwnerId": 74258,
    "X": 696,
    "Y": 210,
    "Info": 7
  },
  {
    "PlanetId": 387,
    "OwnerId": 42243,
    "X": 919,
    "Y": 455,
    "Info": "main"
  },
  {
    "PlanetId": 388,
    "OwnerId": 42243,
    "X": 42,
    "Y": 437,
    "Info": 1
  },
  {
    "PlanetId": 389,
    "OwnerId": 42243,
    "X": 63,
    "Y": 434,
    "Info": 2
  },
  {
    "PlanetId": 390,
    "OwnerId": 42243,
    "X": 53,
    "Y": 412,
    "Info": 3
  },
  {
    "PlanetId": 391,
    "OwnerId": 42243,
    "X": 74,
    "Y": 461,
    "Info": 4
  },
  {
    "PlanetId": 392,
    "OwnerId": 42243,
    "X": 66,
    "Y": 471,
    "Info": 5
  },
  {
    "PlanetId": 393,
    "OwnerId": 42243,
    "X": 179,
    "Y": 434,
    "Info": 6
  },
  {
    "PlanetId": 394,
    "OwnerId": 42243,
    "X": 7,
    "Y": 419,
    "Info": 7
  },
  {
    "PlanetId": 395,
    "OwnerId": 42243,
    "X": 0,
    "Y": 402,
    "Info": 8
  },
  {
    "PlanetId": 396,
    "OwnerId": 42243,
    "X": 3,
    "Y": 385,
    "Info": 9
  },
  {
    "PlanetId": 397,
    "OwnerId": 43331,
    "X": 47,
    "Y": 49,
    "Info": "main"
  },
  {
    "PlanetId": 398,
    "OwnerId": 43331,
    "X": 907,
    "Y": 492,
    "Info": 1
  },
  {
    "PlanetId": 399,
    "OwnerId": 43331,
    "X": 473,
    "Y": 284,
    "Info": 2
  },
  {
    "PlanetId": 400,
    "OwnerId": 43331,
    "X": 645,
    "Y": 114,
    "Info": 3
  },
  {
    "PlanetId": 401,
    "OwnerId": 43331,
    "X": 192,
    "Y": 802,
    "Info": 4
  },
  {
    "PlanetId": 402,
    "OwnerId": 43331,
    "X": 325,
    "Y": 320,
    "Info": 5
  },
  {
    "PlanetId": 403,
    "OwnerId": 43331,
    "X": 513,
    "Y": 12,
    "Info": 6
  },
  {
    "PlanetId": 404,
    "OwnerId": 43331,
    "X": 12,
    "Y": 871,
    "Info": 7
  },
  {
    "PlanetId": 405,
    "OwnerId": 43331,
    "X": 687,
    "Y": 868,
    "Info": 8
  },
  {
    "PlanetId": 406,
    "OwnerId": 43331,
    "X": 716,
    "Y": 487,
    "Info": 9
  },
  {
    "PlanetId": 407,
    "OwnerId": 72147,
    "X": 315,
    "Y": 384,
    "Info": "main"
  },
  {
    "PlanetId": 408,
    "OwnerId": 72147,
    "X": 316,
    "Y": 388,
    "Info": 1
  },
  {
    "PlanetId": 409,
    "OwnerId": 72147,
    "X": 296,
    "Y": 385,
    "Info": 2
  },
  {
    "PlanetId": 410,
    "OwnerId": 72147,
    "X": 405,
    "Y": 420,
    "Info": 3
  },
  {
    "PlanetId": 411,
    "OwnerId": 72147,
    "X": 334,
    "Y": 378,
    "Info": 4
  },
  {
    "PlanetId": 412,
    "OwnerId": 72147,
    "X": 289,
    "Y": 390,
    "Info": 5
  },
  {
    "PlanetId": 413,
    "OwnerId": 72147,
    "X": 896,
    "Y": 889,
    "Info": 6
  },
  {
    "PlanetId": 414,
    "OwnerId": 72147,
    "X": 928,
    "Y": 898,
    "Info": 7
  },
  {
    "PlanetId": 415,
    "OwnerId": 72147,
    "X": 903,
    "Y": 1,
    "Info": 8
  },
  {
    "PlanetId": 416,
    "OwnerId": 72147,
    "X": 2,
    "Y": 896,
    "Info": 9
  },
  {
    "PlanetId": 417,
    "OwnerId": 90023,
    "X": 459,
    "Y": 174,
    "Info": "main"
  },
  {
    "PlanetId": 418,
    "OwnerId": 90023,
    "X": 169,
    "Y": 398,
    "Info": 1
  },
  {
    "PlanetId": 419,
    "OwnerId": 90023,
    "X": 69,
    "Y": 174,
    "Info": 2
  },
  {
    "PlanetId": 420,
    "OwnerId": 90023,
    "X": 4,
    "Y": 8,
    "Info": 3
  },
  {
    "PlanetId": 421,
    "OwnerId": 90023,
    "X": 201,
    "Y": 69,
    "Info": 4
  },
  {
    "PlanetId": 422,
    "OwnerId": 90023,
    "X": 168,
    "Y": 170,
    "Info": 5
  },
  {
    "PlanetId": 423,
    "OwnerId": 90023,
    "X": 435,
    "Y": 190,
    "Info": 6
  },
  {
    "PlanetId": 424,
    "OwnerId": 90023,
    "X": 506,
    "Y": 153,
    "Info": 7
  },
  {
    "PlanetId": 425,
    "OwnerId": 53837,
    "X": 175,
    "Y": 334,
    "Info": "main"
  },
  {
    "PlanetId": 426,
    "OwnerId": 53837,
    "X": 179,
    "Y": 331,
    "Info": 1
  },
  {
    "PlanetId": 427,
    "OwnerId": 53837,
    "X": 167,
    "Y": 335,
    "Info": 2
  },
  {
    "PlanetId": 428,
    "OwnerId": 53837,
    "X": 174,
    "Y": 334,
    "Info": 3
  },
  {
    "PlanetId": 429,
    "OwnerId": 53837,
    "X": 184,
    "Y": 337,
    "Info": 4
  },
  {
    "PlanetId": 430,
    "OwnerId": 53837,
    "X": 148,
    "Y": 348,
    "Info": 5
  },
  {
    "PlanetId": 431,
    "OwnerId": 53837,
    "X": 1513,
    "Y": 312,
    "Info": 6
  },
  {
    "PlanetId": 432,
    "OwnerId": 53837,
    "X": 210,
    "Y": 319,
    "Info": 7
  },
  {
    "PlanetId": 433,
    "OwnerId": 53837,
    "X": 105,
    "Y": 341,
    "Info": 8
  },
  {
    "PlanetId": 434,
    "OwnerId": 42036,
    "X": 320,
    "Y": 263,
    "Info": "main"
  },
  {
    "PlanetId": 435,
    "OwnerId": 42036,
    "X": 316,
    "Y": 261,
    "Info": 1
  },
  {
    "PlanetId": 436,
    "OwnerId": 42036,
    "X": 316,
    "Y": 258,
    "Info": 2
  },
  {
    "PlanetId": 437,
    "OwnerId": 42036,
    "X": 330,
    "Y": 283,
    "Info": 3
  },
  {
    "PlanetId": 438,
    "OwnerId": 42036,
    "X": 333,
    "Y": 272,
    "Info": 4
  },
  {
    "PlanetId": 439,
    "OwnerId": 42036,
    "X": 322,
    "Y": 261,
    "Info": 5
  },
  {
    "PlanetId": 440,
    "OwnerId": 42036,
    "X": 308,
    "Y": 246,
    "Info": 6
  },
  {
    "PlanetId": 441,
    "OwnerId": 42036,
    "X": 278,
    "Y": 236,
    "Info": 7
  },
  {
    "PlanetId": 442,
    "OwnerId": 59276,
    "X": 482,
    "Y": 251,
    "Info": "main"
  },
  {
    "PlanetId": 443,
    "OwnerId": 59276,
    "X": 482,
    "Y": 251,
    "Info": 1
  },
  {
    "PlanetId": 444,
    "OwnerId": 59276,
    "X": 481,
    "Y": 250,
    "Info": 2
  },
  {
    "PlanetId": 445,
    "OwnerId": 59276,
    "X": 485,
    "Y": 252,
    "Info": 3
  },
  {
    "PlanetId": 446,
    "OwnerId": 59276,
    "X": 490,
    "Y": 247,
    "Info": 4
  },
  {
    "PlanetId": 447,
    "OwnerId": 59276,
    "X": 498,
    "Y": 250,
    "Info": 5
  },
  {
    "PlanetId": 448,
    "OwnerId": 55021,
    "X": 217,
    "Y": 37,
    "Info": "main"
  },
  {
    "PlanetId": 449,
    "OwnerId": 55021,
    "X": 68,
    "Y": 185,
    "Info": 1
  },
  {
    "PlanetId": 450,
    "OwnerId": 55021,
    "X": 2,
    "Y": 4,
    "Info": 2
  },
  {
    "PlanetId": 451,
    "OwnerId": 55021,
    "X": 107,
    "Y": 239,
    "Info": 3
  },
  {
    "PlanetId": 452,
    "OwnerId": 55021,
    "X": 336,
    "Y": 120,
    "Info": 4
  },
  {
    "PlanetId": 453,
    "OwnerId": 55021,
    "X": 216,
    "Y": 38,
    "Info": 5
  },
  {
    "PlanetId": 454,
    "OwnerId": 55021,
    "X": 212,
    "Y": 32,
    "Info": 6
  },
  {
    "PlanetId": 455,
    "OwnerId": 55021,
    "X": 216,
    "Y": 38,
    "Info": 7
  },
  {
    "PlanetId": 456,
    "OwnerId": 40572,
    "X": 406,
    "Y": 376,
    "Info": "main"
  },
  {
    "PlanetId": 457,
    "OwnerId": 40572,
    "X": 16,
    "Y": 1,
    "Info": 1
  },
  {
    "PlanetId": 458,
    "OwnerId": 40572,
    "X": 21,
    "Y": 6,
    "Info": 2
  },
  {
    "PlanetId": 459,
    "OwnerId": 40572,
    "X": 5,
    "Y": 7,
    "Info": 3
  },
  {
    "PlanetId": 460,
    "OwnerId": 40572,
    "X": 9,
    "Y": 3,
    "Info": 4
  },
  {
    "PlanetId": 461,
    "OwnerId": 40572,
    "X": 20,
    "Y": 8,
    "Info": 5
  },
  {
    "PlanetId": 462,
    "OwnerId": 40572,
    "X": 14,
    "Y": 1,
    "Info": 6
  },
  {
    "PlanetId": 463,
    "OwnerId": 57840,
    "X": 307,
    "Y": 336,
    "Info": "main"
  },
  {
    "PlanetId": 464,
    "OwnerId": 57840,
    "X": 317,
    "Y": 352,
    "Info": 1
  },
  {
    "PlanetId": 465,
    "OwnerId": 57840,
    "X": 329,
    "Y": 340,
    "Info": 2
  },
  {
    "PlanetId": 466,
    "OwnerId": 57840,
    "X": 204,
    "Y": 267,
    "Info": 3
  },
  {
    "PlanetId": 467,
    "OwnerId": 89457,
    "X": 412,
    "Y": 55,
    "Info": "main"
  },
  {
    "PlanetId": 468,
    "OwnerId": 89457,
    "X": 412,
    "Y": 62,
    "Info": 1
  },
  {
    "PlanetId": 469,
    "OwnerId": 89457,
    "X": 422,
    "Y": 63,
    "Info": 2
  },
  {
    "PlanetId": 470,
    "OwnerId": 89457,
    "X": 411,
    "Y": 57,
    "Info": 3
  },
  {
    "PlanetId": 471,
    "OwnerId": 89457,
    "X": 423,
    "Y": 64,
    "Info": 4
  },
  {
    "PlanetId": 472,
    "OwnerId": 89457,
    "X": 451,
    "Y": 57,
    "Info": 5
  },
  {
    "PlanetId": 473,
    "OwnerId": 40236,
    "X": 19,
    "Y": 33,
    "Info": 1
  },
  {
    "PlanetId": 474,
    "OwnerId": 40236,
    "X": 21,
    "Y": 49,
    "Info": 2
  },
  {
    "PlanetId": 475,
    "OwnerId": 185986,
    "X": 144,
    "Y": 361,
    "Info": 1
  },
  {
    "PlanetId": 476,
    "OwnerId": 185986,
    "X": 155,
    "Y": 349,
    "Info": 2
  },
  {
    "PlanetId": 477,
    "OwnerId": 185986,
    "X": 152,
    "Y": 358,
    "Info": 3
  },
  {
    "PlanetId": 478,
    "OwnerId": 185986,
    "X": 148,
    "Y": 361,
    "Info": 4
  },
  {
    "PlanetId": 479,
    "OwnerId": 185986,
    "X": 151,
    "Y": 357,
    "Info": 5
  },
  {
    "PlanetId": 480,
    "OwnerId": 224772,
    "X": 710,
    "Y": 497,
    "Info": "main"
  },
  {
    "PlanetId": 481,
    "OwnerId": 224772,
    "X": 692,
    "Y": 495,
    "Info": 1
  },
  {
    "PlanetId": 482,
    "OwnerId": 224772,
    "X": 655,
    "Y": 478,
    "Info": 2
  },
  {
    "PlanetId": 483,
    "OwnerId": 224772,
    "X": 787,
    "Y": 505,
    "Info": 3
  },
  {
    "PlanetId": 484,
    "OwnerId": 212342,
    "X": 143,
    "Y": 220,
    "Info": "main"
  },
  {
    "PlanetId": 485,
    "OwnerId": 212342,
    "X": 128,
    "Y": 206,
    "Info": 1
  },
  {
    "PlanetId": 486,
    "OwnerId": 212342,
    "X": 139,
    "Y": 209,
    "Info": 2
  },
  {
    "PlanetId": 487,
    "OwnerId": 212342,
    "X": 115,
    "Y": 221,
    "Info": 3
  },
  {
    "PlanetId": 488,
    "OwnerId": 212342,
    "X": 118,
    "Y": 200,
    "Info": 4
  },
  {
    "PlanetId": 489,
    "OwnerId": 43567,
    "X": 492,
    "Y": 72,
    "Info": "main"
  },
  {
    "PlanetId": 490,
    "OwnerId": 43567,
    "X": 503,
    "Y": 75,
    "Info": 1
  },
  {
    "PlanetId": 491,
    "OwnerId": 43567,
    "X": 504,
    "Y": 72,
    "Info": 2
  },
  {
    "PlanetId": 492,
    "OwnerId": 43567,
    "X": 492,
    "Y": 70,
    "Info": 3
  },
  {
    "PlanetId": 493,
    "OwnerId": 43567,
    "X": 497,
    "Y": 69,
    "Info": 4
  },
  {
    "PlanetId": 494,
    "OwnerId": 43567,
    "X": 488,
    "Y": 76,
    "Info": 5
  },
  {
    "PlanetId": 495,
    "OwnerId": 43567,
    "X": 496,
    "Y": 71,
    "Info": 6
  },
  {
    "PlanetId": 496,
    "OwnerId": 224874,
    "X": 293,
    "Y": 505,
    "Info": ""
  },
  {
    "PlanetId": 497,
    "OwnerId": 224874,
    "X": 74,
    "Y": 276,
    "Info": 1
  },
  {
    "PlanetId": 498,
    "OwnerId": 224874,
    "X": 286,
    "Y": 533,
    "Info": 2
  },
  {
    "PlanetId": 499,
    "OwnerId": 224874,
    "X": 152,
    "Y": 155,
    "Info": 3
  },
  {
    "PlanetId": 500,
    "OwnerId": 224874,
    "X": 397,
    "Y": 403,
    "Info": 4
  },
  {
    "PlanetId": 501,
    "OwnerId": 224874,
    "X": 9,
    "Y": 18,
    "Info": 5
  },
  {
    "PlanetId": 502,
    "OwnerId": 224874,
    "X": 431,
    "Y": 103,
    "Info": 6
  },
  {
    "PlanetId": 503,
    "OwnerId": 71768,
    "X": 442,
    "Y": 275,
    "Info": "main"
  },
  {
    "PlanetId": 504,
    "OwnerId": 71768,
    "X": 441,
    "Y": 271,
    "Info": 1
  },
  {
    "PlanetId": 505,
    "OwnerId": 71768,
    "X": 438,
    "Y": 273,
    "Info": 2
  },
  {
    "PlanetId": 506,
    "OwnerId": 71768,
    "X": 433,
    "Y": 276,
    "Info": 3
  },
  {
    "PlanetId": 507,
    "OwnerId": 71768,
    "X": 454,
    "Y": 258,
    "Info": 4
  },
  {
    "PlanetId": 508,
    "OwnerId": 71768,
    "X": 439,
    "Y": 279,
    "Info": 5
  },
  {
    "PlanetId": 509,
    "OwnerId": 71768,
    "X": 431,
    "Y": 284,
    "Info": 6
  },
  {
    "PlanetId": 510,
    "OwnerId": 71768,
    "X": 447,
    "Y": 270,
    "Info": 7
  },
  {
    "PlanetId": 511,
    "OwnerId": 41342,
    "X": 459,
    "Y": 314,
    "Info": "main"
  },
  {
    "PlanetId": 512,
    "OwnerId": 41342,
    "X": 516,
    "Y": 746,
    "Info": 1
  },
  {
    "PlanetId": 513,
    "OwnerId": 41342,
    "X": 477,
    "Y": 279,
    "Info": 2
  },
  {
    "PlanetId": 514,
    "OwnerId": 41342,
    "X": 627,
    "Y": 401,
    "Info": 3
  },
  {
    "PlanetId": 515,
    "OwnerId": 41342,
    "X": 812,
    "Y": 488,
    "Info": 4
  },
  {
    "PlanetId": 516,
    "OwnerId": 41342,
    "X": 267,
    "Y": 381,
    "Info": 5
  },
  {
    "PlanetId": 517,
    "OwnerId": 41342,
    "X": 89,
    "Y": 64,
    "Info": 6
  },
  {
    "PlanetId": 518,
    "OwnerId": 41342,
    "X": 221,
    "Y": 2,
    "Info": 7
  },
  {
    "PlanetId": 519,
    "OwnerId": 181206,
    "X": 330,
    "Y": 108,
    "Info": "main"
  },
  {
    "PlanetId": 520,
    "OwnerId": 181206,
    "X": 0,
    "Y": 130,
    "Info": 1
  },
  {
    "PlanetId": 521,
    "OwnerId": 181206,
    "X": 97,
    "Y": 151,
    "Info": 2
  },
  {
    "PlanetId": 522,
    "OwnerId": 181206,
    "X": 157,
    "Y": 556,
    "Info": 3
  },
  {
    "PlanetId": 523,
    "OwnerId": 181206,
    "X": 203,
    "Y": 208,
    "Info": 4
  },
  {
    "PlanetId": 524,
    "OwnerId": 181206,
    "X": 553,
    "Y": 446,
    "Info": 5
  },
  {
    "PlanetId": 525,
    "OwnerId": 181206,
    "X": 455,
    "Y": 256,
    "Info": 6
  },
  {
    "PlanetId": 526,
    "OwnerId": 181206,
    "X": 671,
    "Y": 778,
    "Info": 7
  },
  {
    "PlanetId": 527,
    "OwnerId": 181206,
    "X": 271,
    "Y": 316,
    "Info": 8
  },
  {
    "PlanetId": 528,
    "OwnerId": 186315,
    "X": 202,
    "Y": 379,
    "Info": "main"
  },
  {
    "PlanetId": 529,
    "OwnerId": 186315,
    "X": 2,
    "Y": 9,
    "Info": 1
  },
  {
    "PlanetId": 530,
    "OwnerId": 186315,
    "X": 197,
    "Y": 0,
    "Info": 2
  },
  {
    "PlanetId": 531,
    "OwnerId": 186315,
    "X": 787,
    "Y": 779,
    "Info": 3
  },
  {
    "PlanetId": 532,
    "OwnerId": 186315,
    "X": 169,
    "Y": 382,
    "Info": 4
  },
  {
    "PlanetId": 533,
    "OwnerId": 186315,
    "X": 170,
    "Y": 385,
    "Info": 5
  },
  {
    "PlanetId": 534,
    "OwnerId": 186315,
    "X": 145,
    "Y": 400,
    "Info": 6
  },
  {
    "PlanetId": 535,
    "OwnerId": 186315,
    "X": 177,
    "Y": 338,
    "Info": 7
  },
  {
    "PlanetId": 536,
    "OwnerId": 186315,
    "X": 152,
    "Y": 407,
    "Info": 8
  },
  {
    "PlanetId": 537,
    "OwnerId": 186315,
    "X": 232,
    "Y": 374,
    "Info": 9
  },
  {
    "PlanetId": 538,
    "OwnerId": 186315,
    "X": 248,
    "Y": 409,
    "Info": 10
  },
  {
    "PlanetId": 539,
    "OwnerId": 186315,
    "X": 313,
    "Y": 282,
    "Info": 11
  },
  {
    "PlanetId": 540,
    "OwnerId": 59938,
    "X": 109,
    "Y": 473,
    "Info": "main"
  },
  {
    "PlanetId": 541,
    "OwnerId": 59938,
    "X": 751,
    "Y": 804,
    "Info": 1
  },
  {
    "PlanetId": 542,
    "OwnerId": 59938,
    "X": 353,
    "Y": 662,
    "Info": 2
  },
  {
    "PlanetId": 543,
    "OwnerId": 59938,
    "X": 774,
    "Y": 614,
    "Info": 3
  },
  {
    "PlanetId": 544,
    "OwnerId": 59938,
    "X": 66,
    "Y": 808,
    "Info": 4
  },
  {
    "PlanetId": 545,
    "OwnerId": 59938,
    "X": 375,
    "Y": 678,
    "Info": 5
  },
  {
    "PlanetId": 546,
    "OwnerId": 59938,
    "X": 748,
    "Y": 840,
    "Info": 6
  },
  {
    "PlanetId": 547,
    "OwnerId": 128522,
    "X": 413,
    "Y": 240,
    "Info": "main"
  },
  {
    "PlanetId": 548,
    "OwnerId": 128522,
    "X": 4,
    "Y": 8,
    "Info": 1
  },
  {
    "PlanetId": 549,
    "OwnerId": 128522,
    "X": 44,
    "Y": 24,
    "Info": 2
  },
  {
    "PlanetId": 550,
    "OwnerId": 128522,
    "X": 47,
    "Y": 2,
    "Info": 3
  },
  {
    "PlanetId": 551,
    "OwnerId": 128522,
    "X": 385,
    "Y": 180,
    "Info": 4
  },
  {
    "PlanetId": 552,
    "OwnerId": 128522,
    "X": 365,
    "Y": 140,
    "Info": 5
  },
  {
    "PlanetId": 553,
    "OwnerId": 128522,
    "X": 45,
    "Y": 14,
    "Info": 6
  },
  {
    "PlanetId": 554,
    "OwnerId": 128522,
    "X": 5,
    "Y": 40,
    "Info": 7
  },
  {
    "PlanetId": 555,
    "OwnerId": 79619,
    "X": 79,
    "Y": 219,
    "Info": "main"
  },
  {
    "PlanetId": 556,
    "OwnerId": 79619,
    "X": 9,
    "Y": 3,
    "Info": 1
  },
  {
    "PlanetId": 557,
    "OwnerId": 79619,
    "X": 868,
    "Y": 810,
    "Info": 2
  },
  {
    "PlanetId": 558,
    "OwnerId": 79619,
    "X": 88,
    "Y": 826,
    "Info": 3
  },
  {
    "PlanetId": 559,
    "OwnerId": 79619,
    "X": 287,
    "Y": 437,
    "Info": 4
  },
  {
    "PlanetId": 560,
    "OwnerId": 79619,
    "X": 706,
    "Y": 124,
    "Info": 5
  },
  {
    "PlanetId": 561,
    "OwnerId": 79619,
    "X": 59,
    "Y": 101,
    "Info": 6
  },
  {
    "PlanetId": 562,
    "OwnerId": 79619,
    "X": 19,
    "Y": 9,
    "Info": 7
  },
  {
    "PlanetId": 563,
    "OwnerId": 131571,
    "X": 48,
    "Y": 203,
    "Info": ""
  },
  {
    "PlanetId": 564,
    "OwnerId": 131571,
    "X": 11,
    "Y": 1,
    "Info": ""
  },
  {
    "PlanetId": 565,
    "OwnerId": 70525,
    "X": 227,
    "Y": 388,
    "Info": 2
  },
  {
    "PlanetId": 566,
    "OwnerId": 175711,
    "X": 142,
    "Y": 329,
    "Info": "main"
  },
  {
    "PlanetId": 567,
    "OwnerId": 175711,
    "X": 18,
    "Y": 38,
    "Info": 1
  },
  {
    "PlanetId": 568,
    "OwnerId": 175711,
    "X": 650,
    "Y": 545,
    "Info": 2
  },
  {
    "PlanetId": 569,
    "OwnerId": 175711,
    "X": 16,
    "Y": 327,
    "Info": 3
  },
  {
    "PlanetId": 570,
    "OwnerId": 186849,
    "X": 394,
    "Y": 66,
    "Info": "main"
  },
  {
    "PlanetId": 571,
    "OwnerId": 186849,
    "X": 115,
    "Y": 118,
    "Info": 2
  },
  {
    "PlanetId": 572,
    "OwnerId": 186849,
    "X": 79,
    "Y": 70,
    "Info": 4
  },
  {
    "PlanetId": 573,
    "OwnerId": 186849,
    "X": 180,
    "Y": 180,
    "Info": 5
  },
  {
    "PlanetId": 574,
    "OwnerId": 186849,
    "X": 271,
    "Y": 268,
    "Info": 6
  },
  {
    "PlanetId": 575,
    "OwnerId": 186849,
    "X": 520,
    "Y": 498,
    "Info": 7
  },
  {
    "PlanetId": 576,
    "OwnerId": 186849,
    "X": 331,
    "Y": 338,
    "Info": 8
  },
  {
    "PlanetId": 577,
    "OwnerId": 186849,
    "X": 429,
    "Y": 98,
    "Info": 9
  },
  {
    "PlanetId": 578,
    "OwnerId": 186849,
    "X": 349,
    "Y": 86,
    "Info": 10
  },
  {
    "PlanetId": 579,
    "OwnerId": 186849,
    "X": 419,
    "Y": 92,
    "Info": 11
  },
  {
    "PlanetId": 580,
    "OwnerId": 36157,
    "X": 51,
    "Y": 98,
    "Info": 2
  },
  {
    "PlanetId": 593,
    "OwnerId": 62172,
    "X": 94,
    "Y": 22,
    "Info": "main"
  },
  {
    "PlanetId": 594,
    "OwnerId": 62172,
    "X": 210,
    "Y": 91,
    "Info": 1
  },
  {
    "PlanetId": 595,
    "OwnerId": 62172,
    "X": 316,
    "Y": 271,
    "Info": 2
  },
  {
    "PlanetId": 596,
    "OwnerId": 62172,
    "X": 109,
    "Y": 25,
    "Info": 7
  },
  {
    "PlanetId": 597,
    "OwnerId": 62236,
    "X": 89,
    "Y": 304,
    "Info": "main"
  },
  {
    "PlanetId": 598,
    "OwnerId": 62236,
    "X": 134,
    "Y": 445,
    "Info": 1
  },
  {
    "PlanetId": 599,
    "OwnerId": 75224,
    "X": 0,
    "Y": 0,
    "Info": ""
  },
  {
    "PlanetId": 600,
    "OwnerId": 95764,
    "X": 0,
    "Y": 0,
    "Info": ""
  },
  {
    "PlanetId": 601,
    "OwnerId": 0,
    "X": 0,
    "Y": 0,
    "Info": ""
  },
  {
    "PlanetId": 602,
    "OwnerId": 168274,
    "X": 0,
    "Y": 0,
    "Info": ""
  },
  {
    "PlanetId": 603,
    "OwnerId": 73660,
    "X": 9,
    "Y": 62,
    "Info": ""
  },
  {
    "PlanetId": 604,
    "OwnerId": 75724,
    "X": 9,
    "Y": 65,
    "Info": ""
  },
  {
    "PlanetId": 605,
    "OwnerId": 133509,
    "X": 9,
    "Y": 65,
    "Info": ""
  },
  {
    "PlanetId": 606,
    "OwnerId": 165784,
    "X": 9,
    "Y": 65,
    "Info": ""
  },
  {
    "PlanetId": 607,
    "OwnerId": 206367,
    "X": 9,
    "Y": 65,
    "Info": ""
  },
  {
    "PlanetId": 608,
    "OwnerId": 64745,
    "X": 9,
    "Y": 65,
    "Info": ""
  },
  {
    "PlanetId": 609,
    "OwnerId": 56523,
    "X": 9,
    "Y": 55,
    "Info": ""
  },
  {
    "PlanetId": 610,
    "OwnerId": 166615,
    "X": 9,
    "Y": 55,
    "Info": ""
  },
  {
    "PlanetId": 611,
    "OwnerId": 124317,
    "X": 9,
    "Y": 55,
    "Info": ""
  },
  {
    "PlanetId": 612,
    "OwnerId": 57612,
    "X": 9,
    "Y": 55,
    "Info": ""
  },
  {
    "PlanetId": 613,
    "OwnerId": 173762,
    "X": 9,
    "Y": 55,
    "Info": ""
  },
  {
    "PlanetId": 614,
    "OwnerId": 40370,
    "X": 9,
    "Y": 55,
    "Info": ""
  },
  {
    "PlanetId": 615,
    "OwnerId": 197264,
    "X": 9,
    "Y": 55,
    "Info": ""
  },
  {
    "PlanetId": 616,
    "OwnerId": 81883,
    "X": 9,
    "Y": 55,
    "Info": ""
  },
  {
    "PlanetId": 617,
    "OwnerId": 141114,
    "X": 9,
    "Y": 39,
    "Info": ""
  },
  {
    "PlanetId": 618,
    "OwnerId": 146903,
    "X": 9,
    "Y": 39,
    "Info": ""
  },
  {
    "PlanetId": 619,
    "OwnerId": 147442,
    "X": 9,
    "Y": 39,
    "Info": ""
  },
  {
    "PlanetId": 620,
    "OwnerId": 157543,
    "X": 9,
    "Y": 39,
    "Info": ""
  },
  {
    "PlanetId": 621,
    "OwnerId": 190937,
    "X": 9,
    "Y": 39,
    "Info": ""
  },
  {
    "PlanetId": 622,
    "OwnerId": 143684,
    "X": 9,
    "Y": 39,
    "Info": ""
  },
  {
    "PlanetId": 623,
    "OwnerId": 75224,
    "X": 9,
    "Y": 78,
    "Info": ""
  },
  {
    "PlanetId": 624,
    "OwnerId": 95764,
    "X": 9,
    "Y": 78,
    "Info": ""
  },
  {
    "PlanetId": 625,
    "OwnerId": 136153,
    "X": 9,
    "Y": 78,
    "Info": ""
  },
  {
    "PlanetId": 626,
    "OwnerId": 160619,
    "X": 9,
    "Y": 78,
    "Info": ""
  },
  {
    "PlanetId": 627,
    "OwnerId": 168274,
    "X": 9,
    "Y": 78,
    "Info": ""
  },
  {
    "PlanetId": 628,
    "OwnerId": 46321,
    "X": 9,
    "Y": 78,
    "Info": ""
  },
  {
    "PlanetId": 629,
    "OwnerId": 198553,
    "X": 9,
    "Y": 78,
    "Info": ""
  },
  {
    "PlanetId": 630,
    "OwnerId": 127551,
    "X": 9,
    "Y": 76,
    "Info": ""
  },
  {
    "PlanetId": 631,
    "OwnerId": 170530,
    "X": 9,
    "Y": 76,
    "Info": ""
  },
  {
    "PlanetId": 632,
    "OwnerId": 194600,
    "X": 9,
    "Y": 76,
    "Info": ""
  },
  {
    "PlanetId": 633,
    "OwnerId": 207340,
    "X": 9,
    "Y": 76,
    "Info": ""
  },
  {
    "PlanetId": 634,
    "OwnerId": 64684,
    "X": 9,
    "Y": 76,
    "Info": ""
  },
  {
    "PlanetId": 635,
    "OwnerId": 75724,
    "X": 9,
    "Y": 76,
    "Info": ""
  },
  {
    "PlanetId": 636,
    "OwnerId": 179704,
    "X": 9,
    "Y": 76,
    "Info": ""
  },
  {
    "PlanetId": 637,
    "OwnerId": 82895,
    "X": 9,
    "Y": 74,
    "Info": ""
  },
  {
    "PlanetId": 638,
    "OwnerId": 86438,
    "X": 9,
    "Y": 74,
    "Info": ""
  },
  {
    "PlanetId": 639,
    "OwnerId": 94102,
    "X": 9,
    "Y": 74,
    "Info": ""
  },
  {
    "PlanetId": 640,
    "OwnerId": 119472,
    "X": 9,
    "Y": 74,
    "Info": ""
  },
  {
    "PlanetId": 641,
    "OwnerId": 135817,
    "X": 9,
    "Y": 74,
    "Info": ""
  },
  {
    "PlanetId": 642,
    "OwnerId": 192334,
    "X": 9,
    "Y": 74,
    "Info": ""
  },
  {
    "PlanetId": 643,
    "OwnerId": 102942,
    "X": 9,
    "Y": 3,
    "Info": ""
  },
  {
    "PlanetId": 644,
    "OwnerId": 146404,
    "X": 9,
    "Y": 3,
    "Info": ""
  },
  {
    "PlanetId": 645,
    "OwnerId": 151398,
    "X": 9,
    "Y": 3,
    "Info": ""
  },
  {
    "PlanetId": 646,
    "OwnerId": 62906,
    "X": 9,
    "Y": 3,
    "Info": ""
  },
  {
    "PlanetId": 647,
    "OwnerId": 56302,
    "X": 9,
    "Y": 3,
    "Info": ""
  },
  {
    "PlanetId": 648,
    "OwnerId": 41358,
    "X": 9,
    "Y": 3,
    "Info": ""
  },
  {
    "PlanetId": 649,
    "OwnerId": 137667,
    "X": 9,
    "Y": 3,
    "Info": ""
  },
  {
    "PlanetId": 650,
    "OwnerId": 134218,
    "X": 9,
    "Y": 3,
    "Info": ""
  },
  {
    "PlanetId": 651,
    "OwnerId": 181951,
    "X": 9,
    "Y": 3,
    "Info": ""
  },
  {
    "PlanetId": 652,
    "OwnerId": 42836,
    "X": 9,
    "Y": 3,
    "Info": ""
  },
  {
    "PlanetId": 653,
    "OwnerId": 183939,
    "X": 9,
    "Y": 3,
    "Info": ""
  },
  {
    "PlanetId": 654,
    "OwnerId": 112607,
    "X": 9,
    "Y": 37,
    "Info": ""
  },
  {
    "PlanetId": 655,
    "OwnerId": 115771,
    "X": 9,
    "Y": 37,
    "Info": ""
  },
  {
    "PlanetId": 656,
    "OwnerId": 142901,
    "X": 9,
    "Y": 37,
    "Info": ""
  },
  {
    "PlanetId": 657,
    "OwnerId": 156339,
    "X": 9,
    "Y": 37,
    "Info": ""
  },
  {
    "PlanetId": 658,
    "OwnerId": 172150,
    "X": 9,
    "Y": 37,
    "Info": ""
  },
  {
    "PlanetId": 659,
    "OwnerId": 208734,
    "X": 9,
    "Y": 37,
    "Info": ""
  },
  {
    "PlanetId": 660,
    "OwnerId": 166688,
    "X": 9,
    "Y": 37,
    "Info": ""
  },
  {
    "PlanetId": 661,
    "OwnerId": 137989,
    "X": 9,
    "Y": 29,
    "Info": ""
  },
  {
    "PlanetId": 662,
    "OwnerId": 173288,
    "X": 9,
    "Y": 29,
    "Info": ""
  },
  {
    "PlanetId": 663,
    "OwnerId": 130342,
    "X": 9,
    "Y": 29,
    "Info": ""
  },
  {
    "PlanetId": 664,
    "OwnerId": 185146,
    "X": 9,
    "Y": 29,
    "Info": ""
  },
  {
    "PlanetId": 665,
    "OwnerId": 97439,
    "X": 9,
    "Y": 29,
    "Info": ""
  },
  {
    "PlanetId": 666,
    "OwnerId": 147620,
    "X": 9,
    "Y": 29,
    "Info": ""
  },
  {
    "PlanetId": 667,
    "OwnerId": 204723,
    "X": 9,
    "Y": 29,
    "Info": ""
  },
  {
    "PlanetId": 668,
    "OwnerId": 110735,
    "X": 9,
    "Y": 29,
    "Info": ""
  },
  {
    "PlanetId": 669,
    "OwnerId": 139242,
    "X": 9,
    "Y": 22,
    "Info": ""
  },
  {
    "PlanetId": 670,
    "OwnerId": 178256,
    "X": 9,
    "Y": 22,
    "Info": ""
  },
  {
    "PlanetId": 671,
    "OwnerId": 129769,
    "X": 9,
    "Y": 22,
    "Info": ""
  },
  {
    "PlanetId": 672,
    "OwnerId": 211656,
    "X": 9,
    "Y": 22,
    "Info": ""
  },
  {
    "PlanetId": 673,
    "OwnerId": 213217,
    "X": 9,
    "Y": 22,
    "Info": ""
  },
  {
    "PlanetId": 674,
    "OwnerId": 191017,
    "X": 9,
    "Y": 22,
    "Info": ""
  },
  {
    "PlanetId": 675,
    "OwnerId": 63916,
    "X": 9,
    "Y": 22,
    "Info": ""
  },
  {
    "PlanetId": 676,
    "OwnerId": 58932,
    "X": 9,
    "Y": 27,
    "Info": ""
  },
  {
    "PlanetId": 677,
    "OwnerId": 195478,
    "X": 9,
    "Y": 27,
    "Info": ""
  },
  {
    "PlanetId": 678,
    "OwnerId": 223996,
    "X": 9,
    "Y": 194,
    "Info": ""
  },
  {
    "PlanetId": 679,
    "OwnerId": 213359,
    "X": 9,
    "Y": 2,
    "Info": ""
  },
  {
    "PlanetId": 680,
    "OwnerId": 242984,
    "X": 9,
    "Y": 2,
    "Info": ""
  },
  {
    "PlanetId": 681,
    "OwnerId": 51652,
    "X": 9,
    "Y": 2,
    "Info": ""
  },
  {
    "PlanetId": 682,
    "OwnerId": 144441,
    "X": 9,
    "Y": 2,
    "Info": ""
  },
  {
    "PlanetId": 683,
    "OwnerId": 67616,
    "X": 9,
    "Y": 2,
    "Info": ""
  },
  {
    "PlanetId": 684,
    "OwnerId": 254148,
    "X": 9,
    "Y": 2,
    "Info": ""
  },
  {
    "PlanetId": 685,
    "OwnerId": 255695,
    "X": 9,
    "Y": 2,
    "Info": ""
  },
  {
    "PlanetId": 686,
    "OwnerId": 174938,
    "X": 9,
    "Y": 2,
    "Info": ""
  },
  {
    "PlanetId": 687,
    "OwnerId": 252537,
    "X": 9,
    "Y": 2,
    "Info": ""
  },
  {
    "PlanetId": 688,
    "OwnerId": 44726,
    "X": 9,
    "Y": 2,
    "Info": ""
  },
  {
    "PlanetId": 689,
    "OwnerId": 183938,
    "X": 9,
    "Y": 2,
    "Info": ""
  },
  {
    "PlanetId": 690,
    "OwnerId": 106666,
    "X": 9,
    "Y": 2,
    "Info": ""
  },
  {
    "PlanetId": 691,
    "OwnerId": 197751,
    "X": 9,
    "Y": 186,
    "Info": ""
  },
  {
    "PlanetId": 692,
    "OwnerId": 213323,
    "X": 9,
    "Y": 186,
    "Info": ""
  },
  {
    "PlanetId": 693,
    "OwnerId": 214730,
    "X": 9,
    "Y": 186,
    "Info": ""
  },
  {
    "PlanetId": 694,
    "OwnerId": 215269,
    "X": 9,
    "Y": 186,
    "Info": ""
  },
  {
    "PlanetId": 695,
    "OwnerId": 207185,
    "X": 9,
    "Y": 186,
    "Info": ""
  },
  {
    "PlanetId": 696,
    "OwnerId": 64298,
    "X": 9,
    "Y": 186,
    "Info": ""
  },
  {
    "PlanetId": 697,
    "OwnerId": 77102,
    "X": 9,
    "Y": 158,
    "Info": ""
  },
  {
    "PlanetId": 698,
    "OwnerId": 101537,
    "X": 9,
    "Y": 158,
    "Info": ""
  },
  {
    "PlanetId": 699,
    "OwnerId": 122751,
    "X": 9,
    "Y": 158,
    "Info": ""
  },
  {
    "PlanetId": 700,
    "OwnerId": 78498,
    "X": 9,
    "Y": 158,
    "Info": ""
  },
  {
    "PlanetId": 701,
    "OwnerId": 100993,
    "X": 9,
    "Y": 158,
    "Info": ""
  },
  {
    "PlanetId": 702,
    "OwnerId": 92940,
    "X": 9,
    "Y": 158,
    "Info": ""
  },
  {
    "PlanetId": 703,
    "OwnerId": 163605,
    "X": 9,
    "Y": 18,
    "Info": ""
  },
  {
    "PlanetId": 704,
    "OwnerId": 73648,
    "X": 9,
    "Y": 18,
    "Info": ""
  },
  {
    "PlanetId": 705,
    "OwnerId": 176989,
    "X": 9,
    "Y": 18,
    "Info": ""
  },
  {
    "PlanetId": 706,
    "OwnerId": 39340,
    "X": 9,
    "Y": 18,
    "Info": ""
  },
  {
    "PlanetId": 707,
    "OwnerId": 210383,
    "X": 9,
    "Y": 18,
    "Info": ""
  },
  {
    "PlanetId": 708,
    "OwnerId": 107223,
    "X": 9,
    "Y": 18,
    "Info": ""
  },
  {
    "PlanetId": 709,
    "OwnerId": 40580,
    "X": 9,
    "Y": 18,
    "Info": ""
  },
  {
    "PlanetId": 710,
    "OwnerId": 145977,
    "X": 9,
    "Y": 156,
    "Info": ""
  },
  {
    "PlanetId": 711,
    "OwnerId": 42217,
    "X": 9,
    "Y": 155,
    "Info": ""
  },
  {
    "PlanetId": 712,
    "OwnerId": 125422,
    "X": 9,
    "Y": 155,
    "Info": ""
  },
  {
    "PlanetId": 713,
    "OwnerId": 163170,
    "X": 9,
    "Y": 155,
    "Info": ""
  },
  {
    "PlanetId": 714,
    "OwnerId": 63583,
    "X": 9,
    "Y": 155,
    "Info": ""
  },
  {
    "PlanetId": 715,
    "OwnerId": 163938,
    "X": 9,
    "Y": 155,
    "Info": ""
  },
  {
    "PlanetId": 716,
    "OwnerId": 93454,
    "X": 9,
    "Y": 155,
    "Info": ""
  },
  {
    "PlanetId": 717,
    "OwnerId": 99145,
    "X": 9,
    "Y": 137,
    "Info": ""
  },
  {
    "PlanetId": 718,
    "OwnerId": 146876,
    "X": 9,
    "Y": 137,
    "Info": ""
  },
  {
    "PlanetId": 719,
    "OwnerId": 169442,
    "X": 9,
    "Y": 137,
    "Info": ""
  },
  {
    "PlanetId": 720,
    "OwnerId": 162891,
    "X": 9,
    "Y": 137,
    "Info": ""
  },
  {
    "PlanetId": 721,
    "OwnerId": 39020,
    "X": 9,
    "Y": 137,
    "Info": ""
  },
  {
    "PlanetId": 722,
    "OwnerId": 71212,
    "X": 9,
    "Y": 124,
    "Info": ""
  },
  {
    "PlanetId": 723,
    "OwnerId": 110603,
    "X": 9,
    "Y": 124,
    "Info": ""
  },
  {
    "PlanetId": 724,
    "OwnerId": 52752,
    "X": 9,
    "Y": 124,
    "Info": ""
  },
  {
    "PlanetId": 725,
    "OwnerId": 143108,
    "X": 9,
    "Y": 124,
    "Info": ""
  },
  {
    "PlanetId": 726,
    "OwnerId": 93444,
    "X": 9,
    "Y": 124,
    "Info": ""
  },
  {
    "PlanetId": 727,
    "OwnerId": 98810,
    "X": 9,
    "Y": 110,
    "Info": ""
  },
  {
    "PlanetId": 728,
    "OwnerId": 107636,
    "X": 9,
    "Y": 110,
    "Info": ""
  },
  {
    "PlanetId": 729,
    "OwnerId": 187453,
    "X": 9,
    "Y": 110,
    "Info": ""
  },
  {
    "PlanetId": 730,
    "OwnerId": 248266,
    "X": 9,
    "Y": 106,
    "Info": ""
  },
  {
    "PlanetId": 731,
    "OwnerId": 62291,
    "X": 9,
    "Y": 106,
    "Info": ""
  },
  {
    "PlanetId": 732,
    "OwnerId": 127922,
    "X": 9,
    "Y": 106,
    "Info": ""
  },
  {
    "PlanetId": 733,
    "OwnerId": 58876,
    "X": 9,
    "Y": 102,
    "Info": ""
  },
  {
    "PlanetId": 734,
    "OwnerId": 120935,
    "X": 9,
    "Y": 102,
    "Info": ""
  },
  {
    "PlanetId": 735,
    "OwnerId": 185195,
    "X": 9,
    "Y": 102,
    "Info": ""
  },
  {
    "PlanetId": 736,
    "OwnerId": 209397,
    "X": 9,
    "Y": 102,
    "Info": ""
  },
  {
    "PlanetId": 737,
    "OwnerId": 47033,
    "X": 9,
    "Y": 107,
    "Info": ""
  },
  {
    "PlanetId": 738,
    "OwnerId": 58157,
    "X": 9,
    "Y": 107,
    "Info": ""
  },
  {
    "PlanetId": 739,
    "OwnerId": 146852,
    "X": 8,
    "Y": 97,
    "Info": ""
  },
  {
    "PlanetId": 740,
    "OwnerId": 165811,
    "X": 8,
    "Y": 97,
    "Info": ""
  },
  {
    "PlanetId": 741,
    "OwnerId": 141945,
    "X": 8,
    "Y": 97,
    "Info": ""
  },
  {
    "PlanetId": 742,
    "OwnerId": 147761,
    "X": 8,
    "Y": 97,
    "Info": ""
  },
  {
    "PlanetId": 743,
    "OwnerId": 182616,
    "X": 8,
    "Y": 97,
    "Info": ""
  },
  {
    "PlanetId": 744,
    "OwnerId": 105452,
    "X": 8,
    "Y": 97,
    "Info": ""
  },
  {
    "PlanetId": 745,
    "OwnerId": 75724,
    "X": 8,
    "Y": 95,
    "Info": ""
  },
  {
    "PlanetId": 746,
    "OwnerId": 87062,
    "X": 8,
    "Y": 95,
    "Info": ""
  },
  {
    "PlanetId": 747,
    "OwnerId": 176877,
    "X": 8,
    "Y": 95,
    "Info": ""
  },
  {
    "PlanetId": 748,
    "OwnerId": 208787,
    "X": 8,
    "Y": 86,
    "Info": ""
  },
  {
    "PlanetId": 749,
    "OwnerId": 141749,
    "X": 8,
    "Y": 86,
    "Info": ""
  },
  {
    "PlanetId": 750,
    "OwnerId": 172268,
    "X": 9,
    "Y": 1,
    "Info": ""
  },
  {
    "PlanetId": 751,
    "OwnerId": 52699,
    "X": 9,
    "Y": 1,
    "Info": ""
  },
  {
    "PlanetId": 752,
    "OwnerId": 174450,
    "X": 9,
    "Y": 1,
    "Info": ""
  },
  {
    "PlanetId": 753,
    "OwnerId": 76715,
    "X": 9,
    "Y": 1,
    "Info": ""
  },
  {
    "PlanetId": 754,
    "OwnerId": 97837,
    "X": 9,
    "Y": 1,
    "Info": ""
  },
  {
    "PlanetId": 755,
    "OwnerId": 43484,
    "X": 9,
    "Y": 1,
    "Info": ""
  },
  {
    "PlanetId": 756,
    "OwnerId": 176884,
    "X": 9,
    "Y": 1,
    "Info": ""
  },
  {
    "PlanetId": 757,
    "OwnerId": 74208,
    "X": 9,
    "Y": 1,
    "Info": ""
  },
  {
    "PlanetId": 758,
    "OwnerId": 142073,
    "X": 9,
    "Y": 1,
    "Info": ""
  },
  {
    "PlanetId": 759,
    "OwnerId": 138412,
    "X": 9,
    "Y": 1,
    "Info": ""
  },
  {
    "PlanetId": 760,
    "OwnerId": 103110,
    "X": 9,
    "Y": 1,
    "Info": ""
  },
  {
    "PlanetId": 761,
    "OwnerId": 118420,
    "X": 9,
    "Y": 1,
    "Info": ""
  },
  {
    "PlanetId": 762,
    "OwnerId": 245588,
    "X": 8,
    "Y": 82,
    "Info": ""
  },
  {
    "PlanetId": 763,
    "OwnerId": 117003,
    "X": 8,
    "Y": 81,
    "Info": ""
  },
  {
    "PlanetId": 764,
    "OwnerId": 247740,
    "X": 8,
    "Y": 73,
    "Info": ""
  },
  {
    "PlanetId": 765,
    "OwnerId": 265138,
    "X": 8,
    "Y": 72,
    "Info": ""
  },
  {
    "PlanetId": 766,
    "OwnerId": 220589,
    "X": 9,
    "Y": 138,
    "Info": ""
  },
  {
    "PlanetId": 767,
    "OwnerId": 76121,
    "X": 9,
    "Y": 138,
    "Info": ""
  },
  {
    "PlanetId": 768,
    "OwnerId": 262035,
    "X": 9,
    "Y": 142,
    "Info": ""
  },
  {
    "PlanetId": 769,
    "OwnerId": 256710,
    "X": 9,
    "Y": 142,
    "Info": ""
  },
  {
    "PlanetId": 770,
    "OwnerId": 265784,
    "X": 8,
    "Y": 66,
    "Info": ""
  },
  {
    "PlanetId": 771,
    "OwnerId": 47759,
    "X": 8,
    "Y": 66,
    "Info": ""
  },
  {
    "PlanetId": 772,
    "OwnerId": 153154,
    "X": 8,
    "Y": 66,
    "Info": ""
  },
  {
    "PlanetId": 773,
    "OwnerId": 55174,
    "X": 8,
    "Y": 49,
    "Info": ""
  },
  {
    "PlanetId": 774,
    "OwnerId": 150000,
    "X": 8,
    "Y": 49,
    "Info": ""
  },
  {
    "PlanetId": 775,
    "OwnerId": 153154,
    "X": 8,
    "Y": 49,
    "Info": ""
  },
  {
    "PlanetId": 776,
    "OwnerId": 61872,
    "X": 8,
    "Y": 47,
    "Info": ""
  },
  {
    "PlanetId": 777,
    "OwnerId": 71303,
    "X": 8,
    "Y": 47,
    "Info": ""
  },
  {
    "PlanetId": 778,
    "OwnerId": 132390,
    "X": 8,
    "Y": 47,
    "Info": ""
  },
  {
    "PlanetId": 779,
    "OwnerId": 183756,
    "X": 8,
    "Y": 47,
    "Info": ""
  },
  {
    "PlanetId": 780,
    "OwnerId": 110193,
    "X": 8,
    "Y": 47,
    "Info": ""
  },
  {
    "PlanetId": 781,
    "OwnerId": 100264,
    "X": 8,
    "Y": 32,
    "Info": ""
  },
  {
    "PlanetId": 782,
    "OwnerId": 104048,
    "X": 8,
    "Y": 32,
    "Info": ""
  },
  {
    "PlanetId": 783,
    "OwnerId": 129750,
    "X": 8,
    "Y": 32,
    "Info": ""
  },
  {
    "PlanetId": 784,
    "OwnerId": 150562,
    "X": 8,
    "Y": 32,
    "Info": ""
  },
  {
    "PlanetId": 785,
    "OwnerId": 158908,
    "X": 8,
    "Y": 32,
    "Info": ""
  },
  {
    "PlanetId": 786,
    "OwnerId": 114600,
    "X": 8,
    "Y": 37,
    "Info": ""
  },
  {
    "PlanetId": 787,
    "OwnerId": 163843,
    "X": 8,
    "Y": 37,
    "Info": ""
  },
  {
    "PlanetId": 788,
    "OwnerId": 169799,
    "X": 8,
    "Y": 37,
    "Info": ""
  },
  {
    "PlanetId": 789,
    "OwnerId": 191294,
    "X": 8,
    "Y": 37,
    "Info": ""
  },
  {
    "PlanetId": 790,
    "OwnerId": 205981,
    "X": 8,
    "Y": 37,
    "Info": ""
  },
  {
    "PlanetId": 791,
    "OwnerId": 227587,
    "X": 8,
    "Y": 44,
    "Info": ""
  },
  {
    "PlanetId": 792,
    "OwnerId": 239875,
    "X": 8,
    "Y": 44,
    "Info": ""
  },
  {
    "PlanetId": 793,
    "OwnerId": 263018,
    "X": 8,
    "Y": 44,
    "Info": ""
  },
  {
    "PlanetId": 794,
    "OwnerId": 53281,
    "X": 8,
    "Y": 31,
    "Info": ""
  },
  {
    "PlanetId": 795,
    "OwnerId": 41421,
    "X": 8,
    "Y": 21,
    "Info": ""
  },
  {
    "PlanetId": 796,
    "OwnerId": 42819,
    "X": 8,
    "Y": 21,
    "Info": ""
  },
  {
    "PlanetId": 797,
    "OwnerId": 206806,
    "X": 8,
    "Y": 21,
    "Info": ""
  },
  {
    "PlanetId": 798,
    "OwnerId": 55831,
    "X": 8,
    "Y": 21,
    "Info": ""
  },
  {
    "PlanetId": 799,
    "OwnerId": 70304,
    "X": 8,
    "Y": 21,
    "Info": ""
  },
  {
    "PlanetId": 800,
    "OwnerId": 68966,
    "X": 8,
    "Y": 21,
    "Info": ""
  },
  {
    "PlanetId": 801,
    "OwnerId": 240500,
    "X": 8,
    "Y": 21,
    "Info": ""
  },
  {
    "PlanetId": 802,
    "OwnerId": 236768,
    "X": 8,
    "Y": 21,
    "Info": ""
  },
  {
    "PlanetId": 803,
    "OwnerId": 43629,
    "X": 8,
    "Y": 21,
    "Info": ""
  },
  {
    "PlanetId": 804,
    "OwnerId": 72282,
    "X": 8,
    "Y": 175,
    "Info": ""
  },
  {
    "PlanetId": 805,
    "OwnerId": 67795,
    "X": 8,
    "Y": 175,
    "Info": ""
  },
  {
    "PlanetId": 806,
    "OwnerId": 70800,
    "X": 8,
    "Y": 175,
    "Info": ""
  },
  {
    "PlanetId": 807,
    "OwnerId": 38586,
    "X": 8,
    "Y": 175,
    "Info": ""
  },
  {
    "PlanetId": 808,
    "OwnerId": 122050,
    "X": 8,
    "Y": 175,
    "Info": ""
  },
  {
    "PlanetId": 809,
    "OwnerId": 54340,
    "X": 8,
    "Y": 175,
    "Info": ""
  },
  {
    "PlanetId": 810,
    "OwnerId": 71479,
    "X": 8,
    "Y": 175,
    "Info": ""
  },
  {
    "PlanetId": 811,
    "OwnerId": 185206,
    "X": 8,
    "Y": 175,
    "Info": ""
  },
  {
    "PlanetId": 812,
    "OwnerId": 41117,
    "X": 8,
    "Y": 175,
    "Info": ""
  },
  {
    "PlanetId": 813,
    "OwnerId": 180702,
    "X": 8,
    "Y": 175,
    "Info": ""
  },
  {
    "PlanetId": 814,
    "OwnerId": 44525,
    "X": 8,
    "Y": 174,
    "Info": ""
  },
  {
    "PlanetId": 815,
    "OwnerId": 183324,
    "X": 8,
    "Y": 174,
    "Info": ""
  },
  {
    "PlanetId": 816,
    "OwnerId": 167304,
    "X": 8,
    "Y": 174,
    "Info": ""
  },
  {
    "PlanetId": 817,
    "OwnerId": 170826,
    "X": 8,
    "Y": 174,
    "Info": ""
  },
  {
    "PlanetId": 818,
    "OwnerId": 186592,
    "X": 8,
    "Y": 174,
    "Info": ""
  },
  {
    "PlanetId": 819,
    "OwnerId": 54340,
    "X": 8,
    "Y": 174,
    "Info": ""
  },
  {
    "PlanetId": 820,
    "OwnerId": 191021,
    "X": 8,
    "Y": 173,
    "Info": ""
  },
  {
    "PlanetId": 821,
    "OwnerId": 225863,
    "X": 8,
    "Y": 173,
    "Info": ""
  },
  {
    "PlanetId": 822,
    "OwnerId": 54340,
    "X": 8,
    "Y": 173,
    "Info": ""
  },
  {
    "PlanetId": 823,
    "OwnerId": 54340,
    "X": 8,
    "Y": 172,
    "Info": ""
  },
  {
    "PlanetId": 824,
    "OwnerId": 150582,
    "X": 8,
    "Y": 167,
    "Info": ""
  },
  {
    "PlanetId": 825,
    "OwnerId": 151256,
    "X": 8,
    "Y": 167,
    "Info": ""
  },
  {
    "PlanetId": 826,
    "OwnerId": 172715,
    "X": 8,
    "Y": 167,
    "Info": ""
  },
  {
    "PlanetId": 827,
    "OwnerId": 73332,
    "X": 8,
    "Y": 167,
    "Info": ""
  },
  {
    "PlanetId": 828,
    "OwnerId": 177572,
    "X": 8,
    "Y": 167,
    "Info": ""
  },
  {
    "PlanetId": 829,
    "OwnerId": 66024,
    "X": 8,
    "Y": 167,
    "Info": ""
  },
  {
    "PlanetId": 830,
    "OwnerId": 79610,
    "X": 8,
    "Y": 167,
    "Info": ""
  },
  {
    "PlanetId": 831,
    "OwnerId": 93440,
    "X": 8,
    "Y": 53,
    "Info": ""
  },
  {
    "PlanetId": 832,
    "OwnerId": 68394,
    "X": 8,
    "Y": 53,
    "Info": ""
  },
  {
    "PlanetId": 833,
    "OwnerId": 63213,
    "X": 8,
    "Y": 89,
    "Info": ""
  },
  {
    "PlanetId": 834,
    "OwnerId": 133714,
    "X": 8,
    "Y": 89,
    "Info": ""
  },
  {
    "PlanetId": 835,
    "OwnerId": 46598,
    "X": 8,
    "Y": 89,
    "Info": ""
  },
  {
    "PlanetId": 836,
    "OwnerId": 41441,
    "X": 8,
    "Y": 89,
    "Info": ""
  },
  {
    "PlanetId": 837,
    "OwnerId": 163769,
    "X": 8,
    "Y": 89,
    "Info": ""
  },
  {
    "PlanetId": 838,
    "OwnerId": 190951,
    "X": 8,
    "Y": 89,
    "Info": ""
  },
  {
    "PlanetId": 839,
    "OwnerId": 52464,
    "X": 8,
    "Y": 145,
    "Info": ""
  },
  {
    "PlanetId": 840,
    "OwnerId": 164133,
    "X": 8,
    "Y": 149,
    "Info": ""
  },
  {
    "PlanetId": 841,
    "OwnerId": 181883,
    "X": 8,
    "Y": 149,
    "Info": ""
  },
  {
    "PlanetId": 842,
    "OwnerId": 256016,
    "X": 8,
    "Y": 149,
    "Info": ""
  },
  {
    "PlanetId": 843,
    "OwnerId": 173658,
    "X": 8,
    "Y": 16,
    "Info": ""
  },
  {
    "PlanetId": 844,
    "OwnerId": 170398,
    "X": 8,
    "Y": 16,
    "Info": ""
  },
  {
    "PlanetId": 845,
    "OwnerId": 103743,
    "X": 8,
    "Y": 16,
    "Info": ""
  },
  {
    "PlanetId": 846,
    "OwnerId": 43118,
    "X": 8,
    "Y": 16,
    "Info": ""
  },
  {
    "PlanetId": 847,
    "OwnerId": 39426,
    "X": 8,
    "Y": 16,
    "Info": ""
  },
  {
    "PlanetId": 848,
    "OwnerId": 46242,
    "X": 8,
    "Y": 135,
    "Info": ""
  },
  {
    "PlanetId": 849,
    "OwnerId": 44352,
    "X": 8,
    "Y": 135,
    "Info": ""
  },
  {
    "PlanetId": 850,
    "OwnerId": 115071,
    "X": 8,
    "Y": 135,
    "Info": ""
  },
  {
    "PlanetId": 851,
    "OwnerId": 77435,
    "X": 8,
    "Y": 135,
    "Info": ""
  },
  {
    "PlanetId": 852,
    "OwnerId": 129194,
    "X": 8,
    "Y": 135,
    "Info": ""
  },
  {
    "PlanetId": 853,
    "OwnerId": 132945,
    "X": 8,
    "Y": 135,
    "Info": ""
  },
  {
    "PlanetId": 854,
    "OwnerId": 43863,
    "X": 8,
    "Y": 126,
    "Info": ""
  },
  {
    "PlanetId": 855,
    "OwnerId": 104643,
    "X": 8,
    "Y": 124,
    "Info": ""
  },
  {
    "PlanetId": 856,
    "OwnerId": 104216,
    "X": 8,
    "Y": 124,
    "Info": ""
  },
  {
    "PlanetId": 857,
    "OwnerId": 41135,
    "X": 8,
    "Y": 124,
    "Info": ""
  },
  {
    "PlanetId": 858,
    "OwnerId": 127596,
    "X": 8,
    "Y": 12,
    "Info": ""
  },
  {
    "PlanetId": 859,
    "OwnerId": 78732,
    "X": 8,
    "Y": 12,
    "Info": ""
  },
  {
    "PlanetId": 860,
    "OwnerId": 97469,
    "X": 8,
    "Y": 12,
    "Info": ""
  },
  {
    "PlanetId": 861,
    "OwnerId": 116363,
    "X": 8,
    "Y": 12,
    "Info": ""
  },
  {
    "PlanetId": 862,
    "OwnerId": 63898,
    "X": 8,
    "Y": 12,
    "Info": ""
  },
  {
    "PlanetId": 863,
    "OwnerId": 90414,
    "X": 8,
    "Y": 12,
    "Info": ""
  },
  {
    "PlanetId": 864,
    "OwnerId": 58022,
    "X": 8,
    "Y": 12,
    "Info": ""
  },
  {
    "PlanetId": 865,
    "OwnerId": 164754,
    "X": 8,
    "Y": 12,
    "Info": ""
  },
  {
    "PlanetId": 866,
    "OwnerId": 50002,
    "X": 8,
    "Y": 12,
    "Info": ""
  },
  {
    "PlanetId": 867,
    "OwnerId": 80169,
    "X": 8,
    "Y": 12,
    "Info": ""
  },
  {
    "PlanetId": 868,
    "OwnerId": 84745,
    "X": 8,
    "Y": 12,
    "Info": ""
  },
  {
    "PlanetId": 869,
    "OwnerId": 120022,
    "X": 8,
    "Y": 120,
    "Info": ""
  },
  {
    "PlanetId": 870,
    "OwnerId": 40255,
    "X": 8,
    "Y": 120,
    "Info": ""
  },
  {
    "PlanetId": 871,
    "OwnerId": 256156,
    "X": 8,
    "Y": 120,
    "Info": ""
  },
  {
    "PlanetId": 872,
    "OwnerId": 234581,
    "X": 8,
    "Y": 109,
    "Info": ""
  },
  {
    "PlanetId": 873,
    "OwnerId": 87293,
    "X": 8,
    "Y": 109,
    "Info": ""
  },
  {
    "PlanetId": 874,
    "OwnerId": 39400,
    "X": 8,
    "Y": 109,
    "Info": ""
  },
  {
    "PlanetId": 875,
    "OwnerId": 85198,
    "X": 8,
    "Y": 118,
    "Info": ""
  },
  {
    "PlanetId": 876,
    "OwnerId": 73467,
    "X": 8,
    "Y": 118,
    "Info": ""
  },
  {
    "PlanetId": 877,
    "OwnerId": 197096,
    "X": 8,
    "Y": 118,
    "Info": ""
  },
  {
    "PlanetId": 878,
    "OwnerId": 138019,
    "X": 8,
    "Y": 118,
    "Info": ""
  },
  {
    "PlanetId": 879,
    "OwnerId": 95762,
    "X": 8,
    "Y": 118,
    "Info": ""
  },
  {
    "PlanetId": 880,
    "OwnerId": 57646,
    "X": 8,
    "Y": 114,
    "Info": ""
  },
  {
    "PlanetId": 881,
    "OwnerId": 46132,
    "X": 8,
    "Y": 114,
    "Info": ""
  },
  {
    "PlanetId": 882,
    "OwnerId": 130403,
    "X": 8,
    "Y": 114,
    "Info": ""
  },
  {
    "PlanetId": 883,
    "OwnerId": 77011,
    "X": 8,
    "Y": 114,
    "Info": ""
  },
  {
    "PlanetId": 884,
    "OwnerId": 94169,
    "X": 8,
    "Y": 114,
    "Info": ""
  },
  {
    "PlanetId": 885,
    "OwnerId": 42217,
    "X": 8,
    "Y": 105,
    "Info": ""
  },
  {
    "PlanetId": 886,
    "OwnerId": 39020,
    "X": 8,
    "Y": 105,
    "Info": ""
  },
  {
    "PlanetId": 887,
    "OwnerId": 187675,
    "X": 8,
    "Y": 105,
    "Info": ""
  },
  {
    "PlanetId": 888,
    "OwnerId": 207982,
    "X": 8,
    "Y": 105,
    "Info": ""
  },
  {
    "PlanetId": 889,
    "OwnerId": 142131,
    "X": 8,
    "Y": 105,
    "Info": ""
  },
  {
    "PlanetId": 890,
    "OwnerId": 71539,
    "X": 8,
    "Y": 103,
    "Info": ""
  },
  {
    "PlanetId": 891,
    "OwnerId": 105452,
    "X": 8,
    "Y": 103,
    "Info": ""
  },
  {
    "PlanetId": 892,
    "OwnerId": 138507,
    "X": 8,
    "Y": 103,
    "Info": ""
  },
  {
    "PlanetId": 893,
    "OwnerId": 150578,
    "X": 8,
    "Y": 103,
    "Info": ""
  },
  {
    "PlanetId": 894,
    "OwnerId": 154326,
    "X": 8,
    "Y": 103,
    "Info": ""
  },
  {
    "PlanetId": 895,
    "OwnerId": 119119,
    "X": 8,
    "Y": 103,
    "Info": ""
  },
  {
    "PlanetId": 896,
    "OwnerId": 41663,
    "X": 8,
    "Y": 1,
    "Info": ""
  },
  {
    "PlanetId": 897,
    "OwnerId": 60946,
    "X": 8,
    "Y": 1,
    "Info": ""
  },
  {
    "PlanetId": 898,
    "OwnerId": 53780,
    "X": 8,
    "Y": 1,
    "Info": ""
  },
  {
    "PlanetId": 899,
    "OwnerId": 76065,
    "X": 8,
    "Y": 1,
    "Info": ""
  },
  {
    "PlanetId": 900,
    "OwnerId": 153453,
    "X": 8,
    "Y": 1,
    "Info": ""
  },
  {
    "PlanetId": 901,
    "OwnerId": 115513,
    "X": 8,
    "Y": 1,
    "Info": ""
  },
  {
    "PlanetId": 902,
    "OwnerId": 219750,
    "X": 8,
    "Y": 1,
    "Info": ""
  },
  {
    "PlanetId": 903,
    "OwnerId": 222632,
    "X": 8,
    "Y": 1,
    "Info": ""
  },
  {
    "PlanetId": 904,
    "OwnerId": 47171,
    "X": 8,
    "Y": 1,
    "Info": ""
  },
  {
    "PlanetId": 905,
    "OwnerId": 226947,
    "X": 8,
    "Y": 1,
    "Info": ""
  },
  {
    "PlanetId": 906,
    "OwnerId": 238444,
    "X": 8,
    "Y": 1,
    "Info": ""
  },
  {
    "PlanetId": 907,
    "OwnerId": 111047,
    "X": 7,
    "Y": 98,
    "Info": ""
  },
  {
    "PlanetId": 908,
    "OwnerId": 146852,
    "X": 7,
    "Y": 98,
    "Info": ""
  },
  {
    "PlanetId": 909,
    "OwnerId": 60886,
    "X": 7,
    "Y": 98,
    "Info": ""
  },
  {
    "PlanetId": 910,
    "OwnerId": 81244,
    "X": 7,
    "Y": 98,
    "Info": ""
  },
  {
    "PlanetId": 911,
    "OwnerId": 155441,
    "X": 7,
    "Y": 98,
    "Info": ""
  },
  {
    "PlanetId": 912,
    "OwnerId": 39400,
    "X": 8,
    "Y": 153,
    "Info": ""
  },
  {
    "PlanetId": 913,
    "OwnerId": 122440,
    "X": 8,
    "Y": 139,
    "Info": ""
  },
  {
    "PlanetId": 914,
    "OwnerId": 142441,
    "X": 8,
    "Y": 139,
    "Info": ""
  },
  {
    "PlanetId": 915,
    "OwnerId": 147258,
    "X": 8,
    "Y": 139,
    "Info": ""
  },
  {
    "PlanetId": 916,
    "OwnerId": 157707,
    "X": 8,
    "Y": 139,
    "Info": ""
  },
  {
    "PlanetId": 917,
    "OwnerId": 79233,
    "X": 7,
    "Y": 82,
    "Info": ""
  },
  {
    "PlanetId": 918,
    "OwnerId": 246684,
    "X": 7,
    "Y": 82,
    "Info": ""
  },
  {
    "PlanetId": 919,
    "OwnerId": 40048,
    "X": 7,
    "Y": 82,
    "Info": ""
  },
  {
    "PlanetId": 920,
    "OwnerId": 167944,
    "X": 8,
    "Y": 0,
    "Info": ""
  },
  {
    "PlanetId": 921,
    "OwnerId": 44726,
    "X": 8,
    "Y": 0,
    "Info": ""
  },
  {
    "PlanetId": 922,
    "OwnerId": 229478,
    "X": 8,
    "Y": 0,
    "Info": ""
  },
  {
    "PlanetId": 923,
    "OwnerId": 39488,
    "X": 8,
    "Y": 0,
    "Info": ""
  },
  {
    "PlanetId": 924,
    "OwnerId": 92243,
    "X": 8,
    "Y": 0,
    "Info": ""
  },
  {
    "PlanetId": 925,
    "OwnerId": 107605,
    "X": 8,
    "Y": 0,
    "Info": ""
  },
  {
    "PlanetId": 926,
    "OwnerId": 75499,
    "X": 8,
    "Y": 0,
    "Info": ""
  },
  {
    "PlanetId": 927,
    "OwnerId": 55577,
    "X": 8,
    "Y": 0,
    "Info": ""
  },
  {
    "PlanetId": 928,
    "OwnerId": 203331,
    "X": 8,
    "Y": 0,
    "Info": ""
  },
  {
    "PlanetId": 929,
    "OwnerId": 40320,
    "X": 8,
    "Y": 0,
    "Info": ""
  },
  {
    "PlanetId": 930,
    "OwnerId": 42231,
    "X": 8,
    "Y": 0,
    "Info": ""
  },
  {
    "PlanetId": 931,
    "OwnerId": 83326,
    "X": 8,
    "Y": 0,
    "Info": ""
  },
  {
    "PlanetId": 932,
    "OwnerId": 198529,
    "X": 7,
    "Y": 76,
    "Info": ""
  },
  {
    "PlanetId": 933,
    "OwnerId": 127922,
    "X": 7,
    "Y": 73,
    "Info": ""
  },
  {
    "PlanetId": 934,
    "OwnerId": 123227,
    "X": 7,
    "Y": 68,
    "Info": ""
  },
  {
    "PlanetId": 935,
    "OwnerId": 91313,
    "X": 7,
    "Y": 60,
    "Info": ""
  },
  {
    "PlanetId": 936,
    "OwnerId": 104660,
    "X": 7,
    "Y": 79,
    "Info": ""
  },
  {
    "PlanetId": 937,
    "OwnerId": 175394,
    "X": 7,
    "Y": 79,
    "Info": ""
  },
  {
    "PlanetId": 938,
    "OwnerId": 46321,
    "X": 7,
    "Y": 79,
    "Info": ""
  },
  {
    "PlanetId": 939,
    "OwnerId": 95764,
    "X": 7,
    "Y": 79,
    "Info": ""
  },
  {
    "PlanetId": 940,
    "OwnerId": 184407,
    "X": 7,
    "Y": 79,
    "Info": ""
  },
  {
    "PlanetId": 941,
    "OwnerId": 87176,
    "X": 7,
    "Y": 79,
    "Info": ""
  },
  {
    "PlanetId": 942,
    "OwnerId": 88930,
    "X": 7,
    "Y": 79,
    "Info": ""
  },
  {
    "PlanetId": 943,
    "OwnerId": 157454,
    "X": 7,
    "Y": 79,
    "Info": ""
  },
  {
    "PlanetId": 944,
    "OwnerId": 225861,
    "X": 7,
    "Y": 54,
    "Info": ""
  },
  {
    "PlanetId": 945,
    "OwnerId": 173762,
    "X": 7,
    "Y": 54,
    "Info": ""
  },
  {
    "PlanetId": 946,
    "OwnerId": 103516,
    "X": 7,
    "Y": 50,
    "Info": ""
  },
  {
    "PlanetId": 947,
    "OwnerId": 146257,
    "X": 7,
    "Y": 50,
    "Info": ""
  },
  {
    "PlanetId": 948,
    "OwnerId": 197395,
    "X": 7,
    "Y": 42,
    "Info": ""
  },
  {
    "PlanetId": 949,
    "OwnerId": 247749,
    "X": 7,
    "Y": 45,
    "Info": ""
  },
  {
    "PlanetId": 950,
    "OwnerId": 55795,
    "X": 7,
    "Y": 45,
    "Info": ""
  },
  {
    "PlanetId": 951,
    "OwnerId": 55036,
    "X": 7,
    "Y": 36,
    "Info": ""
  },
  {
    "PlanetId": 952,
    "OwnerId": 85049,
    "X": 7,
    "Y": 36,
    "Info": ""
  },
  {
    "PlanetId": 953,
    "OwnerId": 190951,
    "X": 7,
    "Y": 36,
    "Info": ""
  },
  {
    "PlanetId": 954,
    "OwnerId": 107423,
    "X": 7,
    "Y": 36,
    "Info": ""
  },
  {
    "PlanetId": 955,
    "OwnerId": 86590,
    "X": 7,
    "Y": 36,
    "Info": ""
  },
  {
    "PlanetId": 956,
    "OwnerId": 78082,
    "X": 7,
    "Y": 36,
    "Info": ""
  },
  {
    "PlanetId": 957,
    "OwnerId": 73802,
    "X": 7,
    "Y": 36,
    "Info": ""
  },
  {
    "PlanetId": 958,
    "OwnerId": 75836,
    "X": 7,
    "Y": 36,
    "Info": ""
  },
  {
    "PlanetId": 959,
    "OwnerId": 110080,
    "X": 7,
    "Y": 36,
    "Info": ""
  },
  {
    "PlanetId": 960,
    "OwnerId": 93990,
    "X": 7,
    "Y": 36,
    "Info": ""
  },
  {
    "PlanetId": 961,
    "OwnerId": 228345,
    "X": 7,
    "Y": 31,
    "Info": ""
  },
  {
    "PlanetId": 962,
    "OwnerId": 236653,
    "X": 7,
    "Y": 31,
    "Info": ""
  },
  {
    "PlanetId": 963,
    "OwnerId": 210383,
    "X": 7,
    "Y": 31,
    "Info": ""
  },
  {
    "PlanetId": 964,
    "OwnerId": 143007,
    "X": 7,
    "Y": 23,
    "Info": ""
  },
  {
    "PlanetId": 965,
    "OwnerId": 167086,
    "X": 7,
    "Y": 23,
    "Info": ""
  },
  {
    "PlanetId": 966,
    "OwnerId": 184617,
    "X": 7,
    "Y": 23,
    "Info": ""
  },
  {
    "PlanetId": 967,
    "OwnerId": 196578,
    "X": 7,
    "Y": 23,
    "Info": ""
  },
  {
    "PlanetId": 968,
    "OwnerId": 200768,
    "X": 7,
    "Y": 23,
    "Info": ""
  },
  {
    "PlanetId": 969,
    "OwnerId": 68966,
    "X": 7,
    "Y": 23,
    "Info": ""
  },
  {
    "PlanetId": 970,
    "OwnerId": 204723,
    "X": 7,
    "Y": 21,
    "Info": ""
  },
  {
    "PlanetId": 971,
    "OwnerId": 68966,
    "X": 7,
    "Y": 21,
    "Info": ""
  },
  {
    "PlanetId": 972,
    "OwnerId": 126674,
    "X": 7,
    "Y": 200,
    "Info": ""
  },
  {
    "PlanetId": 973,
    "OwnerId": 127661,
    "X": 7,
    "Y": 200,
    "Info": ""
  },
  {
    "PlanetId": 974,
    "OwnerId": 141480,
    "X": 7,
    "Y": 200,
    "Info": ""
  },
  {
    "PlanetId": 975,
    "OwnerId": 162825,
    "X": 7,
    "Y": 200,
    "Info": ""
  },
  {
    "PlanetId": 976,
    "OwnerId": 189289,
    "X": 7,
    "Y": 200,
    "Info": ""
  },
  {
    "PlanetId": 977,
    "OwnerId": 87443,
    "X": 7,
    "Y": 200,
    "Info": ""
  },
  {
    "PlanetId": 978,
    "OwnerId": 86968,
    "X": 7,
    "Y": 200,
    "Info": ""
  },
  {
    "PlanetId": 979,
    "OwnerId": 47592,
    "X": 7,
    "Y": 200,
    "Info": ""
  },
  {
    "PlanetId": 980,
    "OwnerId": 102742,
    "X": 7,
    "Y": 198,
    "Info": ""
  },
  {
    "PlanetId": 981,
    "OwnerId": 222290,
    "X": 7,
    "Y": 195,
    "Info": ""
  },
  {
    "PlanetId": 982,
    "OwnerId": 239331,
    "X": 7,
    "Y": 195,
    "Info": ""
  },
  {
    "PlanetId": 983,
    "OwnerId": 189973,
    "X": 7,
    "Y": 195,
    "Info": ""
  },
  {
    "PlanetId": 984,
    "OwnerId": 222163,
    "X": 7,
    "Y": 56,
    "Info": ""
  },
  {
    "PlanetId": 985,
    "OwnerId": 240772,
    "X": 7,
    "Y": 56,
    "Info": ""
  },
  {
    "PlanetId": 986,
    "OwnerId": 73498,
    "X": 7,
    "Y": 92,
    "Info": ""
  },
  {
    "PlanetId": 987,
    "OwnerId": 40739,
    "X": 7,
    "Y": 92,
    "Info": ""
  },
  {
    "PlanetId": 988,
    "OwnerId": 66839,
    "X": 7,
    "Y": 92,
    "Info": ""
  },
  {
    "PlanetId": 989,
    "OwnerId": 55539,
    "X": 7,
    "Y": 92,
    "Info": ""
  },
  {
    "PlanetId": 990,
    "OwnerId": 196911,
    "X": 7,
    "Y": 92,
    "Info": ""
  },
  {
    "PlanetId": 991,
    "OwnerId": 104616,
    "X": 7,
    "Y": 92,
    "Info": ""
  },
  {
    "PlanetId": 992,
    "OwnerId": 124942,
    "X": 7,
    "Y": 194,
    "Info": ""
  },
  {
    "PlanetId": 993,
    "OwnerId": 147198,
    "X": 7,
    "Y": 194,
    "Info": ""
  },
  {
    "PlanetId": 994,
    "OwnerId": 159191,
    "X": 7,
    "Y": 194,
    "Info": ""
  },
  {
    "PlanetId": 995,
    "OwnerId": 182503,
    "X": 7,
    "Y": 194,
    "Info": ""
  },
  {
    "PlanetId": 996,
    "OwnerId": 196702,
    "X": 7,
    "Y": 194,
    "Info": ""
  },
  {
    "PlanetId": 997,
    "OwnerId": 133838,
    "X": 7,
    "Y": 181,
    "Info": ""
  },
  {
    "PlanetId": 998,
    "OwnerId": 142014,
    "X": 7,
    "Y": 181,
    "Info": ""
  },
  {
    "PlanetId": 999,
    "OwnerId": 146689,
    "X": 7,
    "Y": 181,
    "Info": ""
  },
  {
    "PlanetId": 1000,
    "OwnerId": 153910,
    "X": 7,
    "Y": 181,
    "Info": ""
  },
  {
    "PlanetId": 1001,
    "OwnerId": 155351,
    "X": 7,
    "Y": 181,
    "Info": ""
  },
  {
    "PlanetId": 1002,
    "OwnerId": 51039,
    "X": 7,
    "Y": 181,
    "Info": ""
  },
  {
    "PlanetId": 1003,
    "OwnerId": 151843,
    "X": 7,
    "Y": 192,
    "Info": ""
  },
  {
    "PlanetId": 1004,
    "OwnerId": 235104,
    "X": 7,
    "Y": 170,
    "Info": ""
  },
  {
    "PlanetId": 1005,
    "OwnerId": 64298,
    "X": 7,
    "Y": 184,
    "Info": ""
  },
  {
    "PlanetId": 1006,
    "OwnerId": 196540,
    "X": 7,
    "Y": 184,
    "Info": ""
  },
  {
    "PlanetId": 1007,
    "OwnerId": 210152,
    "X": 7,
    "Y": 184,
    "Info": ""
  },
  {
    "PlanetId": 1008,
    "OwnerId": 99924,
    "X": 7,
    "Y": 184,
    "Info": ""
  },
  {
    "PlanetId": 1009,
    "OwnerId": 140148,
    "X": 7,
    "Y": 163,
    "Info": ""
  },
  {
    "PlanetId": 1010,
    "OwnerId": 160589,
    "X": 7,
    "Y": 163,
    "Info": ""
  },
  {
    "PlanetId": 1011,
    "OwnerId": 188433,
    "X": 7,
    "Y": 163,
    "Info": ""
  },
  {
    "PlanetId": 1012,
    "OwnerId": 209728,
    "X": 7,
    "Y": 163,
    "Info": ""
  },
  {
    "PlanetId": 1013,
    "OwnerId": 211467,
    "X": 7,
    "Y": 163,
    "Info": ""
  },
  {
    "PlanetId": 1014,
    "OwnerId": 177572,
    "X": 7,
    "Y": 164,
    "Info": ""
  },
  {
    "PlanetId": 1015,
    "OwnerId": 141945,
    "X": 7,
    "Y": 16,
    "Info": ""
  },
  {
    "PlanetId": 1016,
    "OwnerId": 139905,
    "X": 7,
    "Y": 16,
    "Info": ""
  },
  {
    "PlanetId": 1017,
    "OwnerId": 194387,
    "X": 7,
    "Y": 16,
    "Info": ""
  },
  {
    "PlanetId": 1018,
    "OwnerId": 58383,
    "X": 7,
    "Y": 16,
    "Info": ""
  },
  {
    "PlanetId": 1019,
    "OwnerId": 113959,
    "X": 7,
    "Y": 150,
    "Info": ""
  },
  {
    "PlanetId": 1020,
    "OwnerId": 167473,
    "X": 7,
    "Y": 150,
    "Info": ""
  },
  {
    "PlanetId": 1021,
    "OwnerId": 68273,
    "X": 7,
    "Y": 150,
    "Info": ""
  },
  {
    "PlanetId": 1022,
    "OwnerId": 213443,
    "X": 7,
    "Y": 150,
    "Info": ""
  },
  {
    "PlanetId": 1023,
    "OwnerId": 214790,
    "X": 7,
    "Y": 150,
    "Info": ""
  },
  {
    "PlanetId": 1024,
    "OwnerId": 181883,
    "X": 7,
    "Y": 150,
    "Info": ""
  },
  {
    "PlanetId": 1025,
    "OwnerId": 203400,
    "X": 7,
    "Y": 150,
    "Info": ""
  },
  {
    "PlanetId": 1026,
    "OwnerId": 68629,
    "X": 7,
    "Y": 146,
    "Info": ""
  },
  {
    "PlanetId": 1027,
    "OwnerId": 114637,
    "X": 7,
    "Y": 146,
    "Info": ""
  },
  {
    "PlanetId": 1028,
    "OwnerId": 61697,
    "X": 7,
    "Y": 146,
    "Info": ""
  },
  {
    "PlanetId": 1029,
    "OwnerId": 164889,
    "X": 7,
    "Y": 146,
    "Info": ""
  },
  {
    "PlanetId": 1030,
    "OwnerId": 89854,
    "X": 7,
    "Y": 146,
    "Info": ""
  },
  {
    "PlanetId": 1031,
    "OwnerId": 127651,
    "X": 7,
    "Y": 143,
    "Info": ""
  },
  {
    "PlanetId": 1032,
    "OwnerId": 218944,
    "X": 7,
    "Y": 133,
    "Info": ""
  },
  {
    "PlanetId": 1033,
    "OwnerId": 204174,
    "X": 7,
    "Y": 133,
    "Info": ""
  },
  {
    "PlanetId": 1034,
    "OwnerId": 169232,
    "X": 7,
    "Y": 122,
    "Info": ""
  },
  {
    "PlanetId": 1035,
    "OwnerId": 114580,
    "X": 7,
    "Y": 122,
    "Info": ""
  },
  {
    "PlanetId": 1036,
    "OwnerId": 95349,
    "X": 7,
    "Y": 122,
    "Info": ""
  },
  {
    "PlanetId": 1037,
    "OwnerId": 81739,
    "X": 7,
    "Y": 122,
    "Info": ""
  },
  {
    "PlanetId": 1038,
    "OwnerId": 172320,
    "X": 7,
    "Y": 132,
    "Info": ""
  },
  {
    "PlanetId": 1039,
    "OwnerId": 89006,
    "X": 7,
    "Y": 132,
    "Info": ""
  },
  {
    "PlanetId": 1040,
    "OwnerId": 193169,
    "X": 7,
    "Y": 132,
    "Info": ""
  },
  {
    "PlanetId": 1041,
    "OwnerId": 198899,
    "X": 7,
    "Y": 132,
    "Info": ""
  },
  {
    "PlanetId": 1042,
    "OwnerId": 207750,
    "X": 7,
    "Y": 132,
    "Info": ""
  },
  {
    "PlanetId": 1043,
    "OwnerId": 74731,
    "X": 7,
    "Y": 132,
    "Info": ""
  },
  {
    "PlanetId": 1044,
    "OwnerId": 62670,
    "X": 7,
    "Y": 132,
    "Info": ""
  },
  {
    "PlanetId": 1045,
    "OwnerId": 131751,
    "X": 7,
    "Y": 132,
    "Info": ""
  },
  {
    "PlanetId": 1046,
    "OwnerId": 102116,
    "X": 7,
    "Y": 132,
    "Info": ""
  },
  {
    "PlanetId": 1047,
    "OwnerId": 66687,
    "X": 7,
    "Y": 136,
    "Info": ""
  },
  {
    "PlanetId": 1048,
    "OwnerId": 48840,
    "X": 7,
    "Y": 136,
    "Info": ""
  },
  {
    "PlanetId": 1049,
    "OwnerId": 37821,
    "X": 7,
    "Y": 136,
    "Info": ""
  },
  {
    "PlanetId": 1050,
    "OwnerId": 44935,
    "X": 7,
    "Y": 136,
    "Info": ""
  },
  {
    "PlanetId": 1051,
    "OwnerId": 117887,
    "X": 7,
    "Y": 136,
    "Info": ""
  },
  {
    "PlanetId": 1052,
    "OwnerId": 112943,
    "X": 7,
    "Y": 136,
    "Info": ""
  },
  {
    "PlanetId": 1053,
    "OwnerId": 73583,
    "X": 7,
    "Y": 136,
    "Info": ""
  },
  {
    "PlanetId": 1054,
    "OwnerId": 50189,
    "X": 7,
    "Y": 118,
    "Info": ""
  },
  {
    "PlanetId": 1055,
    "OwnerId": 54619,
    "X": 7,
    "Y": 118,
    "Info": ""
  },
  {
    "PlanetId": 1056,
    "OwnerId": 136845,
    "X": 7,
    "Y": 118,
    "Info": ""
  },
  {
    "PlanetId": 1057,
    "OwnerId": 153900,
    "X": 7,
    "Y": 118,
    "Info": ""
  },
  {
    "PlanetId": 1058,
    "OwnerId": 167944,
    "X": 7,
    "Y": 118,
    "Info": ""
  },
  {
    "PlanetId": 1059,
    "OwnerId": 46132,
    "X": 7,
    "Y": 114,
    "Info": ""
  },
  {
    "PlanetId": 1060,
    "OwnerId": 149437,
    "X": 7,
    "Y": 114,
    "Info": ""
  },
  {
    "PlanetId": 1061,
    "OwnerId": 167183,
    "X": 7,
    "Y": 114,
    "Info": ""
  },
  {
    "PlanetId": 1062,
    "OwnerId": 180422,
    "X": 7,
    "Y": 114,
    "Info": ""
  },
  {
    "PlanetId": 1063,
    "OwnerId": 180784,
    "X": 7,
    "Y": 114,
    "Info": ""
  },
  {
    "PlanetId": 1064,
    "OwnerId": 100844,
    "X": 7,
    "Y": 114,
    "Info": ""
  },
  {
    "PlanetId": 1065,
    "OwnerId": 145893,
    "X": 7,
    "Y": 0,
    "Info": ""
  },
  {
    "PlanetId": 1066,
    "OwnerId": 40115,
    "X": 7,
    "Y": 0,
    "Info": ""
  },
  {
    "PlanetId": 1067,
    "OwnerId": 188660,
    "X": 7,
    "Y": 0,
    "Info": ""
  },
  {
    "PlanetId": 1068,
    "OwnerId": 134218,
    "X": 7,
    "Y": 0,
    "Info": ""
  },
  {
    "PlanetId": 1069,
    "OwnerId": 215323,
    "X": 7,
    "Y": 0,
    "Info": ""
  },
  {
    "PlanetId": 1070,
    "OwnerId": 93791,
    "X": 7,
    "Y": 0,
    "Info": ""
  },
  {
    "PlanetId": 1071,
    "OwnerId": 138741,
    "X": 7,
    "Y": 0,
    "Info": ""
  },
  {
    "PlanetId": 1072,
    "OwnerId": 103475,
    "X": 7,
    "Y": 0,
    "Info": ""
  },
  {
    "PlanetId": 1073,
    "OwnerId": 81883,
    "X": 7,
    "Y": 0,
    "Info": ""
  },
  {
    "PlanetId": 1074,
    "OwnerId": 83326,
    "X": 7,
    "Y": 0,
    "Info": ""
  },
  {
    "PlanetId": 1075,
    "OwnerId": 153801,
    "X": 7,
    "Y": 0,
    "Info": ""
  },
  {
    "PlanetId": 1076,
    "OwnerId": 179722,
    "X": 6,
    "Y": 99,
    "Info": ""
  },
  {
    "PlanetId": 1077,
    "OwnerId": 176238,
    "X": 6,
    "Y": 99,
    "Info": ""
  },
  {
    "PlanetId": 1078,
    "OwnerId": 239250,
    "X": 6,
    "Y": 99,
    "Info": ""
  },
  {
    "PlanetId": 1079,
    "OwnerId": 61729,
    "X": 7,
    "Y": 131,
    "Info": ""
  },
  {
    "PlanetId": 1080,
    "OwnerId": 153130,
    "X": 7,
    "Y": 131,
    "Info": ""
  },
  {
    "PlanetId": 1081,
    "OwnerId": 189630,
    "X": 7,
    "Y": 131,
    "Info": ""
  },
  {
    "PlanetId": 1082,
    "OwnerId": 24092,
    "X": 7,
    "Y": 131,
    "Info": ""
  },
  {
    "PlanetId": 1083,
    "OwnerId": 204174,
    "X": 7,
    "Y": 131,
    "Info": ""
  },
  {
    "PlanetId": 1084,
    "OwnerId": 66839,
    "X": 6,
    "Y": 96,
    "Info": ""
  },
  {
    "PlanetId": 1085,
    "OwnerId": 53962,
    "X": 6,
    "Y": 84,
    "Info": ""
  },
  {
    "PlanetId": 1086,
    "OwnerId": 126126,
    "X": 6,
    "Y": 84,
    "Info": ""
  },
  {
    "PlanetId": 1087,
    "OwnerId": 144115,
    "X": 6,
    "Y": 84,
    "Info": ""
  },
  {
    "PlanetId": 1088,
    "OwnerId": 165520,
    "X": 6,
    "Y": 84,
    "Info": ""
  },
  {
    "PlanetId": 1089,
    "OwnerId": 172099,
    "X": 6,
    "Y": 84,
    "Info": ""
  },
  {
    "PlanetId": 1090,
    "OwnerId": 59301,
    "X": 6,
    "Y": 84,
    "Info": ""
  },
  {
    "PlanetId": 1091,
    "OwnerId": 151936,
    "X": 7,
    "Y": 174,
    "Info": ""
  },
  {
    "PlanetId": 1092,
    "OwnerId": 136255,
    "X": 7,
    "Y": 174,
    "Info": ""
  },
  {
    "PlanetId": 1093,
    "OwnerId": 95250,
    "X": 7,
    "Y": 174,
    "Info": ""
  },
  {
    "PlanetId": 1094,
    "OwnerId": 191021,
    "X": 7,
    "Y": 174,
    "Info": ""
  },
  {
    "PlanetId": 1095,
    "OwnerId": 172434,
    "X": 7,
    "Y": 174,
    "Info": ""
  },
  {
    "PlanetId": 1096,
    "OwnerId": 53573,
    "X": 6,
    "Y": 83,
    "Info": ""
  },
  {
    "PlanetId": 1097,
    "OwnerId": 270249,
    "X": 6,
    "Y": 83,
    "Info": ""
  },
  {
    "PlanetId": 1098,
    "OwnerId": 46321,
    "X": 6,
    "Y": 78,
    "Info": ""
  },
  {
    "PlanetId": 1099,
    "OwnerId": 141899,
    "X": 6,
    "Y": 78,
    "Info": ""
  },
  {
    "PlanetId": 1100,
    "OwnerId": 152358,
    "X": 6,
    "Y": 78,
    "Info": ""
  },
  {
    "PlanetId": 1101,
    "OwnerId": 159222,
    "X": 6,
    "Y": 78,
    "Info": ""
  },
  {
    "PlanetId": 1102,
    "OwnerId": 160619,
    "X": 6,
    "Y": 78,
    "Info": ""
  },
  {
    "PlanetId": 1103,
    "OwnerId": 41441,
    "X": 6,
    "Y": 78,
    "Info": ""
  },
  {
    "PlanetId": 1104,
    "OwnerId": 58016,
    "X": 6,
    "Y": 78,
    "Info": ""
  },
  {
    "PlanetId": 1105,
    "OwnerId": 125645,
    "X": 6,
    "Y": 79,
    "Info": ""
  },
  {
    "PlanetId": 1106,
    "OwnerId": 128586,
    "X": 6,
    "Y": 79,
    "Info": ""
  },
  {
    "PlanetId": 1107,
    "OwnerId": 86671,
    "X": 6,
    "Y": 79,
    "Info": ""
  },
  {
    "PlanetId": 1108,
    "OwnerId": 157309,
    "X": 6,
    "Y": 79,
    "Info": ""
  },
  {
    "PlanetId": 1109,
    "OwnerId": 198529,
    "X": 6,
    "Y": 79,
    "Info": ""
  },
  {
    "PlanetId": 1110,
    "OwnerId": 160619,
    "X": 6,
    "Y": 79,
    "Info": ""
  },
  {
    "PlanetId": 1111,
    "OwnerId": 46321,
    "X": 6,
    "Y": 79,
    "Info": ""
  },
  {
    "PlanetId": 1112,
    "OwnerId": 40247,
    "X": 6,
    "Y": 77,
    "Info": ""
  },
  {
    "PlanetId": 1113,
    "OwnerId": 118535,
    "X": 7,
    "Y": 178,
    "Info": ""
  },
  {
    "PlanetId": 1114,
    "OwnerId": 134832,
    "X": 7,
    "Y": 178,
    "Info": ""
  },
  {
    "PlanetId": 1115,
    "OwnerId": 268430,
    "X": 7,
    "Y": 178,
    "Info": ""
  },
  {
    "PlanetId": 1116,
    "OwnerId": 138843,
    "X": 7,
    "Y": 178,
    "Info": ""
  },
  {
    "PlanetId": 1117,
    "OwnerId": 141776,
    "X": 7,
    "Y": 178,
    "Info": ""
  },
  {
    "PlanetId": 1118,
    "OwnerId": 138312,
    "X": 6,
    "Y": 80,
    "Info": ""
  },
  {
    "PlanetId": 1119,
    "OwnerId": 59340,
    "X": 6,
    "Y": 65,
    "Info": ""
  },
  {
    "PlanetId": 1120,
    "OwnerId": 105943,
    "X": 6,
    "Y": 65,
    "Info": ""
  },
  {
    "PlanetId": 1121,
    "OwnerId": 138314,
    "X": 6,
    "Y": 65,
    "Info": ""
  },
  {
    "PlanetId": 1122,
    "OwnerId": 146611,
    "X": 6,
    "Y": 65,
    "Info": ""
  },
  {
    "PlanetId": 1123,
    "OwnerId": 93440,
    "X": 6,
    "Y": 65,
    "Info": ""
  },
  {
    "PlanetId": 1124,
    "OwnerId": 185405,
    "X": 6,
    "Y": 65,
    "Info": ""
  },
  {
    "PlanetId": 1125,
    "OwnerId": 145210,
    "X": 6,
    "Y": 59,
    "Info": ""
  },
  {
    "PlanetId": 1126,
    "OwnerId": 71605,
    "X": 6,
    "Y": 59,
    "Info": ""
  },
  {
    "PlanetId": 1127,
    "OwnerId": 146914,
    "X": 6,
    "Y": 59,
    "Info": ""
  },
  {
    "PlanetId": 1128,
    "OwnerId": 157609,
    "X": 6,
    "Y": 59,
    "Info": ""
  },
  {
    "PlanetId": 1129,
    "OwnerId": 173322,
    "X": 6,
    "Y": 59,
    "Info": ""
  },
  {
    "PlanetId": 1130,
    "OwnerId": 229699,
    "X": 6,
    "Y": 61,
    "Info": ""
  },
  {
    "PlanetId": 1131,
    "OwnerId": 240168,
    "X": 6,
    "Y": 57,
    "Info": ""
  },
  {
    "PlanetId": 1132,
    "OwnerId": 178264,
    "X": 6,
    "Y": 50,
    "Info": ""
  },
  {
    "PlanetId": 1133,
    "OwnerId": 75445,
    "X": 6,
    "Y": 50,
    "Info": ""
  },
  {
    "PlanetId": 1134,
    "OwnerId": 214944,
    "X": 6,
    "Y": 50,
    "Info": ""
  },
  {
    "PlanetId": 1135,
    "OwnerId": 126375,
    "X": 6,
    "Y": 50,
    "Info": ""
  },
  {
    "PlanetId": 1136,
    "OwnerId": 51722,
    "X": 6,
    "Y": 50,
    "Info": ""
  },
  {
    "PlanetId": 1137,
    "OwnerId": 224794,
    "X": 6,
    "Y": 45,
    "Info": ""
  },
  {
    "PlanetId": 1138,
    "OwnerId": 55795,
    "X": 6,
    "Y": 45,
    "Info": ""
  },
  {
    "PlanetId": 1139,
    "OwnerId": 235428,
    "X": 6,
    "Y": 45,
    "Info": ""
  },
  {
    "PlanetId": 1140,
    "OwnerId": 110193,
    "X": 6,
    "Y": 48,
    "Info": ""
  },
  {
    "PlanetId": 1141,
    "OwnerId": 116533,
    "X": 6,
    "Y": 48,
    "Info": ""
  },
  {
    "PlanetId": 1142,
    "OwnerId": 51765,
    "X": 6,
    "Y": 48,
    "Info": ""
  },
  {
    "PlanetId": 1143,
    "OwnerId": 185098,
    "X": 6,
    "Y": 48,
    "Info": ""
  },
  {
    "PlanetId": 1144,
    "OwnerId": 71021,
    "X": 6,
    "Y": 48,
    "Info": ""
  },
  {
    "PlanetId": 1145,
    "OwnerId": 77908,
    "X": 6,
    "Y": 48,
    "Info": ""
  },
  {
    "PlanetId": 1146,
    "OwnerId": 136976,
    "X": 6,
    "Y": 48,
    "Info": ""
  },
  {
    "PlanetId": 1147,
    "OwnerId": 194718,
    "X": 6,
    "Y": 36,
    "Info": ""
  },
  {
    "PlanetId": 1148,
    "OwnerId": 187453,
    "X": 6,
    "Y": 36,
    "Info": ""
  },
  {
    "PlanetId": 1149,
    "OwnerId": 55562,
    "X": 6,
    "Y": 64,
    "Info": ""
  },
  {
    "PlanetId": 1150,
    "OwnerId": 66973,
    "X": 6,
    "Y": 64,
    "Info": ""
  },
  {
    "PlanetId": 1151,
    "OwnerId": 114539,
    "X": 6,
    "Y": 64,
    "Info": ""
  },
  {
    "PlanetId": 1152,
    "OwnerId": 189361,
    "X": 6,
    "Y": 64,
    "Info": ""
  },
  {
    "PlanetId": 1153,
    "OwnerId": 101333,
    "X": 6,
    "Y": 33,
    "Info": ""
  },
  {
    "PlanetId": 1154,
    "OwnerId": 264325,
    "X": 6,
    "Y": 33,
    "Info": ""
  },
  {
    "PlanetId": 1155,
    "OwnerId": 93175,
    "X": 6,
    "Y": 33,
    "Info": ""
  },
  {
    "PlanetId": 1156,
    "OwnerId": 87238,
    "X": 6,
    "Y": 32,
    "Info": ""
  },
  {
    "PlanetId": 1157,
    "OwnerId": 132247,
    "X": 6,
    "Y": 32,
    "Info": ""
  },
  {
    "PlanetId": 1158,
    "OwnerId": 146601,
    "X": 6,
    "Y": 32,
    "Info": ""
  },
  {
    "PlanetId": 1159,
    "OwnerId": 192159,
    "X": 6,
    "Y": 32,
    "Info": ""
  },
  {
    "PlanetId": 1160,
    "OwnerId": 76997,
    "X": 6,
    "Y": 32,
    "Info": ""
  },
  {
    "PlanetId": 1161,
    "OwnerId": 103110,
    "X": 6,
    "Y": 3,
    "Info": ""
  },
  {
    "PlanetId": 1162,
    "OwnerId": 140127,
    "X": 6,
    "Y": 3,
    "Info": ""
  },
  {
    "PlanetId": 1163,
    "OwnerId": 176150,
    "X": 6,
    "Y": 3,
    "Info": ""
  },
  {
    "PlanetId": 1164,
    "OwnerId": 60356,
    "X": 6,
    "Y": 3,
    "Info": ""
  },
  {
    "PlanetId": 1165,
    "OwnerId": 245386,
    "X": 6,
    "Y": 3,
    "Info": ""
  },
  {
    "PlanetId": 1166,
    "OwnerId": 230241,
    "X": 6,
    "Y": 3,
    "Info": ""
  },
  {
    "PlanetId": 1167,
    "OwnerId": 227203,
    "X": 6,
    "Y": 3,
    "Info": ""
  },
  {
    "PlanetId": 1168,
    "OwnerId": 246035,
    "X": 6,
    "Y": 3,
    "Info": ""
  },
  {
    "PlanetId": 1169,
    "OwnerId": 80010,
    "X": 6,
    "Y": 3,
    "Info": ""
  },
  {
    "PlanetId": 1170,
    "OwnerId": 41465,
    "X": 6,
    "Y": 3,
    "Info": ""
  },
  {
    "PlanetId": 1171,
    "OwnerId": 224758,
    "X": 6,
    "Y": 3,
    "Info": ""
  },
  {
    "PlanetId": 1172,
    "OwnerId": 101066,
    "X": 6,
    "Y": 3,
    "Info": ""
  },
  {
    "PlanetId": 1173,
    "OwnerId": 62208,
    "X": 6,
    "Y": 29,
    "Info": ""
  },
  {
    "PlanetId": 1174,
    "OwnerId": 74059,
    "X": 6,
    "Y": 29,
    "Info": ""
  },
  {
    "PlanetId": 1175,
    "OwnerId": 141910,
    "X": 6,
    "Y": 29,
    "Info": ""
  },
  {
    "PlanetId": 1176,
    "OwnerId": 142492,
    "X": 6,
    "Y": 29,
    "Info": ""
  },
  {
    "PlanetId": 1177,
    "OwnerId": 143321,
    "X": 6,
    "Y": 29,
    "Info": ""
  },
  {
    "PlanetId": 1178,
    "OwnerId": 143007,
    "X": 6,
    "Y": 29,
    "Info": ""
  },
  {
    "PlanetId": 1179,
    "OwnerId": 135161,
    "X": 6,
    "Y": 26,
    "Info": ""
  },
  {
    "PlanetId": 1180,
    "OwnerId": 184328,
    "X": 6,
    "Y": 26,
    "Info": ""
  },
  {
    "PlanetId": 1181,
    "OwnerId": 191390,
    "X": 6,
    "Y": 26,
    "Info": ""
  },
  {
    "PlanetId": 1182,
    "OwnerId": 209532,
    "X": 6,
    "Y": 26,
    "Info": ""
  },
  {
    "PlanetId": 1183,
    "OwnerId": 54784,
    "X": 6,
    "Y": 200,
    "Info": ""
  },
  {
    "PlanetId": 1184,
    "OwnerId": 93199,
    "X": 6,
    "Y": 200,
    "Info": ""
  },
  {
    "PlanetId": 1185,
    "OwnerId": 44044,
    "X": 6,
    "Y": 200,
    "Info": ""
  },
  {
    "PlanetId": 1186,
    "OwnerId": 207545,
    "X": 6,
    "Y": 200,
    "Info": ""
  },
  {
    "PlanetId": 1187,
    "OwnerId": 211872,
    "X": 6,
    "Y": 200,
    "Info": ""
  },
  {
    "PlanetId": 1188,
    "OwnerId": 175651,
    "X": 6,
    "Y": 200,
    "Info": ""
  },
  {
    "PlanetId": 1189,
    "OwnerId": 40303,
    "X": 6,
    "Y": 200,
    "Info": ""
  },
  {
    "PlanetId": 1190,
    "OwnerId": 66027,
    "X": 6,
    "Y": 2,
    "Info": ""
  },
  {
    "PlanetId": 1191,
    "OwnerId": 115522,
    "X": 6,
    "Y": 2,
    "Info": ""
  },
  {
    "PlanetId": 1192,
    "OwnerId": 40452,
    "X": 6,
    "Y": 2,
    "Info": ""
  },
  {
    "PlanetId": 1193,
    "OwnerId": 99527,
    "X": 6,
    "Y": 2,
    "Info": ""
  },
  {
    "PlanetId": 1194,
    "OwnerId": 52762,
    "X": 6,
    "Y": 2,
    "Info": ""
  },
  {
    "PlanetId": 1195,
    "OwnerId": 42523,
    "X": 6,
    "Y": 2,
    "Info": ""
  },
  {
    "PlanetId": 1196,
    "OwnerId": 153669,
    "X": 6,
    "Y": 2,
    "Info": ""
  },
  {
    "PlanetId": 1197,
    "OwnerId": 103288,
    "X": 6,
    "Y": 2,
    "Info": ""
  },
  {
    "PlanetId": 1198,
    "OwnerId": 98323,
    "X": 6,
    "Y": 2,
    "Info": ""
  },
  {
    "PlanetId": 1199,
    "OwnerId": 171486,
    "X": 6,
    "Y": 2,
    "Info": ""
  },
  {
    "PlanetId": 1200,
    "OwnerId": 75499,
    "X": 6,
    "Y": 2,
    "Info": ""
  },
  {
    "PlanetId": 1201,
    "OwnerId": 43951,
    "X": 6,
    "Y": 2,
    "Info": ""
  },
  {
    "PlanetId": 1202,
    "OwnerId": 186936,
    "X": 6,
    "Y": 199,
    "Info": ""
  },
  {
    "PlanetId": 1203,
    "OwnerId": 175871,
    "X": 6,
    "Y": 192,
    "Info": ""
  },
  {
    "PlanetId": 1204,
    "OwnerId": 150401,
    "X": 6,
    "Y": 184,
    "Info": ""
  },
  {
    "PlanetId": 1205,
    "OwnerId": 222592,
    "X": 6,
    "Y": 186,
    "Info": ""
  },
  {
    "PlanetId": 1206,
    "OwnerId": 153910,
    "X": 6,
    "Y": 181,
    "Info": ""
  },
  {
    "PlanetId": 1207,
    "OwnerId": 219225,
    "X": 6,
    "Y": 179,
    "Info": ""
  },
  {
    "PlanetId": 1208,
    "OwnerId": 224960,
    "X": 6,
    "Y": 179,
    "Info": ""
  },
  {
    "PlanetId": 1209,
    "OwnerId": 150401,
    "X": 6,
    "Y": 179,
    "Info": ""
  },
  {
    "PlanetId": 1210,
    "OwnerId": 141776,
    "X": 6,
    "Y": 174,
    "Info": ""
  },
  {
    "PlanetId": 1211,
    "OwnerId": 171533,
    "X": 6,
    "Y": 174,
    "Info": ""
  },
  {
    "PlanetId": 1212,
    "OwnerId": 174138,
    "X": 6,
    "Y": 174,
    "Info": ""
  },
  {
    "PlanetId": 1213,
    "OwnerId": 176440,
    "X": 6,
    "Y": 174,
    "Info": ""
  },
  {
    "PlanetId": 1214,
    "OwnerId": 178769,
    "X": 6,
    "Y": 174,
    "Info": ""
  },
  {
    "PlanetId": 1215,
    "OwnerId": 112378,
    "X": 6,
    "Y": 174,
    "Info": ""
  },
  {
    "PlanetId": 1216,
    "OwnerId": 186171,
    "X": 6,
    "Y": 172,
    "Info": ""
  },
  {
    "PlanetId": 1217,
    "OwnerId": 190491,
    "X": 6,
    "Y": 172,
    "Info": ""
  },
  {
    "PlanetId": 1218,
    "OwnerId": 200157,
    "X": 6,
    "Y": 172,
    "Info": ""
  },
  {
    "PlanetId": 1219,
    "OwnerId": 201861,
    "X": 6,
    "Y": 172,
    "Info": ""
  },
  {
    "PlanetId": 1220,
    "OwnerId": 214676,
    "X": 6,
    "Y": 172,
    "Info": ""
  },
  {
    "PlanetId": 1221,
    "OwnerId": 129201,
    "X": 6,
    "Y": 172,
    "Info": ""
  },
  {
    "PlanetId": 1222,
    "OwnerId": 41117,
    "X": 6,
    "Y": 170,
    "Info": ""
  },
  {
    "PlanetId": 1223,
    "OwnerId": 62906,
    "X": 6,
    "Y": 16,
    "Info": ""
  },
  {
    "PlanetId": 1224,
    "OwnerId": 127241,
    "X": 6,
    "Y": 16,
    "Info": ""
  },
  {
    "PlanetId": 1225,
    "OwnerId": 245127,
    "X": 6,
    "Y": 16,
    "Info": ""
  },
  {
    "PlanetId": 1226,
    "OwnerId": 206806,
    "X": 6,
    "Y": 16,
    "Info": ""
  },
  {
    "PlanetId": 1227,
    "OwnerId": 41465,
    "X": 6,
    "Y": 16,
    "Info": ""
  },
  {
    "PlanetId": 1228,
    "OwnerId": 242384,
    "X": 6,
    "Y": 16,
    "Info": ""
  },
  {
    "PlanetId": 1229,
    "OwnerId": 145977,
    "X": 6,
    "Y": 156,
    "Info": ""
  },
  {
    "PlanetId": 1230,
    "OwnerId": 60139,
    "X": 6,
    "Y": 154,
    "Info": ""
  },
  {
    "PlanetId": 1231,
    "OwnerId": 119831,
    "X": 6,
    "Y": 154,
    "Info": ""
  },
  {
    "PlanetId": 1232,
    "OwnerId": 148718,
    "X": 6,
    "Y": 154,
    "Info": ""
  },
  {
    "PlanetId": 1233,
    "OwnerId": 183849,
    "X": 6,
    "Y": 154,
    "Info": ""
  },
  {
    "PlanetId": 1234,
    "OwnerId": 193371,
    "X": 6,
    "Y": 154,
    "Info": ""
  },
  {
    "PlanetId": 1235,
    "OwnerId": 115455,
    "X": 6,
    "Y": 154,
    "Info": ""
  },
  {
    "PlanetId": 1236,
    "OwnerId": 176800,
    "X": 6,
    "Y": 154,
    "Info": ""
  },
  {
    "PlanetId": 1237,
    "OwnerId": 256016,
    "X": 6,
    "Y": 152,
    "Info": ""
  },
  {
    "PlanetId": 1238,
    "OwnerId": 51808,
    "X": 6,
    "Y": 137,
    "Info": ""
  },
  {
    "PlanetId": 1239,
    "OwnerId": 111930,
    "X": 6,
    "Y": 137,
    "Info": ""
  },
  {
    "PlanetId": 1240,
    "OwnerId": 122347,
    "X": 6,
    "Y": 137,
    "Info": ""
  },
  {
    "PlanetId": 1241,
    "OwnerId": 180328,
    "X": 6,
    "Y": 137,
    "Info": ""
  },
  {
    "PlanetId": 1242,
    "OwnerId": 209477,
    "X": 6,
    "Y": 137,
    "Info": ""
  },
  {
    "PlanetId": 1243,
    "OwnerId": 111425,
    "X": 6,
    "Y": 137,
    "Info": ""
  },
  {
    "PlanetId": 1244,
    "OwnerId": 153784,
    "X": 6,
    "Y": 14,
    "Info": ""
  },
  {
    "PlanetId": 1245,
    "OwnerId": 172412,
    "X": 6,
    "Y": 14,
    "Info": ""
  },
  {
    "PlanetId": 1246,
    "OwnerId": 46343,
    "X": 6,
    "Y": 14,
    "Info": ""
  },
  {
    "PlanetId": 1247,
    "OwnerId": 206806,
    "X": 6,
    "Y": 14,
    "Info": ""
  },
  {
    "PlanetId": 1248,
    "OwnerId": 148181,
    "X": 6,
    "Y": 14,
    "Info": ""
  },
  {
    "PlanetId": 1249,
    "OwnerId": 193671,
    "X": 6,
    "Y": 14,
    "Info": ""
  },
  {
    "PlanetId": 1250,
    "OwnerId": 194387,
    "X": 6,
    "Y": 14,
    "Info": ""
  },
  {
    "PlanetId": 1251,
    "OwnerId": 244099,
    "X": 6,
    "Y": 14,
    "Info": ""
  },
  {
    "PlanetId": 1252,
    "OwnerId": 93880,
    "X": 6,
    "Y": 14,
    "Info": ""
  },
  {
    "PlanetId": 1253,
    "OwnerId": 167290,
    "X": 6,
    "Y": 14,
    "Info": ""
  },
  {
    "PlanetId": 1254,
    "OwnerId": 120323,
    "X": 6,
    "Y": 14,
    "Info": ""
  },
  {
    "PlanetId": 1255,
    "OwnerId": 248607,
    "X": 6,
    "Y": 14,
    "Info": ""
  },
  {
    "PlanetId": 1256,
    "OwnerId": 44039,
    "X": 6,
    "Y": 128,
    "Info": ""
  },
  {
    "PlanetId": 1257,
    "OwnerId": 154910,
    "X": 6,
    "Y": 128,
    "Info": ""
  },
  {
    "PlanetId": 1258,
    "OwnerId": 204079,
    "X": 6,
    "Y": 128,
    "Info": ""
  },
  {
    "PlanetId": 1259,
    "OwnerId": 86368,
    "X": 6,
    "Y": 128,
    "Info": ""
  },
  {
    "PlanetId": 1260,
    "OwnerId": 24092,
    "X": 6,
    "Y": 128,
    "Info": ""
  },
  {
    "PlanetId": 1261,
    "OwnerId": 47353,
    "X": 6,
    "Y": 113,
    "Info": ""
  },
  {
    "PlanetId": 1262,
    "OwnerId": 58539,
    "X": 6,
    "Y": 113,
    "Info": ""
  },
  {
    "PlanetId": 1263,
    "OwnerId": 46132,
    "X": 6,
    "Y": 113,
    "Info": ""
  },
  {
    "PlanetId": 1264,
    "OwnerId": 172475,
    "X": 6,
    "Y": 113,
    "Info": ""
  },
  {
    "PlanetId": 1265,
    "OwnerId": 100844,
    "X": 6,
    "Y": 113,
    "Info": ""
  },
  {
    "PlanetId": 1266,
    "OwnerId": 72223,
    "X": 6,
    "Y": 113,
    "Info": ""
  },
  {
    "PlanetId": 1267,
    "OwnerId": 59705,
    "X": 6,
    "Y": 126,
    "Info": ""
  },
  {
    "PlanetId": 1268,
    "OwnerId": 208512,
    "X": 6,
    "Y": 126,
    "Info": ""
  },
  {
    "PlanetId": 1269,
    "OwnerId": 175705,
    "X": 6,
    "Y": 126,
    "Info": ""
  },
  {
    "PlanetId": 1270,
    "OwnerId": 48952,
    "X": 6,
    "Y": 43,
    "Info": ""
  },
  {
    "PlanetId": 1271,
    "OwnerId": 105764,
    "X": 6,
    "Y": 43,
    "Info": ""
  },
  {
    "PlanetId": 1272,
    "OwnerId": 58612,
    "X": 6,
    "Y": 43,
    "Info": ""
  },
  {
    "PlanetId": 1273,
    "OwnerId": 55116,
    "X": 6,
    "Y": 43,
    "Info": ""
  },
  {
    "PlanetId": 1274,
    "OwnerId": 143684,
    "X": 6,
    "Y": 43,
    "Info": ""
  },
  {
    "PlanetId": 1275,
    "OwnerId": 199215,
    "X": 6,
    "Y": 43,
    "Info": ""
  },
  {
    "PlanetId": 1276,
    "OwnerId": 96835,
    "X": 6,
    "Y": 105,
    "Info": ""
  },
  {
    "PlanetId": 1277,
    "OwnerId": 156883,
    "X": 6,
    "Y": 105,
    "Info": ""
  },
  {
    "PlanetId": 1278,
    "OwnerId": 174000,
    "X": 6,
    "Y": 105,
    "Info": ""
  },
  {
    "PlanetId": 1279,
    "OwnerId": 137058,
    "X": 6,
    "Y": 105,
    "Info": ""
  },
  {
    "PlanetId": 1280,
    "OwnerId": 129080,
    "X": 6,
    "Y": 105,
    "Info": ""
  },
  {
    "PlanetId": 1281,
    "OwnerId": 56762,
    "X": 6,
    "Y": 105,
    "Info": ""
  },
  {
    "PlanetId": 1282,
    "OwnerId": 123826,
    "X": 6,
    "Y": 105,
    "Info": ""
  },
  {
    "PlanetId": 1283,
    "OwnerId": 137432,
    "X": 6,
    "Y": 103,
    "Info": ""
  },
  {
    "PlanetId": 1284,
    "OwnerId": 155861,
    "X": 6,
    "Y": 103,
    "Info": ""
  },
  {
    "PlanetId": 1285,
    "OwnerId": 170324,
    "X": 6,
    "Y": 103,
    "Info": ""
  },
  {
    "PlanetId": 1286,
    "OwnerId": 185167,
    "X": 6,
    "Y": 103,
    "Info": ""
  },
  {
    "PlanetId": 1287,
    "OwnerId": 192911,
    "X": 6,
    "Y": 103,
    "Info": ""
  },
  {
    "PlanetId": 1288,
    "OwnerId": 52181,
    "X": 6,
    "Y": 103,
    "Info": ""
  },
  {
    "PlanetId": 1289,
    "OwnerId": 129080,
    "X": 6,
    "Y": 103,
    "Info": ""
  },
  {
    "PlanetId": 1290,
    "OwnerId": 42667,
    "X": 6,
    "Y": 103,
    "Info": ""
  },
  {
    "PlanetId": 1291,
    "OwnerId": 105680,
    "X": 6,
    "Y": 101,
    "Info": ""
  },
  {
    "PlanetId": 1292,
    "OwnerId": 103475,
    "X": 6,
    "Y": 101,
    "Info": ""
  },
  {
    "PlanetId": 1293,
    "OwnerId": 44726,
    "X": 6,
    "Y": 0,
    "Info": ""
  },
  {
    "PlanetId": 1294,
    "OwnerId": 205524,
    "X": 6,
    "Y": 0,
    "Info": ""
  },
  {
    "PlanetId": 1295,
    "OwnerId": 144992,
    "X": 6,
    "Y": 0,
    "Info": ""
  },
  {
    "PlanetId": 1296,
    "OwnerId": 46030,
    "X": 6,
    "Y": 0,
    "Info": ""
  },
  {
    "PlanetId": 1297,
    "OwnerId": 255462,
    "X": 6,
    "Y": 0,
    "Info": ""
  },
  {
    "PlanetId": 1298,
    "OwnerId": 242637,
    "X": 6,
    "Y": 0,
    "Info": ""
  },
  {
    "PlanetId": 1299,
    "OwnerId": 44106,
    "X": 6,
    "Y": 0,
    "Info": ""
  },
  {
    "PlanetId": 1300,
    "OwnerId": 43176,
    "X": 6,
    "Y": 0,
    "Info": ""
  },
  {
    "PlanetId": 1301,
    "OwnerId": 252966,
    "X": 6,
    "Y": 0,
    "Info": ""
  },
  {
    "PlanetId": 1302,
    "OwnerId": 186253,
    "X": 6,
    "Y": 0,
    "Info": ""
  },
  {
    "PlanetId": 1303,
    "OwnerId": 245080,
    "X": 6,
    "Y": 0,
    "Info": ""
  },
  {
    "PlanetId": 1304,
    "OwnerId": 42522,
    "X": 6,
    "Y": 0,
    "Info": ""
  },
  {
    "PlanetId": 1305,
    "OwnerId": 78050,
    "X": 5,
    "Y": 94,
    "Info": ""
  },
  {
    "PlanetId": 1306,
    "OwnerId": 99828,
    "X": 5,
    "Y": 94,
    "Info": ""
  },
  {
    "PlanetId": 1307,
    "OwnerId": 82818,
    "X": 5,
    "Y": 94,
    "Info": ""
  },
  {
    "PlanetId": 1308,
    "OwnerId": 90392,
    "X": 5,
    "Y": 94,
    "Info": ""
  },
  {
    "PlanetId": 1309,
    "OwnerId": 155376,
    "X": 5,
    "Y": 94,
    "Info": ""
  },
  {
    "PlanetId": 1310,
    "OwnerId": 135695,
    "X": 5,
    "Y": 94,
    "Info": ""
  },
  {
    "PlanetId": 1311,
    "OwnerId": 53903,
    "X": 5,
    "Y": 94,
    "Info": ""
  },
  {
    "PlanetId": 1312,
    "OwnerId": 231858,
    "X": 6,
    "Y": 108,
    "Info": ""
  },
  {
    "PlanetId": 1313,
    "OwnerId": 80784,
    "X": 5,
    "Y": 83,
    "Info": ""
  },
  {
    "PlanetId": 1314,
    "OwnerId": 92557,
    "X": 5,
    "Y": 83,
    "Info": ""
  },
  {
    "PlanetId": 1315,
    "OwnerId": 154851,
    "X": 5,
    "Y": 83,
    "Info": ""
  },
  {
    "PlanetId": 1316,
    "OwnerId": 113525,
    "X": 5,
    "Y": 83,
    "Info": ""
  },
  {
    "PlanetId": 1317,
    "OwnerId": 176247,
    "X": 5,
    "Y": 83,
    "Info": ""
  },
  {
    "PlanetId": 1318,
    "OwnerId": 118321,
    "X": 5,
    "Y": 83,
    "Info": ""
  },
  {
    "PlanetId": 1319,
    "OwnerId": 92821,
    "X": 5,
    "Y": 86,
    "Info": ""
  },
  {
    "PlanetId": 1320,
    "OwnerId": 97710,
    "X": 5,
    "Y": 86,
    "Info": ""
  },
  {
    "PlanetId": 1321,
    "OwnerId": 134209,
    "X": 5,
    "Y": 86,
    "Info": ""
  },
  {
    "PlanetId": 1322,
    "OwnerId": 135695,
    "X": 5,
    "Y": 86,
    "Info": ""
  },
  {
    "PlanetId": 1323,
    "OwnerId": 165700,
    "X": 5,
    "Y": 86,
    "Info": ""
  },
  {
    "PlanetId": 1324,
    "OwnerId": 43637,
    "X": 5,
    "Y": 86,
    "Info": ""
  }
]
def recover_colonies(alliance_name):
  allianceDetails = requests.get(f'https://api.galaxylifegame.net/Alliances/get?name={alliance_name}', timeout=2.50)
  parsed_allianceDetails = json.loads(allianceDetails.content)
  allianceSize =  len(parsed_allianceDetails['Members'])

  for it_alliance in range(allianceSize):
    playerName = parsed_allianceDetails['Members'][it_alliance]['Name']
    playerId = parsed_allianceDetails['Members'][it_alliance]['Id']
    for it in range(len(colo_db)):
      if int(colo_db[it]["OwnerId"]) == int(playerId):
        #print(f"trouvé pour {playerName}: X: {colo_db[it]['X']}, Y: {colo_db[it]['Y']}")
        print(f"🪐 **__(SB x):__**\n/colo_update pseudo:{playerName} colo_number:  colo_sys_name:  colo_coord_x:{colo_db[it]['X']} colo_coord_y:{colo_db[it]['Y']}\n")
    
recover_colonies("galactic swamp")    
  
# for s in colo_db:
# 	remove_key = s.pop("Info", None)
# for s in colo_db:
# 	remove_key = s.pop("PlanetId", None)
# for s in colo_db:
# 	remove_key = s.pop("OwnerId", "gl_id")
# print(colo_db)



# intégration de la db:
# - check ig_gl pour voir si trouvé dans db
#
#
#
#