import certifi
import pymongo
import sys
import argparse
from bson.json_util import dumps, loads
import os

parser = argparse.ArgumentParser(description='Insert data to mongdb.net')
parser.add_argument("--con", help="Connection url", default="")
parser.add_argument("--isnow", help="execute now", default="0")



args = parser.parse_args()


client = pymongo.MongoClient(args.con, tlsCAFile=certifi.where())
mydb = client["mydb"]
mycol = mydb["task"]


x = mycol.find_one({"isnow": args.isnow})
if x is None:
    print("None")
    quit()

info = loads(dumps(x))
mycol.delete_one(x)
urlinfo = info['url'].split("##");
cmd = "aria2c --conf aria2.conf --seed-time=0 -o "+urlinfo[1]+" -d downloads -c \""+urlinfo[0]+"\""
os.system(cmd)
