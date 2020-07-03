# Scrapeasy - The simplest Python scraper out there!

With Scrapeasy, you can scarpe websites with python with just one line of code. Scrapeasy is super easy to use and handles everything for you. Just specify what website you want to scrape and what media you want to receive back, and the rest is done for you.

# Overview
The Scrapeasy Python scraper was written with fast use in mind. It provides the following key features

  - Scrape Websites - not just single pages - all with one click.
  - The most common scrape activities (receive Links, Images or Videos) are already implemented
  - Receive special file types like .php or .pdf datas from the scraped website


## Usage

In the following paragraphs, I am going to describe how you can get and use Scrapeasy for your own projects.

###  Getting it

To download scrapeasy, either fork this github repo or simply use Pypi via pip.
```sh
$ pip install scrapeasy
```

### Using it

Scrapeasy was programmed with ease-of-use in mind. First, import Website and Page from Scrapeasy

```Python
from scrapeasy import Website, Page
```

And you are ready to go! At this point, I want to clearly distinct between a Website and a Page. While a Page is defined by just one single  url, like [github.com/joelbarmettlerUZH/Scrapeasy](https://github.com/joelbarmettlerUZH/Scrapeasy), a Website is a collection of such sites that belong to the same Domain. So the Website would be github as a whole, with all its pages - one of them is the scrapeasy repo. So a Website consists of many webpages. 

## Website and Page
As will notice that you can use all the methods for both *Page* and *Website* with the same argument calls. The only difference is that *Page* only gets you results from the specified URL while *Website* gives you results about the whole webpage with all its subsites. But let's have a look at the examples to make it clear:

## Initialize a Website
First, let's create a new Website object. For this manner, just provide the url of the main page. I will use the URL of a website that I created years ago: [fahrschule-liechti.com](http://www.fahrschule-liechti.com). 

```Python
web = Website("http://www.fahrschule-liechti.com/")
```

#### Get Links of all subsites 
Okay, now that we have our Website initialized, we are interested of all the subsites that exists on fahrschule-liechti.com. To find this out, ask the web-object to receive the links of all subpages.

```Python
links = web.getSubpagesLinks()
```

Depending on your local internet connection and the server speed of the domain you are scraping, this request may take a while. Make sure to not scrape whole webpages with this method that are incredibly huge - like github.com for example. Github includes tousands if not billions of pages and links, and to digg through all of them may take hours. You can give it a shot - but use the page-scraping method described later to scrape such big sites. 

But back to the link-getting: By calling *.getSubpagesLinks()*, you request all subpages as links and will receive a list of urls. 

>['fahrschule-liechti.com', 'fahrschule-liechti.com/about', 'fahrschule-liechti.com/der-weg-motorrad' .... ]

You may have noticed that the typical [*http://www.*](#)-stuff is missing. Thats un purpose and makes your live easier to further work with the links. But make sure that - when you actually want to call them in your browser or via requests - you add the http://www. in front of every link. 

#### Find media
Let's try to find links to all images that fahrschule-liechti.com placed on its website. We do that by calling the *.getImages()* method.

```Python
images = web.getImages()
```

The response will include links to all available images. 

>['fahrschule-liechti.com/wp-content/themes/zerif-lite/images/map25-redish.png', 'fahrschule-liechti.com/wp-content/uploads/2016/01/fabi-kreis.png' .... ]

#### Download media
Cool! Now let's do some more advanced stuff. We love the pictures that fahrschule-liechti.com has on its website, so let's download them all to our local disk. Sounds like a lot of work? Its actually deadly easy!

```Python
web.download("img", "fahrschule/images")
```

First, we defined to download all image-media via the keyword *img*. Next, we define the output folder, where the images should be saved to. Thats it! Run the Code and see whats happening. Within seconds, you have received all images there are on fahrschule-liechti.com. 

#### Get linked domains
Next, lets find out to what pages fahrschule-liechti.com is linking to. To get a general overview, let's just find out to what other domains it is linking to. For that reason, we specify to only get the domain-links.

```Python
domains = web.getLinks(intern=False, extern=False, domain=True)
```

What we get back is a list of all domains that are somewhere linked on fahrschule-liechti.com
>['orthotec.ch', 'wordpress.org', 'strassenverkehrsamt.lu.ch', 'themeisle.com', 'google.ch', 'astra.admin.ch', 'samariter-luzern.ch']

All right, but now we want to gain further insights on these links. How do we do that?

#### Get linked domains
Well, more detailed links are nothing more than external links. So we do the same request but this time including externals, but not domains. 

```Python
domains = web.getLinks(intern=False, extern=True, domain=False)
```

Tadaa, we are getting all external links in full detail.

>['samariter-luzern.ch/cms/front_content.php', 'themeisle.com/themes/zerif-lite', 'orthotec.ch/de/pub/otc/fahrzeugumbau/fahrschulen.htm' ... ]

## Initialize a Page
Okay, by now we have seen quiet a bit about that Website-thing, but we have not discovered what Page does yet. Well, as said, page is just a single Site from a Website. Let's try it out on a different example by initializing a w3 schools page.

```Python
w3 = Page("https://www.w3schools.com/html/html5_video.asp")
```

You will see why I chose exactly this page in a second, if you have not already guessed.

#### Downloading Videos 
Yes, you have heard right. Scrapeasy lets you download videos from webpages in seconds. Let's have a look how.

```Python
w3.download("video", "w3/videos")
```

Yep, thats all. Just specify that you want to download all video media into the output folder w3/videos, and you are ready to go. Of course you could also just receive the link to the videos and download them later, but that would be less cool.

```Python
video_links = w3.getVideos()
```

#### Dowload other file types (like *pdf*  or *ics*)
Let's be more general now. What about downloading special file types, like .pdf, .php or .ico? Use the general *.get()* method to receive the links, or the *.download()* method with the filetype as an argument.
Lets use the get method to receive reiceive links to calendar data on the computer-science club of the university of Zurich, UZH:

```Python
calendar_links = Page("https://www.icu.uzh.ch/events/id/207").get("ics")
```
Done.

>['icu.uzh.ch//events/upcoming/icu-upcoming-events.ics', 'icu.uzh.ch//events/id/207/icu-event.ics']

Let's Downlaod some PDF's now. We should already be experienced on how to use *.download()*, but I demonstrate it one last time.

```Python
Page("http://mathcourses.ch/mat182.html").download("pdf", "mathcourses/pdf-files")
```



License
----

MIT License

Copyright (c) 2018 Joel Barmettler

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.


Hire us: [Software Entwickler in Zürich](https://polygon-software.ch)!

