import discord
import pymongo
import os
from pymongo import MongoClient


owner_id = 885193210455011369
owner_tag = "hunter#6967"
support_server = "https://discord.gg/vMnhpAyFZm"
prefix = "&"
maindb = MongoClient(os.environ["mongo_url"])
seconddb = MongoClient(os.environ["db_url"])
version = "1.8.7"
