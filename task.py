import certifi
import pymongo
import sys
import argparse
from bson.json_util import dumps, loads

parser = argparse.ArgumentParser(description='Insert data to mongdb.net')
parser.add_argument("--con", help="Connection url", default="")


args = parser.parse_args()


client = pymongo.MongoClient(args.con, tlsCAFile=certifi.where())
mydb = client["mydb"]
mycol = mydb["task"]


x = mycol.find_one({}, {"_id": 0})
if x is None:
    print("None")
    quit()

info = loads(dumps(x))
mycol.delete_one(x)
print(info['url'])
