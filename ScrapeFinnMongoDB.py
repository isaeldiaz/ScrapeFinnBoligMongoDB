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
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures

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

csv_file = 'bil_data.csv'
with open(csv_file, mode='w', newline='') as file:
    writer =csv.DictWriter(file, fieldnames=BilDB[0].keys())
    writer.writeheader()

    for row in BilDB:
        writer.writerow(row)


# Load your data
data = pd.read_csv('bil_data.csv')
km_price_data = data[['ad_km', 'ad_price']]

# Create polynomial features
poly = PolynomialFeatures(degree=2)
X = km_price_data[['ad_km']]
y = km_price_data['ad_price']
X_poly = poly.fit_transform(X)

# Fit polynomial regression model
poly_model = LinearRegression()
poly_model.fit(X_poly, y)

# Generating points for a smooth curve
X_fit = np.linspace(X.min(), X.max(), 100)
y_poly_pred = poly_model.predict(poly.fit_transform(X_fit.reshape(-1, 1)))

# Plotting
plt.figure(figsize=(10, 6))
plt.scatter(km_price_data['ad_km'], km_price_data['ad_price'], alpha=0.5)
plt.plot(X_fit, y_poly_pred, color='green', linewidth=2, label='2nd Order Polynomial Fit')
plt.title('Scatter plot of Kilometers vs Price with Polynomial Fit')
plt.xlabel('Kilometers (km)')
plt.ylabel('Price (NOK)')
plt.legend()
plt.grid(True)
plt.savefig('plot.png')


