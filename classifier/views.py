# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import get_object_or_404, render

from django.shortcuts import render
from django.http import HttpResponse

from .forms import ArForm 


import numpy as np


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

from uiProcesser import *

vectorizer, clsfyModel = setUpVec()
clsfyModel._make_predict_function()


def index(request, *args, **kwags):
	if request.method == 'POST':
		data = ''
		s = 'Invalid Input!'
		form = ArForm(request.POST)
		if form.is_valid():
			print "VLAID DATA"
			data = form.cleaned_data['article']
			if len(data.strip()) < 20:
				return render(request, 'classifier/index.html', {"article": ""})
	
			dataW = fitWordArticle(data, vectorizer)
			dataG = createGrammarDictionary([data])
			dataF = np.concatenate((dataW[0], dataG[0]), axis=None)
			dataF = ma.log(dataF/dataF.sum()*100+1).filled(0)
			outside = []
			outside.append(dataF)
			outside = np.array(outside)
			print "TESTER"
			print outside.shape
			ynew = clsfyModel.predict(outside)
			print ynew
			if ynew[0][0] > ynew[0][1]:
				s = "You are a Milton Paper Writer"
			else:
				s = "You are a Milton Measure Writer"
		return render(request, 'classifier/index.html', {"article": str(s)})
	else:
		return render(request, 'classifier/index.html', {"article": ""})




