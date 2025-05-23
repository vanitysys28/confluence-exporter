import os
import requests
from requests.auth import HTTPBasicAuth
import json
from dotenv import load_dotenv
from pathlib import Path
from markdownify import markdownify as md

load_dotenv()

parent_ids = []
pages = []
path = []

def getConfluenceData():
    json = []

    url = os.getenv('URL')
    endpoint = '/wiki/api/v2/spaces/2564620362/pages?body-format=storage&limit=250&cursor=eyJpZCI6IjI2NzQwMzI2OTgiLCJjb250ZW50T3JkZXIiOiJpZCIsImNvbnRlbnRPcmRlclZhbHVlIjoyNjc0MDMyNjk4fQ=='
    auth = HTTPBasicAuth(os.getenv('EMAIL'), os.getenv('TOKEN'))
    
    response = requests.get(url + endpoint,auth=auth)
    data = response.json()

    json.append(data['results'])

    if(data['_links']['next']):
        response = requests.get(url + data['_links']['next'])
        data = response.json()
        json.append(data['results'])

    return json

def filterBadCharacters(string):
    characters = [':','/','<','>','*']
    for character in characters:
        if character in string:
            string.replace(character,'-')
    return string

def getParentTitle(parent_id):
    for i in data['results']:
        if i['id'] == parent_id:
            if i['id']!='2564620384':
                path.insert(0, i['title'].replace(':','-').replace('/','-'))
                return getParentTitle(i['parentId'])
            else:
                return path

def filterPages(data):
    for i in data:
        if i['status']!='archived' and i['parentId'] not in parent_ids: 
            A
            parent_ids.append(i['parentId'])

def main():
    data = getConfluenceData()
    filterPages(data)
    for i in data:
        if i['status']!='archived' and i['id'] not in parent_ids:
            path = []
            pages.append({'id':i['id'],'path':i['title']})
            fullpath = 'Confluence/' + '/'.join(getParentTitle(i['parentId'])) + '/' + i['id']        
            output_file = Path(fullpath + '.md')
            output_file.parent.mkdir(exist_ok=True, parents=True)
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(md(i['body']['storage']['value']))

main()
        
print('******** Total pages:' + str(len(pages)) + ' *********')
