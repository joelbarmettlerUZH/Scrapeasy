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
        self._html_content = None

    def __str__(self):
        return self._html_content

    def update_html_content(self):
        print("Scraping HTML content for {}".format(self._url))
        self._html_content = requests.get(self._url).text


# Subclass of Webpage that can also find images in the html content
class Images_Webpage(Webpage):

    _total_images = 0

    def __init__(self, url):
        Webpage.__init__(self, url)
        self._images_list = []

    def find_images(self):
        print("Scraping images for {}".format(self._url))
        self.update_html_content()
        # Find all img tags and get the src link in the html content
        soup = BeautifulSoup(self._html_content, "html.parser")
        for link in soup.find_all("img"):
            img_url = link.get("src")
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



# Class representing an online Image with an url and a name
class Online_Image(object):
    def __init__(self, url):
        self._url = url
        self._name = self.find_name()

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
            img = requests.get(self._url, stream=True)
            if not os.path.exists(folder):
                os.makedirs(folder)
            with open(folder + self._name, "wb") as file:
                print("Downloading {}".format(self._name))
                shutil.copyfileobj(img.raw, file)
        except:
            print("can not download image - invalid image url: {}".format(self._url))

#testing the class 
if __name__ == "__main__":
    travelblog = Images_Webpage("https://www.justtravelous.com/")
    travelblog.find_images()
    travelblog.download_all_images("./travelblog/")
    print("*******")
    print("Total number of downloaded images: {}#".format(Images_Webpage.total_images_found()))
