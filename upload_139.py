import math
import os
import hashlib
import uuid
import argparse
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import xmltodict
from urllib import parse
import random
import string
import time
import json
import base64
import urllib.parse
import datetime


session = requests.Session()
retries = Retry(total=3, backoff_factor=1)
session.mount('http://', HTTPAdapter(max_retries=retries))
session.mount('https://', HTTPAdapter(max_retries=retries))

parser = argparse.ArgumentParser(description='上传文件到yun.139.com')
parser.add_argument("--type", help="上传类型1:个人云，2家庭云", type=int, default=1)
parser.add_argument("--auth", help="Authorization认证，不带Basic", default="")
parser.add_argument("--account", help="上传账号：手机号", default="")
parser.add_argument("--folder", help="上传文件夹路径", default="")
parser.add_argument("--cataId", help="上传到的文件夹ID", default="")
parser.add_argument("--cloudId", help="上传到家庭云的ID", default="")
parser.add_argument("--path", help="上传到家庭云的PATH", default="")
args = parser.parse_args()


FAMILY_UPLOAD_URL = 'https://yun.139.com/orchestration/familyCloud-rebuild/content/v1.0/getFileUploadURL'
UA = 'Mozilla/5.0 (Linux; Android 13; 2304FPN6DC Build/TKQ1.220829.002; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/115.0.5790.40 Mobile Safari/537.36 MCloudApp/10.1.0'
UPLOAD_URL = 'http://ose.caiyun.feixin.10086.cn/richlifeApp/devapp/IUploadAndDownload'

headers = {
    'x-huawei-uploadSrc': '1',
    'x-ClientOprType': '11',
    'Connection': 'keep-alive',
    'x-NetType': '6',
    'x-DeviceInfo': '6|127.0.0.1|1|10.0.1|Xiaomi|M2012K10C|CB63218727431865A48E691BFFDB49A1|02-00-00-00-00-00|android 11|1080X2272|zh||||032|',
    'x-huawei-channelSrc': '10000023',
    'x-MM-Source': '032',
    'x-SvcType': '1',
    'APP_NUMBER': args.account,
    'Authorization': 'Basic '+args.auth,
    'X-Tingyun-Id': 'p35OnrDoP8k;c=2;r=1955442920;u=43ee994e8c3a6057970124db00b2442c::8B3D3F05462B6E4C',
    'Host': 'ose.caiyun.feixin.10086.cn',
    'User-Agent': 'okhttp/3.11.0',
    'Content-Type': 'application/xml; charset=UTF-8',
    'Accept': '*/*'
}


def Yun139Sign(timestamp, key, data):
    #去除多余空格
    data = data.strip()
    data = urllib.parse.quote(data,safe="")
    c = list(data)
    c.sort()
    json = ''.join(c)
    s1 = hashlib.md5(base64.b64encode(json.encode('utf-8'))).hexdigest()
    s2 = hashlib.md5((timestamp + ":" + key).encode('utf-8')).hexdigest()
    return hashlib.md5((s1 + s2).encode('utf-8')).hexdigest().upper()

def generate_uuid():
    """
    Generates a UUID (Universally Unique Identifier) according to RFC 4122, version 4.

    Returns:
        A UUID string.
    """

    # Create a UUID object
    uuid_object = uuid.uuid4()

    # Convert the UUID object to a string
    uuid_str = str(uuid_object)

    # Remove the hyphens from the UUID string
    uuid_str = uuid_str.replace("-", "")

    return uuid_str

def list_visible_files(root_dir):
    files_info = []
    for dirpath, dirnames, filenames in os.walk(root_dir):
        # 排除隐藏文件和文件夹
        dirnames[:] = [d for d in dirnames if not d.startswith('.')]
        filenames = [f for f in filenames if not f.startswith('.')]
        for filename in filenames:
            file_path = os.path.join(dirpath, filename)
            file_size = os.path.getsize(file_path)
            files_info.append((file_path, filename, file_size))
    return files_info
  
def calculate_md5(file_path):
    with open(file_path, "rb") as file:
        file_hash = hashlib.md5()
        while chunk := file.read(4096):
            file_hash.update(chunk)
    return file_hash.hexdigest()



def upload_file(ufile):
    file_path = ufile[0]
    file_name = ufile[1]
    file_size = ufile[2]
    chunk_size = 1024 * 1024 * 100  # 每次上传的文件块大小为32G
    if int(file_size)>1024*1024*1024*30:
        chunk_size = 1024 * 1024 * 500
    digest = calculate_md5(file_path)
    payload = '''
                <pcUploadFileRequest>
                    <ownerMSISDN>{phone}</ownerMSISDN>
                    <fileCount>1</fileCount>
                    <totalSize>0</totalSize>
                    <uploadContentList length="1">
                        <uploadContentInfo>
                            <comlexFlag>0</comlexFlag>
                            <contentDesc><![CDATA[]]></contentDesc>
                            <contentName><![CDATA[{filename}]]></contentName>
                            <contentSize>{filesize}</contentSize>
                            <contentTAGList></contentTAGList>
                            <digest>{digest}</digest>
                            <exif/>
                            <fileEtag>0</fileEtag>
                            <fileVersion>0</fileVersion>
                            <updateContentID></updateContentID>
                        </uploadContentInfo>
                    </uploadContentList>
                    <newCatalogName></newCatalogName>
                    <parentCatalogID>{parent_catalogid}</parentCatalogID>
                    <operation>0</operation>
                    <path></path>
                    <manualRename>2</manualRename>
                    <autoCreatePath length="0"/>
                    <tagID></tagID>
                    <tagType></tagType>
                </pcUploadFileRequest>
            '''.format(phone = args.account,filename=file_name,filesize=file_size,digest=digest,parent_catalogid = args.cataId)
    response = requests.post(url = UPLOAD_URL, headers = headers, data = payload)
    if response is None:
        return
    if response.status_code != 200:
        return print('上传失败')
    print(response.text)
    result = xmltodict.parse(response.text)
    is_need_upload = 0
    if int(result['result']['uploadResult']['newContentIDList']['@length'])==1:
        is_need_upload = int(result['result']['uploadResult']['newContentIDList']['newContent']['isNeedUpload'])
    else:
        is_need_upload = int(result['result']['uploadResult']['newContentIDList']['newContent'][0]['isNeedUpload'])
    if is_need_upload ==1:
        upload_url = result['result']['uploadResult']['redirectionUrl']
        upload_id = result['result']['uploadResult']['uploadTaskID']
        with open(file_path, "rb") as file:
            total_size = int(file_size)
            offset = 0
            while offset < total_size:
                file.seek(offset)
                up_data = file.read(chunk_size)
                up_headers = {
                    "UploadtaskID": upload_id,
                    "contentSize": f"{str(int(file_size))}",
                    "Range": f"bytes={offset}-{offset + len(up_data) - 1}",
                    "rangeType": "0",
                    "Content-Type": f"*/*;name={parse.quote(file_name)}"
                }
                up_response = requests.post(url = upload_url, headers = up_headers, data = up_data)
                if up_response.status_code == 200:
                    print(f"Uploaded chunk {offset}-{offset + len(up_data) - 1}")
                else:
                    print(f"Failed to upload chunk {offset}-{offset + len(up_data) - 1}")
                offset += len(up_data)

def upload_family_file(ufile):
    file_path = ufile[0]
    file_name = ufile[1]
    file_size = ufile[2]
    chunk_size = 1024 * 1024 * 100  # 每次上传的文件块大小为32G
    if int(file_size)>1024*1024*1024*30:
        chunk_size = 1024 * 1024 * 500
    digest = calculate_md5(file_path)
    seqNo=generate_uuid()
    payload = json.dumps({"cloudID":args.cloudId,"path":args.path,"operation":0,"cloudType":1,"catalogType":3,"manualRename":2,"fileCount":1,"totalSize":file_size,"uploadContentList":[{"contentName":file_name,"contentSize":file_size,"digest":digest}],"seqNo":seqNo,"commonAccountInfo":{"account":args.account,"accountType":1}})
    timestamp = int(time.time())
    formatted_time = datetime.datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
    key = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
    sign = Yun139Sign(formatted_time, key,payload)
    headers = {
        'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
        'mcloud-route': '001',
        'x-yun-module-type': '100',
        'x-yun-app-channel': '10000034',
        'Authorization': 'Basic '+args.auth,
        'x-huawei-channelSrc': '10000034',
        "x-DeviceInfo":"||9|6.6.0|chrome|95.0.4638.69|uwIy75obnsRPIwlJSd7D9GhUvFwG96ce||macos 10.15.2||zh-CN|||",
        'caller': 'web',
        'x-yun-channel-source': '10000034',
        'x-inner-ntwk': '2',
        'sec-ch-ua-platform': '"macOS"',
        'CMS-DEVICE': 'default',
        'mcloud-client': '10701',
        'mcloud-channel': '1000101',
        'mcloud-sign': formatted_time + "," + key + "," + sign,
        'x-m4c-src': '10002',
        'INNER-HCY-ROUTER-HTTPS': '1',
        'mcloud-version': '7.13.1',
        'Content-Type': 'application/json;charset=UTF-8',
        'x-SvcType': '2',
        'Accept': 'application/json, text/plain, */*',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'x-yun-api-version': 'v1',
        'sec-ch-ua-mobile': '?0',
        'Referer': 'https://yun.139.com/w/',
        'x-yun-svc-type': '2',
        'x-m4c-caller': 'PC'
    }      
    response = session.post(url = FAMILY_UPLOAD_URL, headers = headers, data = payload)
    if response is None:
        return
    if response.status_code != 200:
        return print('上传失败')
    result = json.loads(response.text)
    is_need_upload = int(result['data']['uploadResult']['newContentIDList'][0]['isNeedUpload'])
    if is_need_upload ==1:
        upload_url = result['data']['uploadResult']['redirectionUrl']
        upload_id = result['data']['uploadResult']['uploadTaskID']
        with open(file_path, "rb") as file:
            total_size = int(file_size)
            offset = 0
            while offset < total_size:
                file.seek(offset)
                up_data = file.read(chunk_size)
                up_headers = {
                    "UploadtaskID": upload_id,
                    "contentSize": f"{str(int(file_size))}",
                    "Range": f"bytes={offset}-{offset + len(up_data) - 1}",
                    "rangeType": "0",
                    "Content-Type": f"*/*;name={parse.quote(file_name)}"
                }
                max_retries = 3
                retry_count = 0
                while retry_count < max_retries:
                    try:
                        up_response = session.post(url=upload_url, headers=up_headers, data=up_data, timeout=600)
                        if up_response.status_code == 200:
                            print(f"Uploaded chunk {offset}-{offset + len(up_data) - 1}")
                            break  # 如果上传成功，跳出循环
                        else:
                            print(f"Failed to upload chunk {offset}-{offset + len(up_data) - 1}")
                    except Exception as e:
                        print(f"Error occurred while uploading chunk: {e}")
                    time.sleep(1)  
                    retry_count += 1
                offset += len(up_data)


if __name__ == "__main__":
    files = list_visible_files(args.folder)
    for tfile in files:
        if args.type == 2:
            upload_family_file(tfile)
        else:
            upload_file(tfile)
