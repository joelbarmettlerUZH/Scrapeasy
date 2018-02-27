import requests
import shutil
import os

# Class representing an online Image with an url and a name
class OnlineData(object):
    def __init__(self, url):
        self._url = url
        self._name = self.findName()
        self._headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:50.0) Gecko/20100101 Firefox/50.0'}

    def __str__(self):
        return "Name: {}. Url: {}".format(self._name, self._url)

    # find name as the string part behind the last backslash
    def findName(self):
        if "/" in self._url:
            last_slash = self._url.rfind("/")
            return self._url[last_slash+1:]
        return self._url

    # download an image to thep rovided folder
    def download(self, folder):
        try:
            img = requests.get("http://www."+self._url, headers=self._headers, stream=True, allow_redirects=True)
            if not os.path.exists(folder):
                os.makedirs(folder)
            if folder and not folder[:-1] == "/":
                folder = folder + "/"
            with open(folder + self._name, "wb") as file:
                # print("Downloading {}".format(self._name))
                shutil.copyfileobj(img.raw, file)
        except:
            print("Invalid URL: {}".format(self._url))