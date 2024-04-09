# -*- coding: utf-8 -*-
"""
Created on Mon Mar 27 20:59:32 2017

@author: qiangwennorge
"""

from pymongo import MongoClient
import requests
from bs4 import BeautifulSoup
import re
import pymongo
import string
from nltk.corpus import stopwords
import operator
from wordcloud import WordCloud, STOPWORDS
from os import path
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt

# Get Bolig information in each page

def GetInfoOfEachRealestate(BoligDoc,soup):
    for ParentalTag in soup.find_all("a","sf-search-ad-link link link--dark hover:no-underline"):
        BoligFinnCode = ParentalTag.get('id')
        BoligTitle = ParentalTag.getText()
        EachBoligDoc = {'boligfinncode': BoligFinnCode,
                        'boligtitle':BoligTitle}  
        BoligDoc.append(EachBoligDoc)
    return BoligDoc

# Start from first page

BoligDoc = []

BoligUrl = "https://www.finn.no/search/savedsearch?alertId=70732026"
BoligResponse = requests.get(BoligUrl)
BoligContent = BoligResponse.content

BoligSoup = BeautifulSoup(BoligContent,"html.parser")

BoligDoc = GetInfoOfEachRealestate(BoligDoc,BoligSoup) 

# Find the next page number

InitialTagsForNextPage = BoligSoup.find('nav','pagination u-pb8 u-pt16')
LastPageTag = InitialTagsForNextPage.find_all('a')[-1]
LastPageMatch = re.search(r'page=(\d+)', str(LastPageTag))
if LastPageMatch:
    LastPageNum = int(LastPageMatch.group(1))

#TODO Iterate thru the pages

# Go to the rest pages

for PageNum in range(NextPageNum,100):
    NextPage = re.sub(r'page=(\d+)', 'page='+str(PageNum), SecondPage)
    NextUrl = 'https://m.finn.no' + NextPage
    NextResponse = requests.get(NextUrl)
    NextHtml = NextResponse.content
    print(  PageNum )
    NextSoup = BeautifulSoup(NextHtml,"html.parser")
    TotalBoligDoc = GetInfoOfEachRealestate(BoligDoc,NextSoup)    

# Save collected bolig information to MongoDB
clientmongo = MongoClient(host = "localhost", port=27017)
databasehandler = clientmongo["FinnBoligDB"]
for EachBoligDoc in BoligDoc:
    databasehandler.boligcollection.insert(EachBoligDoc,safe=True)

# Fetch all bolig title
BoligCollectionDoc = databasehandler.boligcollection.find()
BoligTitleTextSum = ""
for doc in BoligCollectionDoc[2:]:
    BoligTitleText = doc.get("boligtitle")
    BoligTitleTextSum = BoligTitleTextSum + " " + BoligTitleText

BoligTitleTextSum = BoligTitleTextSum.replace(string.punctuation,"")

# Count word frequency
worddic = {}
for word in BoligTitleTextSum.split():
    if word not in worddic:
        worddic[word] = 1
    else:
        worddic[word] = worddic[word] + 1

# Sort word based on frequency
worddicsorted = sorted(worddic.items(),key=operator.itemgetter(1),reverse=True)

# Define stopwords
stop_words = ['-','og','med','i','til','|','fra','av','på','1','2','3','4','5','6','7','8','9','0']

# Remove stopwords
worddicclean = []
for k,v in worddicsorted:
    if k not in stop_words:
        worddicclean.append((k,v))

# Define path
d = path.dirname(__file__)

# Read the mask image
norway_mask = np.array(Image.open(path.join(d,"norwaymap.jpg")))

boligwordcloud = WordCloud(background_color="white",max_words=2000,mask=norway_mask,stopwords=stop_words)

# Generate word cloud
boligwordcloud.generate_from_frequencies(dict(worddicclean))
#  worddicclean )


# Store to file
boligwordcloud.to_file(path.join(d,"norwaymap_mask_output.png"))

# Show
plt.imshow(boligwordcloud,interpolation='bilinear')
plt.axis("off")
plt.figure()
plt.imshow(norway_mask,cmap=plt.cm.gray,interpolation='bilinear')
plt.axis("off")
plt.show()

# General a word cloud image

#d = path.dirname(__file__)
