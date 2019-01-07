import numpy as np
import time
import nltk
import scipy
import string
from Article import *
from collections import deque
import cPickle as pickle

from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from io import BytesIO

from os import listdir
from os.path import isfile, join


def pullTMPPaths():
	mypath = "/Users/alexrodriguez/Desktop/Programming_4/PaperMeasure/TMP"
	onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]
	paths = []
	for f in onlyfiles:
	    paths.append(mypath+"/"+f)

	correctedPaths = []
	for p in paths:
		if ".pdf" in p:
			correctedPaths.append(p)
	paths = correctedPaths

	for p in paths:
		print p
	return paths

def convert_pdf_to_txt(path):
    rsrcmgr = PDFResourceManager()
    retstr = BytesIO()
    codec = 'utf-8'
    laparams = LAParams()
    device = TextConverter(rsrcmgr, retstr, codec=codec, laparams=laparams)
    fp = open(path, 'rb')
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    password = ""
    maxpages = 0
    caching = True
    pagenos=set()

    for page in PDFPage.get_pages(fp, pagenos, maxpages=maxpages, password=password,caching=caching, check_extractable=True):
        interpreter.process_page(page)

    text = retstr.getvalue()

    fp.close()
    device.close()
    retstr.close()
    return text

def numberPuller(string):
	hitLetters = False
	numString = ""
	for ch in string:
		if ch.isdigit() and hitLetters == False:
			numString+=ch
		else:
			hitLetters = True
	try:
		return int(numString)
	except:
		return 0

def fallBackNameChecker(s):
	if len(s)>25:
		split = s[:25].strip().split(" ")
	else:
		split = s.strip().split(" ")
	cutBack = []
	for x in split:
		if x != "":
			cutBack.append(x)
	if len(cutBack) < 4:
		return False
	try:
		if (cutBack[1][0].isupper() and cutBack[2][0].isupper()):
			return True
		else:
			return False
	except:
		return False

def chopLeadingNumbers(string):
	finalString = ""
	hitLetters = False
	for c in string:
		if hitLetters:
			finalString+=c
		if c.isdigit():
			hitLetters = True

	return finalString


def convertIssueTMP(issueRawText):
	numOfArticles = 0

	splitString = issueRawText.split("\n\n")
	spacesCut = []
	for s in splitString:
		if s != " ":
			spacesCut.append(s)


	starterIndexes = []
	for s in spacesCut:
		if len(s) > 25:
			if "By" in s[:25]:
				# print s[:25]
				if float(len([letter for letter in s[:25] if letter.isupper()]))/float(len(s[:25])) > 0.3 or fallBackNameChecker(s):
					starterIndexes.append(spacesCut.index(s)+1)
					numOfArticles+=1
		elif "By" in s:
			# print s
			if float(len([letter for letter in s if letter.isupper()]))/float(len(s)) > 0.3 or fallBackNameChecker(s):
				starterIndexes.append(spacesCut.index(s)+1)
				numOfArticles+=1

	endIndexes = []
	for s in spacesCut:
		if "\xe2\x80\xa2" in s:
			endIndexes.append(spacesCut.index(s))
		if "CONTINUED ON" in s:
			endIndexes.append(spacesCut.index(s))

	cleanedArticles = []
	article = ""
	recordingArticle = False
	startedFromBy = False
	continuingWatch = False
	pageNum = 1
	continueIndex = 0
 
	for s in spacesCut:
		printable = set(string.printable)
		if "CONTINUED FROM PAGE " in s:
			continuingWatch = True
			continueIndex = int(numberPuller(s.split("CONTINUED FROM PAGE ")[-1]))
			print "CONTINUE INDEX UPDATED TO"
			print continueIndex
		if len(filter(lambda x: x in printable, s)) < 10 and "PAGE" in filter(lambda x: x in printable, s):
			# print "PAGE FOUND!!!" 
			# print filter(lambda x: x in printable, s)
			pageNum = filter(lambda x: x in printable, s).split("PAGE ")[-1]
			print "Updating page number to "
			print pageNum
			splitA = article.split(" ")
			splitA[0] = str(pageNum)
			article = " ".join(splitA)

		if spacesCut.index(s) in starterIndexes:
			article = str(pageNum)+" "
			recordingArticle = True
			startedFromBy = True

		if recordingArticle:
			if len(s) > 50:
				article += s
			elif "CONTINUED" in s:
				article += s

		if spacesCut.index(s) in endIndexes:
			# This method relies on the fact that no two articles are continued on the same page!
			if len(article) > 4:
				if startedFromBy:
					newArticle = Article(pageNum)
					newArticle.articlePieces.append(article)
					if "CONTINUED ON PAGE " in article:
						# print "Found an incomplete article"
						newArticle.completed = False
						newArticle.continuePage = int(numberPuller(article.split("CONTINUED ON PAGE ")[-1]))
					else:
						newArticle.completed = True
					cleanedArticles.append(newArticle)
				elif continuingWatch == True:
					continuingWatch = False
					# print "Continuing an article piece"
					for ar in cleanedArticles:
						if ar.completed == False:
							if ar.continuePage == int(article.split(" ")[0]):
								if int(continueIndex) == int(ar.originalPage):
									print "MATCHED UP!"
									ar.articlePieces.append(article)
									ar.completed = True
									break
								else:
									print "DIDNT MATCH UP"
									print article
									print continueIndex
									print ar.originalPage
							# else:
								# print "PRoblem:"
								# print int(article.split(" ")[0])
								# print article

				article = str(pageNum)+" "

			else:
				recordingArticle = False
			startedFromBy = False



	# for s in spacesCut:
	# 	if spacesCut.index(s) in starterIndexes:
	# 		print "************************************************"
	# 	else:
	# 		print "------------------------------------------------"
	# 	print s
	# 	if spacesCut.index(s) in endIndexes:
	# 		print "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
	# 	else:
	# 		print "------------------------------------------------" 
	# 	print "\n"

	# for p in cleanedArticles[1].articlePieces:
	# 	print p
	# 	print "------------------------------------------------" 


	finishedArticles = []
	for a in cleanedArticles:
		if len(a.articlePieces) > 1:
			finished1 = a.articlePieces[0].split("CONTINUED ON PAGE")[0]
			if "CONTINUED FROM" in a.articlePieces[1]:
				finished2 = a.articlePieces[1].split("CONTINUED FROM PAGE ")[1]
			else: 
				finished2 = a.articlePieces[1]
			finishedArticles.append(chopLeadingNumbers(finished1)+chopLeadingNumbers(finished2))
		else:
			finishedArticles.append(a.articlePieces[0])


	return finishedArticles

# For converting all of the TMPS:
paths = pullTMPPaths()
allIssues = []
for path in paths:
	allIssues += convertIssue(convert_pdf_to_txt(path))

with open("tmp_articles.pkl",'wb') as fp:
    pickle.dump(allIssues,fp)

