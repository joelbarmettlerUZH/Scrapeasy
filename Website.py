from Page import Page, PageLINK, PageMedia

class Website(object):
    def __init__(self, url):
        self._domain = self.findDomain(url)
        self._mainPage = Page(url, self)
        self._subpages = []
        self._media = {}

    def __str__(self):
        return("Website object <"+self._domain+"> with "+str(len(self._subpages))+" Subpages yet.")

    def getDomain(self):
        return self._domain

    def getSubpages(self):
        return self._subpages

    @staticmethod
    def findDomain(url):
        url = url.replace("https://", "")
        url = url.replace("http://", "")
        url = url.replace("www.", "")
        if "/" in url:
            url = url[:url.index("/")]
        return url.lower()

    def findSubpages(self):
        i = 0
        while i < len(self._subpages):
            print(self._subpages[i])
            endings = [".jpg",".jpeg",".png",".tiff",".gif",".pdf",".svc",".ics",".docx", ".doc", ".mp4", ".mov", ".webm", ".zip", ".ogg"]
            skip = False
            for ending in endings:
                if self._subpages[i].getURL.lower().endswith(ending):
                    skip = True
                    break
            if not skip:
                new_links = self._subpages[i].getLinks()
                for link in new_links:
                    self._subpages.append(Page(link, self))
            i += 1