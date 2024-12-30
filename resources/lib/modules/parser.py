import xml.etree.ElementTree as ET
import json
import re
from .downloader import Downloader

class Parser:
    def __init__(self, url):
        self.url = url
    
    def get_list(self):
        if self.url.endswith('.xml'):
            try:
                xml = ET.fromstring(self.get_page())
            except ET.ParseError:
                xml = ET.fromstringlist(["<root>", self.get_page(), "</root>"])
            item_list = []
            for item in xml:
                item_list.append({child.tag: child.text for child in item})
            return json.dumps({'builds': item_list})    
        elif self.url.endswith('.json'):
            return self.get_page()
    
    def get_list2(self):
        try:
            xml = ET.fromstring(self.get_page())
        except ET.ParseError:
            xml = ET.fromstringlist(["<root>", self.get_page(), "</root>"])
        item_list = []
        for item in xml:
            item_list.append({child.tag: child.text for child in item})
        return json.dumps({'builds': item_list})    
    
    def get_page(self):
        if self.url.startswith('http'):
            d = Downloader(self.url)
            return d.get_urllib()
        else:
            return open(self.url).read()

class XmlParser:
    def __init__(self, xml_content):
        self.xml_content = xml_content

    def parse_builds(self):
        build_pattern = re.compile(r"<build>(.*?)</build>", re.DOTALL)
        sub_element_patterns = {
            "name": re.compile(r"<name>(.*?)</name>"),
            "version": re.compile(r"<version>(.*?)</version>"),
            "url": re.compile(r"<url>(.*?)</url>"),
            "icon": re.compile(r"<icon>(.*?)</icon>"),
            "fanart": re.compile(r"<fanart>(.*?)</fanart>"),
            "description": re.compile(r"<description>(.*?)</description>"),
            "preview": re.compile(r"<preview>(.*?)</preview>")
        }
        return self.parse(build_pattern, sub_element_patterns)
    
    def parse_videos(self):
        video_pattern = re.compile(r"<video>(.*?)</video>", re.DOTALL)
        sub_element_patterns = {
            "name": re.compile(r"<name>(.*?)</name>"),
            "url": re.compile(r"<url>(.*?)</url>"),
            "icon": re.compile(r"<icon>(.*?)</icon>"),
            "fanart": re.compile(r"<fanart>(.*?)</fanart>"),
            "description": re.compile(r"<description>(.*?)</description>")
        }
        return self.parse(video_pattern, sub_element_patterns)
        
    def parse(self, main_pattern, sub_patterns: list):
        items = main_pattern.findall(self.xml_content)
        parsed_items = []
        for item in items:
            data = {}
            for key, pattern in sub_patterns.items():
                match = pattern.search(item)
                data[key] = match.group(1) if match else ''
            parsed_items.append(data)
        return parsed_items