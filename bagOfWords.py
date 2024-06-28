import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import requests
import time
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from collections import Counter
import matplotlib.pyplot as plt
from urllib.parse import quote

chrome_options = Options()
chrome_options.add_argument("--headless")  
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

# path
webdriver_service = Service('/usr/local/bin/chromedriver')  

# start chrome
driver = webdriver.Chrome(service=webdriver_service, options=chrome_options)

queryToPerform = input("Give query to search: ")

# ddg search
query_encoded = quote(queryToPerform)
inputURL = f'https://duckduckgo.com/?t=h_&q={query_encoded}&iar=news&ia=news'
driver.get(inputURL)

time.sleep(3)

# page extraction
soup = BeautifulSoup(driver.page_source, 'html.parser')

# all news
news_items = soup.find_all('div', class_='result__body')

# url for article
article_urls = []
for item in news_items:
    url_tag = item.find('a', class_='result__a')
    url = url_tag['href'] if url_tag else None
    if url:
        article_urls.append(url)

#getting the full text
def extract_full_text(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            article_soup = BeautifulSoup(response.content, 'html.parser')
            paragraphs = article_soup.find_all('p')
            full_text = ' '.join([p.text.strip() for p in paragraphs])
            return full_text
        else:
            return None
    except Exception as e:
        print(f"Error extracting full text from {url}: {str(e)}")
        return None

# full text
news_texts = []
for url in article_urls:
    full_text = extract_full_text(url)
    if full_text:
        news_texts.append(full_text)

# close
driver.quit()

# to token
stop_words = set(stopwords.words('english'))
word_freq = Counter()

for text in news_texts:
    tokens = word_tokenize(text.lower())  #to lower
    filtered_tokens = [word for word in tokens if word.isalnum() and word not in stop_words]
    word_freq.update(filtered_tokens)

# common words
common_words = word_freq.most_common(20)

labels, values = zip(*common_words)

#to plot
plt.figure(figsize=(10, 6))
plt.barh(labels, values, color='skyblue')
plt.xlabel('Frequency')
plt.title('Top 20 Words in News Articles')
plt.gca().invert_yaxis() 
plt.tight_layout()
plt.show()
