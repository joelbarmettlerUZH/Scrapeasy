import requests
from bs4 import BeautifulSoup
import validators
import time
from scrapeasy.WebData import OnlineData

#Abstract page class with base functionality
class abstractPage(object):
    def __init__(self, url, verify=True):

        # Define verify behaviour and extract domain from url
        self._verify = verify
        url = url.replace("%2F", "/")
        self._domain = self.findDomain(url)

        # Normalize URL to not contain anything before the domain / subdomain
        try:
            self._url = url[url.index(self._domain):]
        except ValueError as ve:
            self._url = url
        if not validators.url("http://"+self._url):
            raise ValueError("Not valid URL: "+url+"!")

        # Try getting the header via http request.head
        try:
            self._header = requests.head("http://www."+self._url, verify=self._verify).headers
        except requests.exceptions.ConnectionError as ce:
            self._header = "Unknown"

        # Add scrapers headers to identify python scraper on websites
        self._headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:50.0) Gecko/20100101 Firefox/50.0'}
        self._html = None
        self.update()

        # Categorize links into intern - extern and domain
        self._links = {"intern":[], "extern":[], "domain":[]}
        self.findLinks()

        # Empty dict in which media will be inserted
        self._media = {}

    def __str__(self):
        return self._url

    # Getters for private Page content
    def getURL(self):
        return self._url

    def getHTML(self):
        return self._html

    def getDomain(self):
        return self._domain

    def getHeader(self):
        return self._header

    # Return links according to type parameter
    def getLinks(self, intern=True, extern=True, domain=False):
        linklist = []
        if intern:
            linklist += self._links["intern"]
        if extern:
            linklist += self._links["extern"]
        if domain:
            linklist += self._links["domain"]
        return linklist

    # Extracts url out of a domain according to the first backslash occurence that marks the start of the path
    @staticmethod
    def findDomain(url):
        url = url.replace("https://", "")
        url = url.replace("http://", "")
        url = url.replace("www.", "")
        if "/" in url:
            url = url[:url.index("/")]
        return url.lower()

    # Folder is the part of a url without the file, so without the part after the last backslash
    @staticmethod
    def findFolder(url):
        return url[:url.rindex("/")]

    @staticmethod
    def normalize(string):
        return string.replace("https://", "").replace("http://","").replace("www.","")

    # Try scraping the site. If it does not work out, wait some time and try again
    def update(self, tries=5):
        try:
            self._html = requests.get("http://www."+self._url, headers=self._headers, allow_redirects=True, verify=self._verify).text
        except requests.exceptions.ConnectionError as ce:
            if tries > 0:
                time.sleep(1)
                self.update(tries=tries-1)

    # Exctract links from all urls that do not define some well-known filetypes that for sure do not contain any html text (unless .txt or .md could, in theory, contain such links)
    def findLinks(self):
        # print("Finding links of "+self._url)
        # Defined filetypes that are to ignore
        endings = [".jpg", ".jpeg", ".png", ".tiff", ".gif", ".pdf", ".svc", ".ics", ".docx", ".doc", ".mp4", ".mov",
                   ".webm", ".zip", ".ogg"]
        for end in endings:
            if self._url.lower().endswith(end):
                return

        # Parse request as lxml and extract a-tags
        soup = BeautifulSoup(self._html, "lxml")
        links = soup.findAll("a")
        for link in links:
            # Filter out the href link
            link = str(link.get("href")).replace("../", "")
            # Break when the link is None or consists of some javascript that could not be read out
            if link == "None" or "JavaScript:" in link:
                break
            # Categorize link according to its form
            if validators.url(link) and "mailto:" not in link:
                if self._domain in link.lower():
                    self.addInternal(self._domain + link[link.lower().index(self._domain)+len(self._domain):])
                else:
                    self.addExternal((Page.normalize(link)))
            else:
                if validators.url("http://www."+self._domain+"/"+link) and "mailto:" not in link:
                    self.addInternal((self._domain + "/" + link))

    # Add a link to the appropriate list with removing everything before the domain first
    def add(self, list, link):
        link = Page.normalize(link)
        if link[-1] == "/":
            link = link[:-1]
        if "#" in link:
            link = link[:link.index("#")]
        if link not in list:
            list.append(link)

    # Add link to internal links
    def addInternal(self, link):
        self.add(self._links["intern"], link)

    # Add link to external links
    def addExternal(self, link):
        self.add(self._links["extern"], link)
        self.add(self._links["domain"], self.findDomain(link))

    # Filter all internal and external links to certain file endings and returns them
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


# Pagemedie extends the abstract page with media scraping support
class PageMedia(abstractPage):

    def __init__(self, url,verify=True):
        abstractPage.__init__(self, url, verify)

    # Find all images in a page by filtering its links and finding img src tags
    def updateImages(self):
        data = ["jpg","jpeg","png","tiff","svg","webm","gif", ".ico"]
        links = self.findSrc("img")
        new = self.filterFiles(data)
        for link in new:
            if link not in links:
                links.append(link)
        self._media["img"] = links

    # Find all videos in a page by filtering its links and finding video src tags
    def updateVideos(self):
        data = ["avi", "mp4", "mpeg4", "asf", "mov", "qt", "flv", "swf", "wmv"]
        links = self.findSrc("video", "source")
        new = self.filterFiles(data)
        for link in new:
            if link not in links:
                links.append(link)
        self._media["video"] = links

    # Return list of all image links
    def getImages(self):
        if not "img" in self._media.keys() or self._media["img"] == None:
            self.updateImages()
        return self._media["img"]

    # Return list of all video links
    def getVideos(self):
        if not "video" in self._media.keys() or self._media["video"] == None:
            self.updateVideos()
        return self._media["video"]

    # Filter for some specific file types in all links and return the list of all these links
    def get(self, filetype):
        self._media[filetype] = self.filterFiles([filetype])
        return self._media[filetype]

    # Download a file to specified folder
    def download(self, filetype, folder):
        if filetype not in self._media.keys():
            self.get(filetype)
        for link in self._media[filetype]:
            data = OnlineData(link)
            data.download(folder)

    # Find some source that is nested in *tags, like tags("video"->"source"), then "src"!
    def findSrc(self, *tags):
        links = []
        # Sometimes strange Not-implemented error occurs
        try:
            soup = BeautifulSoup(self._html, "html.parser")
        except NotImplementedError as nie:
            print("Not implemented error occurred!")
            print(nie.args)
            return []
        # Filter as long as there are tags left, in the right order
        filter = soup.find_all(tags[0])
        tags = tags[1:]
        for t in range(len(tags)):
            filter_new = []
            for f in range(len(filter)):
                filter_new += filter[f].find_all(tags[t])
            filter = filter_new.copy()
        #Find source in tag and add link according to its structure
        for link in filter:
            img_url = str(link.get("src")).lower()
            if not self._domain in img_url:
                if img_url[0] == "/":
                    self.add(links, self.findFolder(self._url) + img_url)
                elif validators.url(img_url):
                    self.add(links, img_url)
                else:
                    self.add(links, self.findFolder(self._url) + "/" + img_url)
            else:
                self.add(links, img_url)
        return links


# Pagemedia is the version of Page that is always including all functionality, multi-inheritence will be used here later on
class Page(PageMedia):
    def __init__(self, url, verify=True):
        PageMedia.__init__(self, url, verify=True)

# Testing
if __name__=="__main__":
    web = Page("http://mathcourses.ch/mat182.html")
    print(web)
    #web.download("pdf", "mathcourses/pdf-files")


