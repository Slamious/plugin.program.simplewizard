import os
from urllib.request import Request, urlopen
import xbmc
import xbmcgui

class Downloader:
    def __init__(self, url):
        self.url = url
        self.user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        self.headers = {"User-Agent": self.user_agent}
        
    def get_urllib(self, decoding=True):
        req = Request(self.url, headers = self.headers)
        with urlopen(req) as response:
            if decoding:
                return response.read().decode('utf-8')
            return response.read()
    
    def get_session(self, decoding=True, stream=False):
        import requests
        session = requests.sessions.Session()
        if decoding:
            return session.get(self.url,headers=self.headers, stream=stream).content.decode('utf-8')
        return session.get(self.url,headers=self.headers, stream=stream)
    
    def get_requests(self, decoding=True, stream=False):
        import requests
        if decoding:
            return requests.get(self.url, headers=self.headers, stream=stream, timeout=10).content.decode('utf-8')
        else:
            if 'dropbox.com' in self.url:
                return requests.get(self.url, stream=stream, timeout=10)
            return requests.get(self.url, headers=self.headers, stream=stream, timeout=10)
    
    def get_length(self, response, meth = 'session'):
        try:
            if meth in ['session', 'requests']:
                return response.headers.get('content-length')
            elif meth=='urllib':
                return response.getheader('content-length')
        except KeyError:
            return None
    
    def download_build(self, name, zippath,meth='session', stream=True):
        if meth in 'session':
            response = self.get_session(decoding=False, stream=stream)
        elif meth in 'requests':
            response = self.get_requests(decoding=False, stream=stream)
        elif meth in 'urllib':
            response = self.get_urllib(decoding=False)
        
        length = self.get_length(response,meth=meth)
        if length is not None:
            length2 = int(int(length)/1000000)
        else:
            length2 = 'Unknown Size'
        dp = xbmcgui.DialogProgress()
        dp.create(name + ' - ' + str(length2) + ' MB', 'Downloading your build...')
        dp.update(0, 'Downloading your build...')
        cancelled = False
        tempzip = open(zippath, 'wb')
        if length:
            size = 0
            if meth in ['session', 'requests']:
                for chunk in response.iter_content(chunk_size=1000000):
                    size += len(chunk)
                    size2 = int(size/1000000)
                    tempzip.write(chunk)
                    perc = int(int(size)/int(length)*100)
                    dp.update(perc, 'Downloading your build...' + '\n' + str(size2) + '/' + str(length2) + 'MB')
                    if dp.iscanceled():
                        cancelled = True
                        break
            elif meth in 'urllib':
                blocksize = 1000000
                #blocksize = max(int(length)/512, 1000000)
                while True:
                    buf = response.read(blocksize)
                    if not buf:
                        break
                    size += len(buf)
                    size2 = int(size/1000000)
                    perc = int(int(size)/int(length)*100)
                    tempzip.write(buf)
                    dp.update(perc, 'Downloading your build...' + '\n' + str(size2) + '/' + str(length2) + 'MB')
                    if dp.iscanceled():
                        cancelled = True
                        break
                
        else:
            dp.update(50, 'Downloading your build...')
            blocksize = 1000000
            for chunk in response.iter_content(blocksize):
                if dp.iscanceled():
                    cancelled = True
                    break
                tempzip.write(chunk)
        if cancelled:
            xbmc.sleep(1000)
            os.unlink(zippath)
            dialog = xbmcgui.Dialog()
            dialog.ok('Cancelled', 'Download Cancelled')
            quit()
        if length:
            dp.update(100, 'Downloading your build...Done!' + '\n' + str(size2) + '/' + str(length2) + 'MB')
        else:
            dp.update(100, 'Downloading your build...Done!')
        tempzip.close()
    
    def download_zip(self, dest):
        r = self.get_requests(decoding=False, stream=True)
        with open(dest, "wb") as f:
              for ch in r.iter_content(chunk_size = 2391975):
                  if ch:
                      f.write(ch)
                      