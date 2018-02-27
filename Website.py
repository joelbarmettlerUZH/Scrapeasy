from Page import Page


class Website(object):
    def __init__(self, url, verify=True):
        self._domain = self.findDomain(url)
        self._mainPage = Page(url, self)

        #Define empty subpages list and empty media dict
        self._subpages = []
        self._media = {}

        self._verify = verify

    def __str__(self):
        return("Website object <"+self._domain+"> with "+str(len(self._subpages))+" Subpages yet.")

    # Define getters for private variables
    def getDomain(self):
        return self._domain

    # If subpages are not yet found, find and return them
    def getSubpages(self):
        if not self._subpages:
            self.findSubpages()
        return self._subpages

    # Get links of each subpage
    def getSubpagesLinks(self):
        pages = self.getSubpages()
        links = []
        for page in pages:
            links.append(page.getURL())
        return links

    # Get list of all domains that are linked on the page
    def getDomainLinks(self):
        pages = self.getSubpages()
        links = []
        for page in pages:
            links += page.getLinks(intern=False, extern=False, domain=True)
        return list(set(links))

    # Find images on each subsite and return list of total image links
    def getImages(self, reinit=False):
        if (not self._subpages) or reinit:
            # print("Finding subpages")
            self.findSubpages()
        self._media["img"] = []
        for page in self._subpages:
            # print("Searching for Images: "+page.getURL())
            self._media["img"] += page.getImages()
        self._media["img"] = list(set(self._media["img"]))
        return self._media["img"]

    # Find videos on each subsite and return list of total video links
    def getVideo(self, reinit=False):
        if (not self._subpages) or reinit:
            self.findSubpages()
        self._media["video"] = []
        for page in self._subpages:
            # print("Searching for Videos on : " + page.getURL())
            self._media["video"] += page.getVideos()
        self._media["video"] = list(set(self._media["video"]))
        return self._media["video"]

    # Let the user get some specific file type from all subpages of the website
    def get(self, filetype, initialize=False):
        if (not self._subpages) or initialize:
            self.findSubpages()
        self._media[filetype] = []
        for page in self._subpages:
            # print("Searching for "+filetype+" on: " + page.getURL())
            self._media[filetype] += page.get(filetype)
        self._media[filetype] = list(set(self._media[filetype]))
        return self._media[filetype]

    # Staticmethod to extract a domain out of a normal link
    @staticmethod
    def findDomain(url):
        url = url.replace("https://", "")
        url = url.replace("http://", "")
        url = url.replace("www.", "")
        if "/" in url:
            url = url[:url.index("/")]
        return url.lower()

    # Offer downloading all datatypes to the disk into the provided folder
    def download(self, filetype, folder, reinit=False):
        if (not self._subpages) or reinit:
            self.findSubpages()
        for page in self.getSubpages():
            page.download(filetype, folder)

    # Find internal links of all subpages, starting from the provided main page
    def findSubpages(self):
        i = 0
        self._subpages = [Page(self._domain, verify=self._verify)]
        while i < len(self._subpages):
            # print("Finding subpage of: "+self._subpages[i].getURL())
            # Ignore these internal rinks when reached
            endings = [".jpg",".jpeg",".png",".tiff",".gif",".pdf",".svc",".ics",".docx", ".doc", ".mp4", ".mov", ".webm", ".zip", ".ogg"]
            skip = False
            for ending in endings:
                if self._subpages[i].getURL().lower().endswith(ending):
                    skip = True
                    break
            # If subsites links to the subpages (when not already in there)
            if not skip:
                new_links = self._subpages[i].getLinks(intern=True, extern=False)
                for link in new_links:
                    if link not in self.getSubpagesLinks():
                        self._subpages.append(Page(link, verify=self._verify))
            i += 1

# Testing
if __name__ == "__main__":
    web = Website("http://www.fahrschule-liechti.com")
    print("All pages: ",web.getSubpagesLinks())
    print("All Images: ",web.getImages())
    print("All Videos: ",web.getVideo())
    print("Linked Domains: ", web.getDomainLinks())
    print("Downloading all images")
    web.download("img","Fahrschule-Liechti/Images/")