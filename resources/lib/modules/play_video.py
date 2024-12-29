import sys
import re
import requests
import xbmc
import xbmcgui

USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:132.0) Gecko/20100101 Firefox/132.0'
HEADERS = {"User-Agent": USER_AGENT}

def play_video(name: str, url: str, icon:str, description:str):
    if 'rumble.com' in url:
        link = resolve_rumble(url)
    elif 'youtu.be' in url:
        link = resolve_youtube(url)
    else:
        link = url
    if not link:
        sys.exit()
    liz = xbmcgui.ListItem(name, path=link)
    liz.setInfo('video', {'title': name, 'plot': description})
    liz.setArt({'thumb': icon, 'icon': icon, 'poster': icon})
    xbmc.Player().play(link, liz)

def resolve_rumble(url: str) -> str:
    _id = ''
    response = requests.get(url, headers=HEADERS, timeout=10).text
    pattern = r'"video":"(.+?)"'
    match = re.search(pattern, response)
    if match:
        _id = match.group(1)
        link = f'https://rumble.com/embedJS/u3/?request=video&ver=2&v={_id}'
        response = requests.get(link, headers=HEADERS, timeout=10).json()
        mp4 = response['ua']['mp4']
        mp4_sorted = dict(sorted(mp4.items(), key=lambda item: int(item[0]), reverse=True))
        first_item_url = next(iter(mp4_sorted.values()))["url"]
        return first_item_url

def resolve_youtube(url: str) -> str:
    pattern = r"youtu\.be/([a-zA-Z0-9_-]+)"
    match = re.search(pattern, url)
    if match:
        video_id = match.group(1)
        return f'plugin://plugin.video.youtube/play/?video_id={video_id}'

