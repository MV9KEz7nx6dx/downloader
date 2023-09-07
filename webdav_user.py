import sys
import os
import argparse
import json
import requests

parser = argparse.ArgumentParser(description='webdav信息')
parser.add_argument("--projet", help="deta.space的project_id", default="")
parser.add_argument("--apikey", help="deta.space的x_api_key", default="")
parser.add_argument("--name", help="要上传的云盘名称", default="")
parser.add_argument("--filename", help="要上传的文件名称", default="")

args = parser.parse_args()


DETA_DATAKEY=args.apikey
DETA_PROJECT_ID=args.projet

QUERY_URL=f"https://database.deta.sh/v1/{DETA_PROJECT_ID}/cloudreve/query"
#DELETE_URL=f"https://database.deta.sh/v1/{DETA_PROJECT_ID}/cloudreve/items/{args.name}"
UPDATE_URL=f"https://database.deta.sh/v1/{DETA_PROJECT_ID}/cloudreve/items/"

deta_headers = {
    'X-API-Key':DETA_DATAKEY,
    'Content-Type':'application/json'
}

payload = json.dumps({
  "query": [{"name": args.name}],
  "limit": 1
})
tasks_req = requests.post(QUERY_URL,headers=deta_headers,data=payload,verify=False)
tasks=json.loads(tasks_req.text)
if len(tasks['items']) < 1:
    quit()
task=tasks['items'][0]
cmd = f"curl --user {task['username']}:{{task['password']}} {{task['url']}}/videos/{args.filename} -T out/{args.filename}"
os.system(cmd)
# with open(os.environ['GITHUB_OUTPUT'], 'a') as fh:
#     print(f'username={task["username"]}',f'password={task["password"]}',f'url={task["url"]}', file=fh)

