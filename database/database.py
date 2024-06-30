import pymongo, os
from config import DB_URL, DB_NAME, ADMINS

dbclient = pymongo.MongoClient(DB_URL)
database = dbclient[DB_NAME]

user_data = database['users']
fsub = database['fsub_channel']
admin_data = database['admins']

async def present_user(user_id: int):
    found = user_data.find_one({'_id': user_id})
    return bool(found)

async def add_user(user_id: int):
    user_data.insert_one({'_id': user_id})
    return

async def full_userbase():
    user_docs = user_data.find()
    user_ids = [doc['_id'] for doc in list(user_docs)]
    return user_ids

async def del_user(user_id: int):
    user_data.delete_one({'_id': user_id})
    return

async def get_user_data(user_id: int):
    user_info = user_data.find_one({'_id': user_id})
    return user_info

# fsub

async def set_fsub_channel_id(channel_id: str):
    fsub.update_one(
        {'_id': 'sub_channel'},
        {'$set': {'channel_id': channel_id}},
        upsert=True
    )

async def get_fsub_channel_id():
    config = fsub.find_one({'_id': 'sub_channel'})
    if config:
        return config.get('channel_id', "")
    return ""

async def set_fsub_status(status: bool):
    fsub.update_one(
        {'_id': 'fsub_status'},
        {'$set': {'status': status}},
        upsert=True
    )

async def get_fsub_status():
    config = fsub.find_one({'_id': 'fsub_status'})
    if config:
        return config.get('status', False)
    return False

# admins

async def present_admin(user_id: int):
    found = await admin_data.find_one({'_id': user_id})
    return bool(found)

async def add_admin(user_id: int):
    user = {'_id': user_id}
    await admin_data.insert_one(user)
    ADMINS.append(int(user_id))
    return

async def del_admin(user_id: int):
    await admin_data.delete_one({'_id': user_id})
    ADMINS.remove(int(user_id))
    return

async def full_adminbase():
    user_docs = admin_data.find()
    user_ids = [int(doc['_id']) for doc in list(user_docs)]
    return user_ids
