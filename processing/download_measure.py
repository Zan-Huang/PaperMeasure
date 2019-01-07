from subprocess import call
from HTMLParser import HTMLParser
import urllib
import re
import cPickle as pickle

class MLStripper(HTMLParser):
    def __init__(self):
        self.reset()
        self.fed = []
    def handle_data(self, d):
        self.fed.append(d)
    def get_data(self):
        return ''.join(self.fed)

def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()

def pullAllLinks():
	blankSearch = "http://www.miltonmeasure.org/site/page/" 
	bsEnd = "/?s="

	entryString = '<h3 class="entry-title"><a href="'
	endString = '" rel="bookmark'

	totalPages = 65
	allLinks = []

	for i in range(totalPages+1):
		pageNum = i+1
		blankLink = blankSearch+str(pageNum)+bsEnd
		f = urllib.urlopen(blankLink)
		mainBody = f.read()

		for match in re.finditer(entryString, mainBody):
		    testingString = mainBody[match.end():]
		    link = testingString[:testingString.find(endString)]
		    allLinks.append(link)

	for l in allLinks:
		print "Link: " + l

	with open("measure_links",'wb') as fp:
	    pickle.dump(allLinks,fp)

def loadLinks():
	with open("measure_links",'rb') as fp:
		return pickle.load(fp)

def pullArticleText(link):
	f = urllib.urlopen(link)
	body = f.read()
	article = ""
	start = '<p class="p' 
	# continues to be (number)"> so add 3
	end = "</p>"

	for match in re.finditer(start, body):
		tester = body[match.end()+3:]
		content = tester[:tester.find(end)]
		content = strip_tags(content)
		article += content
	return article

def pullAllArticles(links):
	totalNumArticles = float(len(links))
	completed = 0.0
	cleanedArticles = []
	for link in links:
		article = pullArticleText(link)
		if len(article) > 100:
			cleanedArticles.append(article)
		completed += 1.0
		print "Progress: " + str(completed/totalNumArticles*100) + "%"
	return cleanedArticles

if __name__ == '__main__':
	# pullAllLinks()
	cleanedArticles = pullAllArticles(loadLinks())
	with open("measure_articles.pkl",'wb') as fp:
	    pickle.dump(cleanedArticles,fp)







