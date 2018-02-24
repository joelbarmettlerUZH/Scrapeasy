import requests
from bs4 import BeautifulSoup
import validators
from OnlineData import OnlineData

# Basic webpage class that can scrape the html content of an URL
class abstractPage(object):
    def __init__(self, url, verify=True):

        if not validators.url(url):
            raise Exception("Not valid URL!")

        self._verify = verify
        self._domain = self.findDomain(url)
        self._url = url
        self._header = requests.head(self._url, verify=self._verify).headers

        self._headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:50.0) Gecko/20100101 Firefox/50.0'}
        self._html = None
        self.update()

        self._links = {"intern":[], "extern":[], "domain":[]}
        self.findLinks()

        self._media = {}

    def __str__(self):
        return "Page object <"+self._url+"> under the domain "+self._domain

    def getURL(self):
        return self._url

    def getHTML(self):
        return self._html

    def getDomain(self):
        return self._domain

    def getHeader(self):
        return self._header

    def getLinks(self, intern=True, extern=True):
        linklist = []
        if intern:
            linklist += self._links["intern"]
        if extern:
            linklist += self._links["extern"]
        return linklist

    @staticmethod
    def findDomain(url):
        url = url.replace("https://", "")
        url = url.replace("http://", "")
        url = url.replace("www.", "")
        if "/" in url:
            url = url[:url.index("/")]
        return url.lower()

    def update(self):
        self._html = requests.get(self._url, headers=self._headers, allow_redirects=True, verify=self._verify).text

    def findLinks(self):
        soup = BeautifulSoup(self._html, "lxml")
        links = soup.findAll("a")
        for link in links:
            link = str(link.get("href")).replace("../", "")
            if validators.url(link) and "mailto:" not in link:
                if self._domain in link.lower():
                    self.addInternal(self._domain + link[link.lower().index(self._domain)+len(self._domain):])
                else:
                    self.addExternal((link.replace("https://", "").replace("http://","").replace("www.","")))
            else:
                if validators.url("http://www."+self._domain+"/"+link) and "mailto:" not in link:
                    self.addInternal((self._domain + "/" + link))

    def add(self, list, link):
        link = link.replace("https://","").replace("http://","").replace("www.","").replace("//", "/")
        if link[-1] == "/":
            link = link[:-1]
        if "#" in link:
            link = link[:link.index("#")]
        if link not in list:
            list.append(link)

    def addInternal(self, link):
        self.add(self._links["intern"], link)

    def addExternal(self, link):
        self.add(self._links["extern"], link)
        self.add(self._links["domain"], self.findDomain(link))

    def download(self, filetype, folder):
        for link in self._media[filetype]:
            data = OnlineData(link)
            data.download(folder)

    def filterFiles(self, endlist):
        links = []
        for ending in endlist:
            ending = ending.lower()
            if not ending.startswith("."):
                ending = "."+ending
        for link in self._links["intern"]+self._links["extern"]:
            for ending in endlist:
                if link.lower().endswith(ending):
                    links.append(link)
        return links


# Subclass of Webpage that can also find images in the html content
class PageMedia(abstractPage):

    def __init__(self, url,verify=True):
        abstractPage.__init__(self, url, verify)

    def updateImages(self):
        data = ["jpg","jpeg","png","tiff","svg","webm","gif", ".ico"]
        links = self.findSrc("img")
        new = self.filterFiles(data)
        for link in new:
            if link not in links:
                links.append(link)
        self._media["img"] = links

    def updateVideos(self):
        data = ["avi", "mp4", "mpeg4", "asf", "mov", "qt", "flv", "swf", "wmv"]
        links = self.findSrc("video")
        new = self.filterFiles(data)
        for link in new:
            if link not in links:
                links.append(link)
        self._media["video"] = links

    def getImages(self):
        if not "img" in self._media.keys() or self._media["img"] == None:
            self.updateImages()
        return self._media["img"]

    def getVideos(self):
        if not "video" in self._media.keys() or self._media["video"] == None:
            self.updateVideos()
        return self._media["video"]

    def get(self, filetype, ending=None):
        if ending == None:
            return self._media[filetype]
        if not filetype in self._media.keys() or self._media[filetype] == None:
            self._media[filetype] = self.filterFiles(ending)
        return self._media[filetype]

    def findSrc(self, tag):
        links = []
        soup = BeautifulSoup(self._html, "html.parser")
        for link in soup.find_all(tag):
            img_url = str(link.get("src")).lower()
            if not self._domain in img_url:
                if img_url[0] == "/":
                    self.add(links, self._url + img_url)
                elif validators.url(img_url):
                    self.add(links, img_url)
                else:
                    self.add(links, self._url + "/" + img_url)
            else:
                self.add(links, img_url)
        return links



class Page(PageMedia):
    def __init__(self, url, verify=True):
        PageMedia.__init__(self, url, verify=True)

if __name__=="__main__":
    p = Page("https://www.w3schools.com/html/html5_video.asp", verify=True)
    print("Images:", p.getImages())
    print("Links:", p.getLinks(intern=True, extern=True))
    print("Videos:", p.getVideos())
    print("HTML:", p.get("html", [".html"]))


