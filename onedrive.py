#!/usr/bin/env python
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import json
import os
import sys
from datetime import datetime, timedelta
from os.path import join, dirname
from os import getenv
from dotenv import load_dotenv

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)


class Onedrive:
    def __init__(self, tenant_id, client_id, client_secret, redirect):
        self.tenant_id = tenant_id
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect = redirect
        self.base_url = 'https://graph.microsoft.com/v1.0/'
        self.token = self.__token()
        self.headers = {
            'Authorization': "Bearer " + self.token,
            }

    def __token(self):
        data = {'grant_type': "client_credentials",
                'resource': "https://graph.microsoft.com",
                'scope': 'Sites.ReadWrite.All Files.ReadWrite.All',
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'redirect_uri': self.redirect}
        URL = (
            f"https://login.microsoftonline.com/{self.tenant_id}/oauth2/token")
        token_r = requests.post(URL, data=data)
        if token_r.ok:
            TOKEN = token_r.json().get('access_token')
            return TOKEN
        else:
            return 'ERROR'

    def site(self, site_name):
        self.site_name = site_name
        URL = f'{self.base_url}sites?search={self.site_name}'
        r = requests.get(
            URL, headers=self.headers)
        site = json.loads(r.text)
        self.site_id = site['value'][0]['id']

    def drive(self):
        URL = f'{self.base_url}sites/{self.site_id}/drive'
        r = requests.get(
            URL, headers=self.headers)
        drive = json.loads(r.text)
        self.drive_id = drive['id']

    def check_folder_exists(self, backup_folder):
        self.backup_folder = backup_folder
        URL = f'{self.base_url}drives/{self.drive_id}/root:/'
        r = requests.get(
            URL + self.backup_folder, headers=self.headers)
        if not r.ok:
            post_url = f'{self.base_url}drives/{self.drive_id}/root/children'
            headers = self.headers
            headers['Content-type'] = 'application/json'
            data = {
                "name": self.backup_folder,
                "folder": {}
            }
            r = requests.post(post_url, headers=headers, json=data)
            print(f'Backup folder created for database: {self.backup_folder}')
        else:
            print(f'Backup folder already exists for: {self.backup_folder}')

    def __requests_retry_session(
            self, retries=3, backoff_factor=0.3,
            status_forcelist=(500, 502, 504), session=None):
        session = session or requests.Session()
        retry = Retry(
            total=retries, read=retries, connect=retries,
            backoff_factor=backoff_factor, status_forcelist=status_forcelist)
        adapter = HTTPAdapter(max_retries=retry)
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        return session

    def upload(self, backup_folder_path, todays_folder, file):
        self.backup_folder_path = backup_folder_path
        self.todays_folder = todays_folder
        self.backup_file = file
        directory = rf"{self.backup_folder_path}/{self.todays_folder}"
        URL = (
            f"{self.base_url}drives/{self.drive_id}/root:/"
            f"{self.backup_folder}/{self.todays_folder}")
        headers = self.headers
        headers['Content-Type'] = 'application/gzip'
        print("Uploading file(s) to " + URL)
        for root, dirs, files in os.walk(directory):
            filepath = os.path.join(root, self.backup_file)
            print("Uploading "+self.backup_file+"....")
            fileHandle = open(filepath, 'rb')
            try:
                r = self.__requests_retry_session().put(
                    URL+"/"+self.backup_file+":/content", data=fileHandle,
                    headers=headers)
            except Exception as x:
                print("Script error")
                print(x)
                print(r.status_code, r.text)
                self.discord_post('ERROR')
            else:
                print("Script completed")
            fileHandle.close()

    def delete_files(self):
        URL = (
            f"{self.base_url}drives/{self.drive_id}/root:/"
            f"{self.backup_folder}")
        r = requests.get(
            URL+':/children', headers=self.headers)
        j = json.loads(r.text)
        for i in j['value']:
            today = datetime.now().replace(
                hour=0, minute=0, second=0, microsecond=0)
            created = datetime.strptime(
                i['createdDateTime'], "%Y-%m-%dT%H:%M:%SZ")
            start_date = (today - timedelta(days=7))
            if created < start_date:
                del_path = f"{self.base_url}/drive/items/{i['id']}"
                del_ret = requests.delete(del_path, headers=self.headers)
                print(del_ret)
                print('Folder Removed')


if __name__ == '__main__':
    onedrive = Onedrive(
        tenant_id=getenv('OD_TENANT_ID'),
        client_id=getenv('OD_CLIENT_ID'),
        client_secret=getenv('OD_CLIENT_SECRET'),
        redirect=getenv('OD_REDIRECT'),
        )
    if onedrive.token != "ERROR":
        onedrive.site(site_name=getenv('OD_SITE_NAME'))
        onedrive.drive()
        onedrive.check_folder_exists(backup_folder=getenv('DB_BACKUP_FOLDER'))
        onedrive.upload(
            backup_folder_path=getenv('DB_BACKUP_FOLDER_PATH'),
            todays_folder=sys.argv[1:][0], file=sys.argv[1:][1],)
        onedrive.delete_files()
    else:
        print("Error incorrect Onedrive token, cannot continue")
