import requests
import json
import re
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
mycol = mydb["setting"]


username=""
r = requests.get('https://raino.dev/30pikpak')
username_regex = r"账号\<span class=\"notion-orange\"\>([^\<]*)\<\/span\>"
username_pattern = re.search(username_regex, r.text)
if username_pattern:
	username = username_pattern.group(1)
	#print(username_pattern.group(1))
else:
	print("找不到用户名")
	quit()


regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
print(re.fullmatch(regex, username))
if re.fullmatch(regex, username) is None:
	print("无效 Email")
else:
	print("有效 Email")
	#quit()

password_regex = r"密码\<span class=\"notion-orange\"\>([^\<]*)\<\/span\>"
password_pattern = re.search(password_regex, r.text)
if password_pattern:
	password = password_pattern.group(1)
	#print(password_pattern.group(1))
else:
	print("找不到密码")
	quit()


accounts={}
text="[]"
x = mycol.find_one({"name": "pikpak"})
if x is not None:
	text = x["value"]
accounts = json.loads(text)
find=list(filter(lambda account:account['username']==username and account['password']==password,accounts))

if find:
	quit()
else:
	account={}
	account['username']=username
	account['password']=password
	accounts.append(account)
res = mycol.update_one({"name": "pikpak"}, {"$set": {"value": json.dumps(accounts)}},upsert=True)

