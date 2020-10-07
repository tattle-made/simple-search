import os
import re
from dotenv import load_dotenv
load_dotenv()
import pymongo
from pymongo import MongoClient
import datetime
from datetime import datetime, timedelta
from bson.objectid import ObjectId
import json
import requests
import random
import mimetypes
from helper_sharechat import get_data, index_media
import logging
import re

try:
    mongo_url = "mongodb+srv://"+os.environ.get("SHARECHAT_DB_USERNAME")+":"+os.environ.get("SHARECHAT_DB_PASSWORD")+"@tattle-data-fkpmg.mongodb.net/test?retryWrites=true&w=majority&ssl=true&ssl_cert_reqs=CERT_NONE"   
    cli = MongoClient(mongo_url)
    db = cli[os.environ.get("SHARECHAT_DB_NAME")]
    coll = db[os.environ.get("SHARECHAT_DB_COLLECTION")]
except Exception as e:
    print('Error Connecting to Mongo ', e)

def IndexerSharechat():
    c=0
    end = datetime.utcnow() 
    start = end - timedelta(days=1)
    print("Sending media indexing requests from Sharechat service to Simple Search service ...")
    for i in coll.find({
        "media_type": {"$in": ["image", "video"]}, 
        "scraped_date": {'$gte':start,'$lt':end}}).limit(100): #limit for testing
        try:
            print(i["_id"])
            res = {}
            print("Fetching media data from Sharechat db ...")
            data = get_data(i)
            print("Sending media data to indexing queue via Simple Search server ...")
            response = index_media(str(data))
            if response.status_code == 200:
                res["response_timestamp"] = str(datetime.utcnow())
                res["response_text"] = json.loads(response.text) 
                print("Updating Rabbitmq status in Sharechat db record")
                coll.update_one(
                    {"_id": i["_id"]},
                    {"$set": {"simple_search.rabbitmq_status": res}})
                c+=1
            else:
                print(response.text, response.status_code)
        except Exception as e:
            print(logging.traceback.format_exc())
            print('Error sending data to queue', e)
    print("Sent {} media for indexing & updated their queue status in Sharechat db".format(c))
    return c


if __name__ == "__main__":
    IndexerSharechat()
