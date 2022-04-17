from bs4 import BeautifulSoup
import json
import os
import pathlib
import re
import requests

def _is_json_info(tag):
    if tag.name != 'script':
        return
    if not 'type' in tag.attrs:
        return
    if tag['type'] != 'application/ld+json':
        return
    return True

def _fix_broken_json(json):
    def _replace(match):
        return f': "{match.group(1)}"'
    return re.sub(r'\:\s*\"\"(.*)\"\"', _replace, json)

def _download_story(url):
    print(f'Downloading {url}')
    req = requests.get(url)
    soup = BeautifulSoup(req.content, 'html.parser')
    js = _fix_broken_json(soup.find_all(_is_json_info)[0].string)
    
    audio = json.loads(js)[0]['audio']
    mp3 = requests.get(audio['contentUrl'])
    name = f'download/{audio["name"]}.mp3'
    if os.path.exists(name):
        print(f'Skipped "{name}". Already exists')
    with open(name, 'wb') as f:
        f.write(mp3.content)

def _list_stories_page(page):
    req = requests.get(f'https://www.franceinter.fr/emissions/une-histoire-et-oli?p={page}')
    soup = BeautifulSoup(req.content, 'html.parser')
    stories = []
    for card in soup.find_all('a', class_='card-text-sub'):
        stories.append(card['href'])
    return stories

def _list_stories():
    print(f'Gather stories list')
    req = requests.get('https://www.franceinter.fr/emissions/une-histoire-et-oli')
    soup = BeautifulSoup(req.content, 'html.parser')
    stories = []
    last_page_url = soup.find_all('li', class_='pager-item last')[0].a['href']
    match = re.match(r'^.*\?p\=(\d)$', last_page_url)
    stories = []
    for i in range(int(match.group(1))):
        stories.extend(_list_stories_page(i+1))
    return stories
    

pathlib.Path('download').mkdir(parents=True, exist_ok=True)
#_download_story('https://www.franceinter.fr/emissions/une-histoire-et-oli/ariane-ascaride') 
stories = _list_stories()
for story in stories:
    try:
        _download_story(story)
    except Exception as e:
        print(f'Fail!')
