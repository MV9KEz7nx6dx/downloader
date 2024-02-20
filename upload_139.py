import math
import os
import hashlib
import argparse
import requests
import xmltodict
from urllib import parse

parser = argparse.ArgumentParser(description='上传文件到yun.139.com')
parser.add_argument("--auth", help="Authorization认证，不带Basic", default="")
parser.add_argument("--account", help="上传账号：手机号", default="")
parser.add_argument("--folder", help="上传文件夹路径", default="")
parser.add_argument("--cataId", help="上传到的文件夹ID", default="")
args = parser.parse_args()

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

def updata_file(ufile):
    file_path = ufile[0]
    file_name = ufile[1]
    file_size = ufile[2]
    chunk_size = 1024 * 1024 * 100  # 每次上传的文件块大小为32G
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
    print(result)
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
                    "contentSize": f"{str(len(up_data))}",
                    "Range": f"bytes={offset}-{offset + len(up_data) - 1}",
                    "rangeType": "0",
                    "Content-Type": f"*/*;name={parse.quote(file_name)}"
                }
                up_response = requests.post(url = upload_url, headers = up_headers, data = up_data)
                print(up_response)
                if up_response.status_code == 200:
                    print(f"Uploaded chunk {offset}-{offset + len(up_data) - 1}")
                else:
                    print(f"Failed to upload chunk {offset}-{offset + len(up_data) - 1}")
                offset += len(up_data)



if __name__ == "__main__":
    files = list_visible_files(args.folder)
    for tfile in files:
        updata_file(tfile)
