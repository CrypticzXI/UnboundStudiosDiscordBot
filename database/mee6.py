from pymongo import MongoClient
from utilities.config import my_secret

cluster = MongoClient(
    f"mongodb+srv://user:{str(my_secret)}@cluster0.xjask.mongodb.net/myFirstDatabase?retryWrites=true&w=majority"
)
db = cluster["parrot_db"]
collection = db['mee6_role']


async def guild_join(guild_id: int):
    try:
        collection.insert_one({'_id': guild_id})
    except Exception as e:
        return str(e)


async def insert_lvl_role(guild_id: int, level: int, role_id: int):
    try:
        collection.insert_one({'_id': guild_id, level: role_id})
    except Exception as e:
        return str(e)


# async def remove_lvl_role(guild_id: int, level: int):
#     try:
#         collection.delete_one({'_id': guild_id, level: {'$regex': '\d+'}})
#     except Exception as e:
#         return str(e)

async def update_lvl_role(guild_id: int, level: int, role_id: int):
    post = {'_id': guild_id}
    try:
        collection.update(post, {level: role_id})
    except Exception as e:
        return str(e)


async def guild_remove(guild_id: int):
    try:
        collection.delete_one({'_id': guild_id})
    except Exception as e:
        return str(e)
