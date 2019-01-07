import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
import cPickle as pickle
import re
from bs4 import BeautifulSoup
import numpy as np
from numpy import ma
import time
from keras.models import model_from_json
import string

import nltk
import scipy
import json 

def convertSet(dset):
	ndset = []
	for s in dset:
		ndset.append(article_to_wordlist(s))
	return ndset

def _removeNonAscii(s): 
	fixed = []
	for x in s:
		fixed.append("".join(i for i in x if ord(i)<128))
	return fixed

def setUpVec():
	with open('clsfyModel.json', 'r') as f:
		model = model_from_json(f.read())
	model.load_weights('modelfinal.h5')


	with open("processing/measure_articles.pkl",'rb') as fp:
		measure_raw = pickle.load(fp)

	with open("processing/tmp_articles.pkl",'rb') as fp:
		tmp_raw = pickle.load(fp)


	tmp_raw = _removeNonAscii(tmp_raw)
	measure_raw = _removeNonAscii(measure_raw)

	tmp_words = convertSet(tmp_raw)
	measure_words = convertSet(measure_raw)

	baggableArticles = []
	

	totalData = tmp_words + measure_words
	totalRaw = tmp_raw+measure_raw

	for article in totalData:
		baggableArticles.append(" ".join(article))
	vectorizer = CountVectorizer(analyzer = "word",   \
		                         tokenizer = None,    \
		                         preprocessor = None, \
		                         stop_words = None,   \
		                        )
	s = vectorizer.fit_transform(baggableArticles)
	print "Figuring it out!"


	return vectorizer, model
	
def fitWordArticle(article, vec):
	return vec.transform(article_to_wordlist(article)).toarray()

def createGrammarDictionary(dset):
	grammarArticles = []
	punctuation = list(string.punctuation)
	for article in dset:	
		holder = np.zeros(len(punctuation))
		for sType in punctuation:
			holder[punctuation.index(sType)] += article.count(sType)
		grammarArticles.append(holder)
	return grammarArticles

def article_to_wordlist(article, remove_stopwords=False):
    article_text = BeautifulSoup(article).get_text()
    article_text = re.sub("[^a-zA-Z]"," ", article_text)
    words = article_text.lower().split()
    if remove_stopwords:
        stops = set(stopwords.words("english"))
        words = [w for w in words if not w in stops]
    return(words)