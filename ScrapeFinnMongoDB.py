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

# Get Bil information in each page

def GetNumValue(text_src):
    stripped_text= "".join(text_src.split())
    match = re.search(r'\d+', stripped_text)
    if match:
        return match.group(0)
    return None

def GetInfoOfEachSearchPage(soup):
    BilList=[]
    for ParentTag in soup.find_all('div', {'class', 'flex flex-col'}):
        FoundTitleTag = ParentTag.find('a',{'class', 'sf-search-ad-link link link--dark hover:no-underline'})
        BilFinnCode = FoundTitleTag.get('id')
        BilTitle = FoundTitleTag.getText()
        FoundYearKmPriceTag = ParentTag.find('div', {'class', 'mb-8 flex justify-between whitespace-nowrap font-bold'})
        FoundYearKmPriceMatch = FoundYearKmPriceTag.find_all('span')
        BilYear = FoundYearKmPriceMatch[0].getText()
        BilKm = GetNumValue(FoundYearKmPriceMatch[1].getText())
        BilPrice = GetNumValue(FoundYearKmPriceMatch[2].getText())
        print(BilKm)
        EachBilDoc = {'ad_finncode': BilFinnCode,
                      'ad_year': BilYear,
                      'ad_km': BilKm,
                      'ad_price': BilPrice,
                      'ad_title':BilTitle}  
        BilList.append(EachBilDoc)
    return BilList

def GetRawContent(content_src):
    BilSoup = None
    if debug:
        with open(content_src, 'r') as html_file:
            BilSoup = BeautifulSoup(html_file.read(), "html.parser")
    else:
        BilResponse = requests.get(content_src)
        if (BilResponse):
            BilContent = BilResponse.content
            BilSoup = BeautifulSoup(BilContent,"html.parser")
    return BilSoup

# Start from first page
debug = True
BilDB = []

if debug:
    content_src='./example/finn_search_example.html'
    MAX_PAGES=1
else:
    # NOTE: The link below is fetched by right clicking on the link to the number one of the result page at the botton.
    content_src = 'https://www.finn.no/car/used/search.html?model=1.795.1247&sales_form=1&stored-id=70732026'
    MAX_PAGES=100



# Iteration through result pages
for page_idx in range(1,MAX_PAGES+1):
    content_source = content_src + '&page=' + str(page_idx)
    BilSoup = GetRawContent(content_src)
    EachPageBilDoc = GetInfoOfEachSearchPage(BilSoup) 
    if EachPageBilDoc is None:
        break
    BilDB.extend(EachPageBilDoc)
    print('page ' + str(page_idx))
# print(BilDB)



# # Save collected ad information to MongoDB
# clientmongo = MongoClient(host = "localhost", port=27017)
# databasehandler = clientmongo["FinnBilDB"]
# for EachBilDoc in BilDB:
    # databasehandler.ad_collection.insert(EachBilDoc,safe=True)

# # Fetch all ad title
# BilCollectionDoc = databasehandler.ad_collection.find()
# BilTitleTextSum = ""
# for doc in BilCollectionDoc[2:]:
    # BilTitleText = doc.get("ad_title")
    # BilTitleTextSum = BilTitleTextSum + " " + BilTitleText

# BilTitleTextSum = BilTitleTextSum.replace(string.punctuation,"")

# # Count word frequency
# worddic = {}
# for word in BilTitleTextSum.split():
    # if word not in worddic:
        # worddic[word] = 1
    # else:
        # worddic[word] = worddic[word] + 1

# # Sort word based on frequency
# worddicsorted = sorted(worddic.items(),key=operator.itemgetter(1),reverse=True)

# # Define stopwords
# stop_words = ['-','og','med','i','til','|','fra','av','på','1','2','3','4','5','6','7','8','9','0']

# # Remove stopwords
# worddicclean = []
# for k,v in worddicsorted:
    # if k not in stop_words:
        # worddicclean.append((k,v))

# # Define path
# d = path.dirname(__file__)

# # Read the mask image
# norway_mask = np.array(Image.open(path.join(d,"norwaymap.jpg")))

# ad_wordcloud = WordCloud(background_color="white",max_words=2000,mask=norway_mask,stopwords=stop_words)

# # Generate word cloud
# ad_wordcloud.generate_from_frequencies(dict(worddicclean))
# #  worddicclean )


# # Store to file
# ad_wordcloud.to_file(path.join(d,"norwaymap_mask_output.png"))

# # Show
# plt.imshow(ad_wordcloud,interpolation='bilinear')
# plt.axis("off")
# plt.figure()
# plt.imshow(norway_mask,cmap=plt.cm.gray,interpolation='bilinear')
# plt.axis("off")
# plt.show()

# # General a word cloud image

# #d = path.dirname(__file__)
