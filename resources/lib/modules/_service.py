import json
import base64
from urllib.request import Request, urlopen
import xbmc
import xbmcgui
from uservar import buildfile, notify_url
from .maintenance import clear_packages_startup
from .parser import XmlParser, TextParser
from .addonvar import setting, setting_set, addon_name, isBase64, headers, dialog, local_string, addon_id, gui_save_default, build_file
from .build_install import restore_binary, binaries_path
from .addons_enable import enable_addons
from .save_data import backup_gui_skin
from . import  notify

CURRENT_BUILD = setting('buildname')
CURRENT_VERSION = setting('buildversion')


class Startup:
    def check_updates(self):
           if CURRENT_BUILD == 'No Build Installed':
               nobuild = dialog.yesnocustom(
                   addon_name,
                   'There is currently no build installed.\nWould you like to install one now?',
                   'Remind Later'
               )
               if nobuild == 1:
                   xbmc.executebuiltin(
                       f'ActivateWindow(10001, "plugin://{addon_id}/?mode=1",return)'
                   )
               elif nobuild == 0:
                   setting_set('buildname', 'No Build')
               return
               
           response = ''
           try:
               response = self.get_page(buildfile)
           except:
               return
           version = ''
           builds = []
           
           if '"builds"' in response or "'builds'" in response:
               builds = json.loads(response)['builds']
               
           elif '<version>' in response:
               xml = XmlParser(response)
               builds = xml.parse_builds()
               
           elif 'name="' in response:
               text = TextParser(response)
               builds = text.parse_builds()
           
           for build in builds:
               if build.get('name') == CURRENT_BUILD:
                   version = str(build.get('version'))
                   break
                   
           if version > CURRENT_VERSION and setting('update_passed') != 'true':
               update_available = xbmcgui.Dialog().yesnocustom(
                   addon_name,
                   f'{local_string(30047)} {CURRENT_BUILD} {local_string(30048)}\n{local_string(30049)} {CURRENT_VERSION}\n{local_string(30050)} {version}\n{local_string(30051)}',
                   'Remind Later'
               )
               
               if update_available == 1:
                   xbmc.executebuiltin(
                       f'ActivateWindow(10001, "plugin://{addon_id}/?mode=1",return)'
                   )
               elif update_available == 0:
                   setting_set('update_passed', 'true')
           elif version == CURRENT_VERSION and setting('update_passed') == 'true':
               setting_set('update_passed', 'false')
               
    def file_check(self, bfile):
        if isBase64(bfile):
            return base64.b64decode(bfile).decode('utf8')
        return bfile
            
    def get_page(self, url):
           req = Request(self.file_check(url), headers = headers)
           return urlopen(req).read().decode('utf-8')
        
    def save_menu(self):
        choices = [
            'Trakt & Debrid Data',
            'YouTube API Keys',
            'Favourites',
            'Advanced Settings',
            'Sources'
        ]
        save_select = dialog.multiselect(
            f'{addon_name} - {local_string(30052)}',
            choices,
            preselect=[]
        )  # Select Save Items
        if save_select is None:
            return
        save_items = [choices[index] for index in save_select]
                
        if 'Trakt & Debrid Data' in save_items:
            setting_set('savedata', 'true')
        else:
            setting_set('savedata', 'false')
            
        if 'YouTube API Keys' in save_items:
            setting_set('saveyoutube', 'true')
        else:
            setting_set('saveyoutube', 'false')
            
        if 'Favourites' in save_items:
            setting_set('savefavs', 'true')
        else:
            setting_set('savefavs', 'false')
            
        if 'Advanced Settings' in save_items:
            setting_set('saveadvanced', 'true')
        else:
            setting_set('saveadvanced', 'false')
        
        if 'Sources' in save_items:
            setting_set('savesources', 'true')
        else:
            setting_set('savesources', 'false')
  
        setting_set('firstrunSave', 'true')

    def notify_check(self):
        if notify_url in ('http://CHANGEME', 'http://slamiousproject.com/wzrd/notify19.txt', '', 'http://'):
            return
        
        info = notify.get_notify()
        current_notify = int(setting('notifyversion'))
        notify_version = info[0]
        message = info[1]
        if setting('firstrunNotify') != 'true' or notify_version > current_notify:
            notify.notification(message)
            setting_set('firstrunNotify', 'true')
            setting_set('notifyversion', str(notify_version))
    
    def run_startup(self):
        if setting('firstrunSave') != 'true':
            self.save_menu()
            xbmc.sleep(2000)
        if setting('firstrun') == 'true':
            enable_addons()
            backup_gui_skin(gui_save_default)
            setting_set('firstrun', 'false')
        else:
            if setting('autoclearpackages') == 'true':
                clear_packages_startup()
            xbmc.sleep(1000)
            self.notify_check()
            xbmc.sleep(3000)  # Delay Build Update Notification
            self.check_updates()
        if binaries_path.exists():
            restore_binary()
