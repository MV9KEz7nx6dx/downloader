import certifi
import pymongo
import sys
import argparse
from bson.json_util import dumps, loads

parser = argparse.ArgumentParser(description='Insert data to mongdb.net')
parser.add_argument("--con", help="Connection url", default="")
parser.add_argument("--name", help="Insert name", default="")

args = parser.parse_args()

json_data = sys.stdin.read()
file = json.loads(json_data)
if not file['status']:
    print("文件错误")
    quit()
  
mydict = {"id":file['data']['file']['metadata']['id'],"name":file['data']['file']['metadata']['name'],"size":str(file['data']['file']['metadata']['size']['bytes']),"url":file['data']['file']['url']['full']}

client = pymongo.MongoClient(args.con, tlsCAFile=certifi.where())
mydb = client["mydb"]
mycol = mydb["web3"]

myfilecol = mydb['myfile']
x = myfilecol.insert_one(mydict)

taskcol = mydb["transfer"]
keyword="##"+args.name
task = taskcol.find_one({'url':{'$regex':keyword}})
taskcol.delete_one(task)

print(x)
