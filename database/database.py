import pymongo, os
from config import DB_URL, DB_NAME

dbclient = pymongo.MongoClient(DB_URL)
database = dbclient[DB_NAME]

user_data = database['users']
api_data = database['apis']
site_data = database['sites']
fsub = database['fsub_channel']

async def present_user(user_id : int):
    found = user_data.find_one({'_id': user_id})
    return bool(found)

async def add_user(user_id: int):
    user_data.insert_one({'_id': user_id})
    return

async def full_userbase():
    user_docs = user_data.find()
    user_ids = []
    for doc in user_docs:
        user_ids.append(doc['_id'])
        
    return user_ids

async def del_user(user_id: int):
    user_data.delete_one({'_id': user_id})
    return

async def get_user_data(user_id: int):
    user_info = user_data.find_one({'_id': user_id})
    return user_info

async def set_fsub_channel_id(channel_id: str):
    await fsub.update_one(
        {'_id': 'sub_channel'},
        {'$set': {'channel_id': channel_id}},
        upsert=True
    )

async def get_fsub_channel_id():
    config = await fsub.find_one({'_id': 'sub_channel'})
    if config:
        return config.get('channel_id', "")
    return ""
