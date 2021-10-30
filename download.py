import certifi
import pymongo
import sys
import argparse
from bson.json_util import dumps, loads
import os

parser = argparse.ArgumentParser(description='Insert data to mongdb.net')
parser.add_argument("--url", help="Download url", default="")
parser.add_argument("--filename", help="Download url", default="")



args = parser.parse_args()


# client = pymongo.MongoClient(args.con, tlsCAFile=certifi.where())
# mydb = client["mydb"]
# mycol = mydb["task"]


# x = mycol.find_one({})
# if x is None:
#     print("None")
#     quit()

# info = loads(dumps(x))
# mycol.delete_one(x)
# urlinfo = info['url'].split("##");
cmd = "aria2c --conf aria2.conf --seed-time=0 -o "+args.filename+" -d downloads -c \""+args.url+"\""
os.system(cmd)
