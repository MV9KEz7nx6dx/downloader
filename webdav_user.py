import requests
import os
import time
import json
import mimetypes
import argparse
from urllib.parse import urlparse


parser = argparse.ArgumentParser(description='webdav信息')
parser.add_argument("--projet", help="deta.space的project_id", default="")
parser.add_argument("--apikey", help="deta.space的x_api_key", default="")
parser.add_argument("--name", help="要上传的云盘名称", default="")
parser.add_argument("--filename", help="要上传的文件名称", default="")
args = parser.parse_args()

DETA_DATAKEY=args.apikey
DETA_PROJECT_ID=args.projet

QUERY_URL=f"https://database.deta.sh/v1/{DETA_PROJECT_ID}/cloudreve/query"
UPDATE_URL=f"https://database.deta.sh/v1/{DETA_PROJECT_ID}/cloudreve/items/"

deta_headers = {
    'X-API-Key':DETA_DATAKEY,
    'Content-Type':'application/json'
}

def get_file_info(file_path):
    # 获取文件大小
    file_size = os.path.getsize(file_path)
    # 获取文件修改时间
    modification_time = os.path.getmtime(file_path)
    # 获取文件名
    file_name = os.path.basename(file_path)
    return file_size, modification_time, file_name

def get_cloudreve(cloudreve):
    # 获取或更新并返回cloudreve cookie
    cookie_cloudreve=cloudreve['cookie']
    base_url= cloudreve["url"]
    parsed_url = urlparse(base_url)
    host = parsed_url.netloc 
    headers = {
        'authority': host,
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'content-type': 'application/json;charset=UTF-8',
        'cookie': cloudreve['cookie'],
        'origin': base_url,
        'referer': base_url+'/home?path=%2Fvideos',
        'sec-ch-ua': '"Chromium";v="116", "Not)A;Brand";v="24", "Google Chrome";v="116"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36'
    }
    cookie_res = requests.get(base_url+"/api/v3/directory%2F",headers=headers,verify=False)
    cookie_result = json.loads(cookie_res.text)
    if cookie_result['code']==401:
        session_url = base_url+"/api/v3/user/session"
        payload = "{\"userName\":\""+cloudreve['username']+"\",\"Password\":\""+cloudreve['password']+"\",\"captchaCode\":\"\"}"
        headers = {
            'sec-ch-ua': '"Not.A/Brand";v="8", "Chromium";v="114", "Google Chrome";v="114"',
            'Accept': 'application/json, text/plain, */*',
            'Content-Type': 'application/json;charset=UTF-8',
            'Referer': cloudreve['url']+'/login',
            'sec-ch-ua-mobile': '?0',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
        }
        response = requests.request("POST", session_url, headers=headers, data=payload,verify=False)
        cookiedict = requests.utils.dict_from_cookiejar(response.cookies)
        cookie_cloudreve=cookiedict["cloudreve-session"]
        #cookies = requests.utils.cookiejar_from_dict(cookies)
    return cookie_cloudreve


def upload_file(url, filename, chunk_size):
    # 打开文件
    with open(filename, 'rb') as file:
        # 获取文件大小
        file_size = len(file.read())
        file.seek(0)
        # 计算总共需要分片的数量
        num_chunks = file_size // chunk_size
        if file_size % chunk_size != 0:
            num_chunks += 1
        # 分片上传
        for i in range(num_chunks):
            # 读取分片数据
            data = file.read(chunk_size)
            # 构造HTTP请求头，指定分片范围和总大小
            headers = {
                'Content-Length': str(len(data)),
                'Content-Range': 'bytes {}-{}/{}'.format(i * chunk_size, i * chunk_size + len(data) - 1, file_size)
            }
            # 发送分片数据
            response = requests.put(url, data=data, headers=headers,verify=False)
            # 打印上传结果
            print('Uploaded chunk {}/{} with status code {}'.format(i+1, num_chunks, response.status_code))

if __name__ == "__main__":
    file_path = "out/"+args.filename  # 替换为实际的文件路径
    file_size, modification_time, file_name = get_file_info(file_path)
    mime_type, encoding = mimetypes.guess_type(file_path)
    
    payload = json.dumps({
        "query": [{"name": args.name}],
        "limit": 1
    })
    tasks_req = requests.post(QUERY_URL,headers=deta_headers,data=payload,verify=False)
    tasks=json.loads(tasks_req.text)
    if len(tasks['items']) < 1:
        quit()
    task=tasks['items'][0]
    base_url= task["url"]
    parsed_url = urlparse(base_url)
    host = parsed_url.netloc 
    cloudreve_cookie=get_cloudreve(task)
    #更新cookie 
    putpayload = json.dumps({
        "set" : {
            "cookie": cloudreve_cookie,
        }
    })
    put_req = requests.patch(UPDATE_URL+task["key"],headers=deta_headers,data=putpayload,verify=False)
    #更新cookie结束
    url = base_url+"/api/v3/file/upload"
    headers = {
        'authority': host,
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'content-type': 'application/json;charset=UTF-8',
        'cookie': 'cloudreve-session='+cloudreve_cookie,
        'origin': base_url,
        'referer': base_url+'/home?path=%2Fvideos',
        'sec-ch-ua': '"Chromium";v="116", "Not)A;Brand";v="24", "Google Chrome";v="116"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36'
    }
    policy_res = requests.get(base_url+"/api/v3/directory%2F",headers=headers,verify=False)
    policy_result = json.loads(policy_res.text);
    payload = json.dumps({
        "path":"/videos/temp",
        "size":file_size,
        "name":file_name,
        "policy_id":policy_result['data']['policy']['id'],
        "last_modified":int(modification_time*1000),
        "mime_type":mime_type
    })
    init_response = requests.request("PUT", url, headers=headers, data=payload,verify=False)
    init_result=json.loads(init_response.text)
    sessionID=init_result['data']['sessionID']
    uploader=init_result['data']['uploadURLs'][0]
    chunkSize=init_result['data']['chunkSize']
    upload_file(uploader, file_path, chunkSize)
    complete_url = base_url+"/api/v3/callback/onedrive/finish/"+sessionID
    complete_payload = '{}'
    complete_response = requests.request("POST", complete_url, headers=headers, data=complete_payload,verify=False)
