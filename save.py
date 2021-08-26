import certifi
import pymongo
import sys
import argparse


parser = argparse.ArgumentParser(description='Insert data to mongdb.net')
parser.add_argument("--con", help="Connection url", default="")
parser.add_argument("--url", help="Insert url", default="Test Title")

args = parser.parse_args()


client = pymongo.MongoClient(args.con, tlsCAFile=certifi.where())
mydb = client["mydb"]
mycol = mydb["web3"]

mydict = {"url": args.url}
x = mycol.insert_one(mydict)
print(x)
