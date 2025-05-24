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
    url = os.getenv('URL')
    endpoint = '/wiki/api/v2/spaces/2564620362/pages?body-format=storage&limit=250'
    auth = HTTPBasicAuth(os.getenv('EMAIL'), os.getenv('TOKEN'))
    
    response = requests.get(url + endpoint,auth=auth)
    data = response.json()
    
    if(data['_links']['next']):
        response = requests.get(url + data['_links']['next'], auth=auth)
        data['results'].extend(response.json()['results'])

    return data

def filterParentPages(data):
    for i in data['results']:
        if i['status']!='archived' and i['parentId'] not in parent_ids: 
            parent_ids.append(i['parentId'])

def filterBadCharacters(string):
    characters = [':','/','<','>','*']
    for character in characters:
        if character in string:
            string.replace(character,'-')
    return string

def getParentTitle(data, parent_id):
    for i in data['results']:
        if i['id'] == parent_id:
            if i['id']!='2564620384':
                path.insert(0, i['title'].replace(':','-').replace('/','-'))
                return getParentTitle(data, i['parentId'])
            else:
                return path

def main():
    data = getConfluenceData()
    filterParentPages(data)
    for i in data['results']:
        if i['status']!='archived' and i['id'] not in parent_ids:
            global path
            path = []
            fullpath = 'Confluence/' + '/'.join(getParentTitle(data, i['parentId'])) + '/' + i['id']        

            output_file = Path(fullpath + '.md')
            output_file.parent.mkdir(exist_ok=True, parents=True)
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(md(i['body']['storage']['value']))
            
            pages.append({'id':i['id'],'path':i['title']})

main()
        
print('******** Total pages:' + str(len(pages)) + ' *********')
