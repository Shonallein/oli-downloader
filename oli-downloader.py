from bs4 import BeautifulSoup
import json
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
    req = requests.get(url)
    soup = BeautifulSoup(req.content, 'html.parser')
    js = _fix_broken_json(soup.find_all(_is_json_info)[0].string)
    
    audio = json.loads(js)[0]['audio']
    mp3 = requests.get(audio['contentUrl'])
    with open(f'download/{audio["name"]}.mp3', 'wb') as f:
        f.write(mp3.content)

pathlib.Path('download').mkdir(parents=True, exist_ok=True)
_download_story('https://www.franceinter.fr/emissions/une-histoire-et-oli/ariane-ascaride') 
