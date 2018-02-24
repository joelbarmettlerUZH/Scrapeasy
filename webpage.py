import requests
from bs4 import BeautifulSoup
import shutil
import os
import validators

# Basic webpage class that can scrape the html content of an URL
class Webpage(object):
    def __init__(self, url):
        if not validators.url(url):
            raise Exception("Not valid URL!")
        self._url = url
        self._headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:50.0) Gecko/20100101 Firefox/50.0'}
        self._domain = self.findDomain(self._url)
        self._html = None
        self.update()
        self._header = requests.head(self._url).headers

    def __str__(self):
        return self._html

    @staticmethod
    def findDomain(url):
        url = url.replace("https://", "")
        url = url.replace("http://", "")
        url = url.replace("www.", "")
        if "/" in url:
            url = url[:url.index("/")]
        return url.lower()

    def getHTML(self):
        return self._html

    def getDomain(self):
        return self._domain

    def getURL(self):
        return self._url

    def getHeader(self):
        return self._header

    def update(self):
        print("Scraping HTML content for {}".format(self._url))
        self._html = requests.get(self._url, headers=self._headers).text


# Subclass of Webpage that can also find images in the html content
class ImagesWebpage(Webpage):

    _total_images = 0

    def __init__(self, url):
        Webpage.__init__(self, url)
        self._images_list = []

    def find_images(self):
        print("Scraping images for {}".format(self._url))
        # Find all img tags and get the src link in the html content
        soup = BeautifulSoup(self._html, "lxml")
        for link in soup.find_all("img"):
            img_url = str(link.get("src")).lower()
            if not self._url in img_url:
                if img_url[0] == "/":
                    img_url = self._url + img_url
                else:
                    img_url = self._url + "/" + img_url
            if validators.url(img_url):
                # add new image to list as Online_Image objects and increase class counter
                print("Found new valid Link: {}".format(img_url))
                self._images_list.append(Online_Image(img_url))
                __class__._total_images += 1

    # static method to receive static class variable
    @staticmethod
    def total_images_found():
        return(__class__._total_images)

    # receive back a list of all image links
    def get_images(self):
        return self._images_list

    # Download all images
    def download_all_images(self, folder):
        for img in self._images_list:
            img.download(folder)


class LinkWebpage(Webpage):
    def __init__(self, url):
        Webpage.__init__(self, url)
        self._internal_links = [self._domain]
        self._external_links = []

    def findAllLinks(self):
        i = 0
        while(i < len(self._internal_links)):
            print(self._internal_links[i])
            self.findLinks(self._internal_links[i])
            i += 1


    def addInternal(self, link):
        self.add(self._internal_links, link)

    def addExternal(self, link):
        self.add(self._external_links, link)

    def add(self, list, link):
        link = link.replace("//", "/")
        if link[-1] == "/":
            link = link[:-1]
        if "#" in link:
            link = link[:link.index("#")]
        if link not in list:
            list.append(link)

    def getInternals(self):
        return self._internal_links

    def getExternals(self):
        return self._external_links

    def findLinks(self, url):
        html = requests.get("http://"+url, headers=self._headers).text
        soup = BeautifulSoup(html, "lxml")
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


class ScrapePage(LinkWebpage, ImagesWebpage):
    def __init__(self, url):
        ImagesWebpage.__init__(self, url)
        LinkWebpage.__init__(self, url)




# Class representing an online Image with an url and a name
class Online_Image(object):
    def __init__(self, url):
        self._url = url
        self._name = self.find_name()
        self._headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:50.0) Gecko/20100101 Firefox/50.0'}

    def __str__(self):
        return "Name: {}. Url: {}".format(self._name, self._url)

    # find name as the string part behind the last backslash
    def find_name(self):
        if "/" in self._url:
            last_slash = self._url.rfind("/")
            return self._url[last_slash+1:]
        return self._url

    # download an image to thep rovided folder
    def download(self, folder):
        try:
            img = requests.get(self._url, headers=self._headers, stream=True)
            if not os.path.exists(folder):
                os.makedirs(folder)
            with open(folder + self._name, "wb") as file:
                print("Downloading {}".format(self._name))
                shutil.copyfileobj(img.raw, file)
        except:
            print("can not download image - invalid image url: {}".format(self._url))

#testing the class 
if __name__ == "__main__":
    web = ScrapePage("http://www.my3dworld.ch/")
    print(web.getHeader())
    web.find_images()
    print(web.getExternals())
    print(web.getInternals())
    # Webpage.getDomain("https://www.google.ch/home/lol.jpg")
    # travelblog = ImagesWebpage("https://www.justtravelous.com/")
    # travelblog.find_images()
    # travelblog.download_all_images("./travelblog/")
    # print("*******")
    # print("Total number of downloaded images: {}#".format(Images_Webpage.total_images_found()))
