import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

def extract_links(url):

    try:
        response = requests.get(url)
        response.raise_for_status()  # an HTTPError

        soup = BeautifulSoup(response.content, 'html.parser')
        links = []

        for a_tag in soup.find_all('a', href=True):
            name = a_tag.get_text(strip=True)
            link = a_tag['href']
            full_link = urljoin(url, link)
            links.append({'name': name, 'link': full_link})

        return links

    except requests.RequestException as e:
        print(f"An error occurred while fetching the URL: {e}")
        return []

url = input("Give link ")  #
links = extract_links(url)
    
for link in links:
    print(f"Name: {link['name']}, Link: {link['link']}")