import certifi
import pymongo
import sys
import argparse


parser = argparse.ArgumentParser(description='Insert data to mongdb.net')
parser.add_argument("--con", help="Connection url", default="")
parser.add_argument("--name", help="Insert name", default="")
parser.add_argument("--cid", help="Insert cid", default="")

args = parser.parse_args()


client = pymongo.MongoClient(args.con, tlsCAFile=certifi.where())
mydb = client["mydb"]
mycol = mydb["web3"]

mydict = {"name":args.name,"cid": args.cid,"issync":"0"}
x = mycol.insert_one(mydict)
print(x)
