import certifi
import pymongo
import sys
import argparse
from bson.json_util import dumps, loads

parser = argparse.ArgumentParser(description='Insert data to mongdb.net')
parser.add_argument("--con", help="Connection url", default="")
parser.add_argument("--name", help="Insert name", default="")
parser.add_argument("--size", help="Insert size", default="")

args = parser.parse_args()

if args.name is None:
  print("Nothing to save")
  quit()

client = pymongo.MongoClient(args.con, tlsCAFile=certifi.where())
mydb = client["mydb"]
taskcol = mydb["transfer"]

keyword="##"+args.name
task = taskcol.find_one({'url':{'$regex':keyword}})
taskcol.delete_one(task)

print('ok')
