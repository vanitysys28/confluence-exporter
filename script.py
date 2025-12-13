import os
import requests
import re
from requests.auth import HTTPBasicAuth
import json
from dotenv import load_dotenv
from pathlib import Path
from markdownify import markdownify as md

load_dotenv()

parent_ids = []
pages = []
path = []

def getConfluenceSpacesData():
    url = os.getenv('URL')
    endpoint = '/wiki/api/v2/spaces/2564620362/pages?body-format=storage&limit=250'
    auth = HTTPBasicAuth(os.getenv('EMAIL'), os.getenv('TOKEN'))
    
    response = requests.get(url + endpoint,auth=auth)
    data = response.json()
    
    if(data['_links']['next']):
        response = requests.get(url + data['_links']['next'], auth=auth)
        data['results'].extend(response.json()['results'])

    return data

def getConfluenceFoldersData(folder):
    url = os.getenv('URL')
    endpoint = '/wiki/api/v2/folders/'
    auth = HTTPBasicAuth(os.getenv('EMAIL'), os.getenv('TOKEN'))
    
    response = requests.get(url + endpoint + folder,auth=auth)
    data = response.json()
    
    return data

def filterParentPages(data):
    for i in data['results']:
        if i['status']!='archived' and i['parentId'] not in parent_ids: 
            parent_ids.append(i['parentId'])

def filterBadCharacters(string):
    characters = [':','\\','/','<','>','*','"','|','?']
    for character in characters:
        if character in string:
            string = string.replace(character,'_')
    return string

def getParentTitle(data, parent_id):
    folders = [result['parentId'] for result in data['results'] if result.get('parentType') == 'folder']
    
    if parent_id in folders:
        if getConfluenceFoldersData(parent_id)['parentId']!='2564620384':
            path.insert(0, getConfluenceFoldersData(parent_id)['title'])
            return getParentTitle(data, getConfluenceFoldersData(parent_id)['parentId'])
        else:
            path.insert(0, getConfluenceFoldersData(parent_id)['title'])
            return path

    for i in data['results']:
        if i['id'] == parent_id:
            if i['id']!='2564620384':
                path.insert(0, filterBadCharacters(i['title']))
                return getParentTitle(data, i['parentId'])
            else:
                return path 

def sanitizeConfluenceTags(content):
    code_pattern = r'(?s)(<ac:structured-macro ac:name="code".*?CDATA\[)(.*?)(]]>.*?</ac:structured-macro>)'
    image_pattern = r'(?s)(<ac:image .*?ac:src=)(.*?)(><ri:url.*?</ac:image>)'
    sanitized_content = re.sub(code_pattern,r"<pre><code>\2</code></pre>",content)
    sanitized_content = re.sub(image_pattern,r"<img src=\2></img>",sanitized_content)
    return sanitized_content

def main():
    data = getConfluenceSpacesData()
    filterParentPages(data)
    for i in data['results']:
        if i['status']!='archived' and i['id'] not in parent_ids:
            global path
            path = []
            fullpath = 'Confluence/' + '/'.join(getParentTitle(data, i['parentId'])) + '/' + filterBadCharacters(i['title']) 
            full_path_with_prefix = f"\\\\?\\{os.path.abspath(fullpath)}"       

            output_file = Path(full_path_with_prefix + '.md')
            output_file.parent.mkdir(exist_ok=True, parents=True)

            with open(output_file, 'w', encoding='utf-8') as f:
                confluence_content = i['body']['storage']['value']
                sanitized_content = sanitizeConfluenceTags(confluence_content)
                f.write(md(sanitized_content))
            
            pages.append({'id':i['id'],'path':i['title']})

main()
        
print('******** Total pages:' + str(len(pages)) + ' *********')
