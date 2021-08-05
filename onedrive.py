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
from pprint import pprint

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
        token = self.__post(URL, data)
        if token:
            return token['access_token']
        else:
            return 'ERROR'

    def site(self, site_name):
        print("Getting Site ID...")
        self.site_name = site_name
        URL = f'{self.base_url}sites?search={self.site_name}'
        site = self.__get(URL)
        if len(site['value']) > 0:
            self.site_id = site['value'][0]['id']
            print(f'---> Site found: {self.site_id}')
            self.__drive()
        else:
            print(f'---> Site {self.site_name} could not be found.')

    def __drive(self):
        print("Getting Drive ID...")
        URL = f'{self.base_url}sites/{self.site_id}/drive'
        drive = self.__get(URL)
        if drive:
            self.drive_id = drive['id']
            print(f'---> Drive found: {self.drive_id}')
        else:
            print('---> Drive could not be found within your specified Site.')

    def check_folder_exists(self, backup_folder):
        print("Checking if backup folder exists...")
        self.backup_folder = backup_folder
        URL = (
            f'{self.base_url}drives/{self.drive_id}/root:/'
            f'{self.backup_folder}')
        r = self.__get(URL)
        if not r:
            self.__create_folder()
        else:
            print(
                f'---> Backup folder already exists for: {self.backup_folder}')

    def __create_folder(self):
        url = f'{self.base_url}drives/{self.drive_id}/root/children'
        headers = self.headers
        headers['Content-type'] = 'application/json'
        data = {
            "name": self.backup_folder,
            "folder": {}
        }
        self.__post(url, json.dumps(data))
        print(f'---> Backup folder created for database: {self.backup_folder}')

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
        print("Uploading backup file...")
        self.backup_folder_path = backup_folder_path
        self.todays_folder = todays_folder
        self.backup_file = file
        directory = rf"{self.backup_folder_path}/{self.todays_folder}"
        URL = (
            f"{self.base_url}drives/{self.drive_id}/root:/"
            f"{self.backup_folder}/{self.todays_folder}")
        headers = self.headers
        headers['Content-Type'] = 'application/gzip'
        print("---> Backup files uploading to " + URL)
        for root, dirs, files in os.walk(directory):
            filepath = os.path.join(root, self.backup_file)
            print("Uploading "+self.backup_file+"...")
            fileHandle = open(filepath, 'rb')
            try:
                r = self.__requests_retry_session().put(
                    URL+"/"+self.backup_file+":/content", data=fileHandle,
                    headers=headers)
            except Exception as x:
                print("---> Upload failed")
                print(x)
                print(r.status_code, r.text)
            else:
                print("---> Upload completed")
            fileHandle.close()

    def delete_files(self):
        URL = (
            f"{self.base_url}drives/{self.drive_id}/root:/"
            f"{self.backup_folder}:/children")
        r = self.__get(URL)
        if r:
            for i in r['value']:
                today = datetime.now().replace(
                    hour=0, minute=0, second=0, microsecond=0)
                created = datetime.strptime(
                    i['createdDateTime'], "%Y-%m-%dT%H:%M:%SZ")
                start_date = (today - timedelta(days=7))
                if created < start_date:
                    print(f"Deleting folder {i['name']}")
                    delete_path = f"{self.base_url}/drive/items/{i['id']}"
                    del_ret = self.__delete(delete_path)
                    print(del_ret)
                    print('---> Folder removed')

    def __get(self, url):
        result = requests.get(url, headers=self.headers)
        if result.ok:
            return json.loads(result.text)
        else:
            return result.ok

    def __post(self, url, data):
        if hasattr(self, 'headers'):
            headers = self.headers
        else:
            headers = None
        result = requests.post(url, headers=headers, data=data)
        if result.ok:
            return json.loads(result.text)
        else:
            return result.ok

    def __delete(self, url):
        result = requests.delete(url, headers=self.headers)
        if result.ok:
            return result.text
        else:
            return result.ok


if __name__ == '__main__':
    onedrive = Onedrive(
        tenant_id=getenv('OD_TENANT_ID'),
        client_id=getenv('OD_CLIENT_ID'),
        client_secret=getenv('OD_CLIENT_SECRET'),
        redirect=getenv('OD_REDIRECT'),
        )
    if onedrive.token != "ERROR":
        onedrive.site(site_name=getenv('OD_SITE_NAME'))
        if hasattr(onedrive, 'drive_id'):
            onedrive.check_folder_exists(
                backup_folder=getenv('DB_BACKUP_FOLDER'))
            onedrive.upload(
                backup_folder_path=getenv('DB_BACKUP_FOLDER_PATH'),
                todays_folder=sys.argv[1:][0], file=sys.argv[1:][1],)
            onedrive.delete_files()
        else:
            print(
                f"No Site found for: {getenv('OD_SITE_NAME')}, "
                f"cannot continue")
    else:
        print("Error invalid Onedrive token, cannot continue")
