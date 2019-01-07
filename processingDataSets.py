import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
import cPickle as pickle
import re
from bs4 import BeautifulSoup
import numpy as np
from numpy import ma
import time
import string

import nltk
import scipy

with open("processing/measure_articles.pkl",'rb') as fp:
	measure_raw = pickle.load(fp)

with open("processing/tmp_articles.pkl",'rb') as fp:
	tmp_raw = pickle.load(fp)

def _removeNonAscii(s): 
	fixed = []
	for x in s:
		fixed.append("".join(i for i in x if ord(i)<128))
	return fixed

tmp_raw = _removeNonAscii(tmp_raw)
measure_raw = _removeNonAscii(measure_raw)

def article_to_wordlist(article, remove_stopwords=False):
    article_text = BeautifulSoup(article).get_text()
    article_text = re.sub("[^a-zA-Z]"," ", article_text)
    words = article_text.lower().split()
    if remove_stopwords:
        stops = set(stopwords.words("english"))
        words = [w for w in words if not w in stops]
    return(words)

def convertSet(dset):
	ndset = []
	for s in dset:
		ndset.append(article_to_wordlist(s))
	return ndset


tmp_words = convertSet(tmp_raw)
measure_words = convertSet(measure_raw)
outPut = np.concatenate((np.full((len(tmp_raw),2), [1,0]), np.full((len(measure_raw),2), [0,1])), axis=0)



totalData = tmp_words + measure_words
totalRaw = tmp_raw+measure_raw

def createWordDictionary(dset):
	baggableArticles = []
	for article in dset:
	    baggableArticles.append(" ".join(article))
	vectorizer = CountVectorizer(analyzer = "word",   \
	                             tokenizer = None,    \
	                             preprocessor = None, \
	                             stop_words = None,   \
	                             )
	train_data_features = vectorizer.fit_transform(baggableArticles)
	train_data_features = train_data_features.toarray()
	return train_data_features

def createGrammarDictionary(dset):
	grammarArticles = []
	punctuation = list(string.punctuation)
	for article in dset:	
		holder = np.zeros(len(punctuation))
		for sType in punctuation:
			holder[punctuation.index(sType)] += article.count(sType)
		grammarArticles.append(holder)
	return grammarArticles


def unison_shuffled_copies(a, b):
    assert len(a) == len(b)
    p = np.random.permutation(len(a))
    return a[p], b[p]


wordTokenized = createWordDictionary(totalData)
grammarTokenized = createGrammarDictionary(totalRaw)
finalTokenized = []
for i in range(wordTokenized.shape[0]):
	finalTokenized.append(np.concatenate((wordTokenized[i], grammarTokenized[i]), axis=None))

temp = []
for f in finalTokenized:
	temp.append(f/f.sum()*100+1)
finalTokenized = temp
finalTokenized = np.array(finalTokenized)
finalTokenized = ma.log(finalTokenized).filled(0)
print "SHAPE"
print len(totalData)
print len(totalData[0])

# So preprocessing decisions:
# First thing we do is divide by the length of the article, or its sum of bagged words. This is so that all articles train the synapses with the same magnitude
# The second thing we do is mutiply by 100 to add some intuitive separation to the values and fascilitate the log step
# The next step is add one to the end of each, explained next
# the final step is to take the log of everything to apply zipfy's linguistic law
#  -but if all our values were from 0-1, the log would go from error to negative to 1, bad scale
# 	If we make all of our values between 100 and 1, the max input value is 1, max is 2.
#  -Finally adding 1 throughs off the logistic curve partially but makes sure to differentiate between 0's and 1's because now 0's wikl be left as 0's and 1's will be 1's, everythign else is 1-3.



print finalTokenized.shape
print outPut.shape

finalTokenized, outPut = unison_shuffled_copies(finalTokenized, outPut)

np.save("preppedData.npy", finalTokenized)
np.save("preppedDataKey.npy", outPut)
