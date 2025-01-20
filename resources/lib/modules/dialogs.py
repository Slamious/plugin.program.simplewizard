import os
from typing import List
import xbmc
from xbmcaddon import Addon
from . import pyxbmct

ICON = Addon().getAddonInfo('icon')
PATH = Addon().getAddonInfo('path')
IMAGES = os.path.join(PATH, 'resources', 'lib', 'modules', 'pyxbmct', 'textures', 'confluence', 'AddonWindow')

class SelectDialog(pyxbmct.BlankDialogWindow): 
    def __init__(self, heading:str, labels: List[str]=None, icon: str=ICON):
        super().__init__()
        self.setGeometry(1290, 730, 50, 30)
        #self.setGeometry(640, 480, 50, 30)
        self.heading = heading
        self.labels = [] if labels is None else labels
        self.icon = icon
        self.selected = -1
        self.set_controls()
        self.set_navigation()
    
    def set_controls(self):
        self.connect(pyxbmct.ACTION_NAV_BACK, self.close)
        self.fanart = pyxbmct.Image(Addon().getAddonInfo('fanart'))
        self.placeControl(self.fanart, 0, 0, 50, 30)
        self.overlay = pyxbmct.Image(os.path.join(IMAGES, 'ContentPanel.png'))
        self.placeControl(self.overlay, -1, -1, 52, 32)
        self.close_button = pyxbmct.Button('Cancel')
        self.placeControl(self.close_button, 45, 27, 5, 3)
        self.connect(self.close_button, self.close)
        
        # List
        self.list = pyxbmct.List(_space=4, _itemHeight=65)
        self.placeControl(self.list, 4, 1, 49, 19)
        self.icon_control = pyxbmct.Image(self.icon, aspectRatio=2)
        self.placeControl(self.icon_control, 1, 22, 47, 7)
        self.list.addItems(self.labels)
        self.connect(self.list, lambda: self.update_selected(self.list.getListItem(self.list.getSelectedPosition()).getLabel()))
    
    def update_selected(self, label: str):
        self.selected = self.labels.index(label)
        self.close()
    
    def setAnimation(self, control):
        # Set fade animation for all add-on window controls
        control.setAnimations([('WindowOpen', 'effect=slide start=0,200 end=0 time=300 tween=quadratic',),
                                ('WindowClose', 'effect=fade start=100 end=0 time=500',)])

    def set_navigation(self):
        # Set navigation between controls
        self.list.controlUp(self.close_button)
        self.list.controlDown(self.close_button)
        self.list.controlLeft(self.close_button)
        self.list.controlRight(self.close_button)
        self.close_button.controlUp(self.list)
        self.close_button.controlDown(self.list)
        self.close_button.controlLeft(self.list)
        self.close_button.controlRight(self.list)
        # Set initial focus
        self.setFocus(self.list)
    
    def run(self) -> int:
        self.doModal()
        return self.selected

def select_dialog(heading: str, labels: List[str]=None, icon: str=Addon().getAddonInfo('icon')):
    dialog = SelectDialog(heading, labels=labels, icon=icon)
    selected = dialog.run()
    del dialog
    xbmc.executebuiltin('Dialog.Close(busydialog)')
    return selected

if __name__ == '__main__':
    help(pyxbmct.AddonDialogWindow)
    