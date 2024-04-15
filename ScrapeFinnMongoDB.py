# -*- coding: utf-8 -*-
"""
Created on Mon Mar 27 20:59:32 2017

@author: qiangwennorge
"""

import requests
from bs4 import BeautifulSoup
import re
import numpy as np
import matplotlib.pyplot as plt
import csv

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
        if BilPrice is not None and  BilKm is not None :
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
    content_src = ['./example/finn_search_example.html',
                   './example/finn_search_example2.html',
                   './example/finn_search_example3.html']
else:
    # NOTE: The link below is fetched by right clicking on the link to the number one of the result page at the botton.
    content_src = ['https://www.finn.no/car/used/search.html?model=1.795.1247&sales_form=1&stored-id=70732026', 
                   'https://www.finn.no/car/used/search.html?model=1.795.1247&sales_form=1&stored-id=70732026&page=2',
                   'https://www.finn.no/car/used/search.html?model=1.795.1247&sales_form=1&stored-id=70732026&page=3']



# Iteration through result pages
for page in content_src:
    BilSoup = GetRawContent(page)
    EachPageBilDoc = GetInfoOfEachSearchPage(BilSoup) 
    if EachPageBilDoc is None:
        break
    BilDB.extend(EachPageBilDoc)

print('Total entries found:', len(BilDB))

prices=[]
kms=[]
for entry in BilDB:
    price_int=int(entry['ad_price'])
    prices.append(price_int)
    km_int=int(entry['ad_km'])
    kms.append(km_int)

price_array = np.array(prices)
km_array = np.array(kms)
coeff = np.polyfit(km_array, price_array, 1)
estPrice_per_km = np.poly1d(coeff)
print(estPrice_per_km(65000))


x_line = np.linspace(min(kms), max(kms), 200)
y_estimated = estPrice_per_km(x_line)
plt.scatter(kms, prices, color='black')
plt.plot(x_line, y_estimated, color='blue')

plt.savefig('plot.png')
# plt.xlabel['Km']
# plt.ylabel['Price']

csv_file = 'bil_data.csv'
with open(csv_file, mode='w', newline='') as file:
    writer =csv.DictWriter(file, fieldnames=BilDB[0].keys())
    writer.writeheader()

    for row in BilDB:
        writer.writerow(row)



