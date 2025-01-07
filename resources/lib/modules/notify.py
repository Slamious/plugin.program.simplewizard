import xbmcgui
import xbmcaddon
from ..modules.parser import get_page
from uservar import notify_url

def get_notify() -> list:
    response = get_page(notify_url)
    try:
        split_response = response.split('|||')
        notify_version = int(split_response[0])
        message = split_response[1]
    except:
        notify_version = 0
        message = 'Improper Notifications format. Please check the Notifications text.'
    return [notify_version, message]
    

def notification(message: str) -> None:  
    class Notify(xbmcgui.WindowXMLDialog):
        KEY_NAV_BACK = 92
        TEXTBOX = 300
        CLOSEBUTTON = 302
        
        def onInit(self):
            self.getControl(self.TEXTBOX).setText(message)
            
        def onAction(self, action):
            if action.getId() == self.KEY_NAV_BACK:
                self.Close()
    
        def onClick(self, controlId):
            if controlId == self.CLOSEBUTTON:
                self.Close()

        def Close(self):
            self.close()
    
    d = Notify('notify.xml', xbmcaddon.Addon().getAddonInfo('path'), 'Default', '720p')
    d.doModal()
    del d