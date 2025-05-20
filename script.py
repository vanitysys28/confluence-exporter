#https://centreon.atlassian.net//wiki/api/v2/spaces/2564620362/pages?body-format=storage&limit=250

import json
from pathlib import Path
from markdownify import markdownify as md

parent_ids = []
pages = []
path = []

json_file = open('data.json',encoding='utf8')
data = json.load(json_file)

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

for i in data['results']:
    if i['status']!='archived' and i['parentId'] not in parent_ids: 
        parent_ids.append(i['parentId'])

for i in data['results']:
    if i['status']!='archived' and i['id'] not in parent_ids:
        path = []
        pages.append({'id':i['id'],'path':i['title']})
        fullpath = 'Confluence/' + '/'.join(getParentTitle(i['parentId'])) + '/' + i['id']        
        output_file = Path(fullpath)
        output_file.parent.mkdir(exist_ok=True, parents=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(i['body']['storage']['value'])
        
print('******** Total pages:' + str(len(pages)) + ' *********')
