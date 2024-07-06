import json, requests
import time
import re
import math
import hashlib
from cachelib import SimpleCache
import os
import sys
import argparse
import mimetypes
import os.path
import requests
import configparser
sys.path.append(os.path.abspath('../'))


parser = argparse.ArgumentParser()
parser.add_argument('--clientID', default='')
parser.add_argument('--clientSecret', default='')
parser.add_argument('--refreshToken', default='')
parser.add_argument('file', metavar='FILE')
parser.add_argument('--path', metavar='PATH', default='')
parser.add_argument('--block-limit', type=int, default=320*1024)
args = parser.parse_args()



class Onedrive():
    '''
    Onedrive:Onedrive网盘
    '''
    def __init__(self,provider='',region='',rootPath='',clientID='',clientSecret='',redirectUri='',refreshToken=''):
        # 创建配置文件对象 参数对照alist
        '''
        :param provider: 模型实例名称
        :param region: 地区
        :param rootPath: 根文件夹路径
        :param clientID: 客户端ID
        :param clientSecret: 客户端密钥
        :param redirectUri: 重定向 Uri
        :param refreshToken: 刷新令牌
        '''
        onedriveHostMap = {
            "global": {
                "Oauth": "https://login.microsoftonline.com",
                "Api": "https://graph.microsoft.com",
            },
            "cn": {
                "Oauth": "https://login.chinacloudapi.cn",
                "Api": "https://microsoftgraph.chinacloudapi.cn",
            },
            "us": {
                "Oauth": "https://login.microsoftonline.us",
                "Api": "https://graph.microsoft.us",
            },
            "de": {
                "Oauth": "https://login.microsoftonline.de",
                "Api": "https://graph.microsoft.de",
            },
        }
        self.config = configparser.SafeConfigParser()
        self.provider = provider
        self.region = region
        self.rootPath = rootPath
        self.clientID = clientID
        self.clientSecret = clientSecret
        self.redirectUri = redirectUri
        self.refreshToken = refreshToken
        self.accessToken = ""
        self.driveHost=onedriveHostMap[self.region]
        self.cache = SimpleCache()
        # 防止请求过于频繁，用于请求间隔时间
        self.sleep_time = 0.005
        # 缓存结果时间默认10分钟
        self.cache_time = 600
        self.url_cache_time = 600
        self.headers = {
            "user-agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.93 Safari/537.36",
            "content-type":"application/json;charset=UTF-8",
        }
        try:
            with open("configs/onedrive.ini") as f:
                self.config.read_file(f)
        except IOError:
            # 如果配置文件不存在，创建一个空的配置文件
            if not os.path.exists("configs/onedrive.ini"):
                # 创建文件夹及文件
                os.makedirs(os.path.dirname("configs/onedrive.ini"), exist_ok=True)
            with open("configs/onedrive.ini", "w") as f:
                self.config.write(f)
                
        if self.config.has_option(self.provider, 'refresh_token'):
            self.refreshToken = self.config.get(self.provider, 'refresh_token')
            self.accessToken = self.config.get(self.provider, 'access_token')
            self.headers['Authorization']='Bearer '+self.accessToken
        else:
            self.config.add_section(self.provider)
            self.refresh_token()
  

    # 以下都是辅助方法
    def refresh_token(self) -> str:
        loop_index = 1
        access_token = ''
        refresh_token = ''
        while True:
            url = self.driveHost["Oauth"]+ "/common/oauth2/v2.0/token"
            d = {
                "grant_type":    "refresh_token",
                "client_id":     self.clientID,
                "client_secret": self.clientSecret,
                "redirect_uri":  self.redirectUri,
                "refresh_token": self.refreshToken,
            }
            r = requests.post(url, verify=False, data=d)
            result = json.loads(r.text)
            if 'access_token' not in result:
                refresh_token = 'error'
                access_token = 'error'
            else:
                refresh_token = result['refresh_token']
                access_token = result['access_token']
                break
            if loop_index>2:
                break
            loop_index+=1

        if access_token == 'error':
            print("无法获取token请稍后再试")
        else:
            self.config.set(self.provider, 'refresh_token',refresh_token)
            self.config.set(self.provider, 'access_token',access_token)
            with open('configs/onedrive.ini', 'w') as f:
                self.config.write(f)
            self.accessToken = self.config.get(self.provider, 'access_token')
            self.headers['Authorization']='Bearer '+self.accessToken
        
        

od=Onedrive(provider="od",region='global',rootPath='/',clientID=args.clientID,clientSecret=args.clientSecret,redirectUri='https://alist.nn.ci/tool/onedrive/callback',refreshToken=args.refreshToken)

file_path = args.file
drive_path = args.path
block_lim = args.block_limit
assert block_lim > 0

access_token = od.accessToken

file_name = os.path.basename(file_path)
file_size = os.path.getsize(file_path)
file_mime_type = mimetypes.guess_type(file_path)[0]

file_obj = open(file_path, 'rb')
url = 'https://graph.microsoft.com/v1.0/me/drive/root:/{:s}:/createUploadSession'.format(drive_path + file_name)
r = requests.post(url, headers={
	'Authorization': 'Bearer ' + access_token,
	'Content-Type': file_mime_type,
})
r = r.json()
assert 'error' not in r, r['error']['message']
upload_url = r['uploadUrl']

block_pos = 0
while True:
	block_data = file_obj.read(block_lim)
	block_size = len(block_data)
	if block_size == 0:
		break
	print('Upload {:.0f}%'.format(block_pos * 100. / file_size))
	block_beg = block_pos
	block_end = block_pos + block_size - 1
	block_pos += block_size
	r = requests.put(upload_url, headers={
		'Content-Length': '{:d}'.format(block_size),
		'Content-Range': 'bytes {:d}-{:d}/{:d}'.format(block_beg, block_end, file_size),
	}, data=block_data)
	r = r.json()
	assert 'error' not in r, r['error']['message']
print('Upload complete')
file_obj.close()

print(r['id'])

