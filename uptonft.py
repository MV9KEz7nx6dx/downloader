import requests
import json
import argparse


parser = argparse.ArgumentParser(description='Insert data to mongdb.net')
parser.add_argument("--token", help="Connection token", default="")
parser.add_argument("--path", help="Upload path", default="")


args = parser.parse_args()


headers = {
    'Authorization': 'Bearer ' + args.token
}

files = {'file': open(args.path, 'rb')}
response = requests.post('https://api.nft.storage/upload', headers=headers, files=files)
result = json.loads(response.text)
print(result['value']['cid'])
