# imports
from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from lightdb import LightDB
import logging
from pyrogram import Client
import configparser

db = LightDB("db.json")
notes_db = LightDB("notes.json")
ofcrs = []
notes = []
# static variables
logging.basicConfig(level=logging.INFO)
config = configparser.ConfigParser()
config.read("config.ini")
token = config['tg']['token']
api_id = int(config['tg']['api_id'])
api_hash = config['tg']['api_hash']

# bot_data
bot = Bot(token=token, parse_mode="html")
dp = Dispatcher(bot, storage=MemoryStorage())
app = Client(
    "bot",
    bot_token = token,
    api_id = api_id,
    api_hash = api_hash
)