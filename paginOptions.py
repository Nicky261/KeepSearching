import time
import os
import requests

import logging

from bs4 import BeautifulSoup

from fake_useragent import UserAgent
from stem import Signal
from stem.control import Controller

from urllib.parse import quote, urlparse, parse_qs

from fileDownloader import download_pdf

logging.basicConfig(
    filename='my_log_file.log',  # Log file name
    level=logging.DEBUG,         # Log level
    format='%(asctime)s - %(levelname)s - %(message)s',  # Log format
    datefmt='%Y-%m-%d %H:%M:%S'  # Date format
)


def ClearScreen():
    os.system("clear")

def MakeDir(dirName):
    arg = "mkdir " + dirName 
    os.system(arg)

def MainDomain(url):
    from urllib.parse import urlparse
    # Parse the URL
    parsed_url = urlparse(url)

    domain = parsed_url.netloc

    main_domain = '.'.join(domain.split('.')[-2:])

    #print(f"The site name is: {main_domain}")

    return main_domain



proxies = {
    'http': 'socks5://127.0.0.1:9050',
    'https': 'socks5://127.0.0.1:9050'
}

print("Changing IP Address and User-Agent in every request....\n\n")


# init a userAgent instance
user_agent = UserAgent()

def fetch_search_results(search_term, 
                         num_pages=3, 
                         results_per_page=10,
                         advancedOption="filetype:pdf",
                         outputOption = True):
    
    realURLs = []
    try:
        # make query with filetype:pdf
        search_query = quote(f"{search_term} {advancedOption}")
        
        # tor for ip changes
        with Controller.from_port(port=9051) as c:
            c.authenticate()
            
            # go thr multiple pages
            for page in range(num_pages):

                outputOption and print(f"\n\n ----- PAGE = {page}\n\n")
                
                # get random usr agent
                headers = { 'User-Agent': user_agent.random }
                
                c.signal(Signal.NEWNYM)
                
                identityShow = requests.get("https://api.my-ip.io/v2/ip.txt", 
                                                        proxies=proxies, 
                                                        headers=headers).text
                outputOption and print(f"Your IP is: {identityShow}")
                
                outputOption and print(f"User Agent is: {headers['User-Agent']}")
                print("=" * 20)

                start = page * results_per_page
                
                # request to DuckDuckGo with
                response = requests.get(f'https://duckduckgo.com/html?q={search_query}&start={start}&count={results_per_page}'
                                        , proxies=proxies
                                        , headers=headers)
                
                #request ok
                if response.status_code == 200:
                    
                    # parse with BS
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # get links
                    result_links = soup.find_all('a', class_='result__a')
                    
                    # get real url
                    for link in result_links:
                        redirect_url = link['href']
                        parsed_url = urlparse(redirect_url)
                        real_url = parse_qs(parsed_url.query).get('uddg', [''])[0]
                        if outputOption == True:
                            print(f"Redirect URL: {redirect_url}")
                            print(f"Real URL: {real_url}")
                            print("-"*10)
                        if real_url:
                            realURLs.append(real_url)
                    
                    print("=" * 20)
                    
                elif response.status_code == 403:
                    outputOption and print("Access Forbidden. Check if Tor is configured correctly or if the website is blocking Tor exit nodes.")
                    outputOption and print("=" * 20)
                    #break  #access is forbidden
                
                else:
                    outputOption and print(f"Failed to fetch data. Status code: {response.status_code}")
                    outputOption and print("=" * 20)
                    #break
                time.sleep(1)
    
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        print("=" * 20)
        return realURLs

    return realURLs


def DigDeeper(searchTerm,targetSite, num_pages=3, results_per_page=10):

    advancesOnURL = []

    advancesOnURL = fetch_search_results(searchTerm, num_pages=1, 
                                         results_per_page=results_per_page,
                                         advancedOption=f"{searchTerm} site:{targetSite}",outputOption=False)

    return advancesOnURL

# usr interact
while True:
    try:
        
        search_term = input("Enter your search term (for KeepSearching): ")
        
        # pages obtained with diff ident.
        obtainedReal_URLs = []
        obtainedReal_URLs = fetch_search_results(search_term)

        if len(obtainedReal_URLs) == 0:
            print("We strongly advice you to retry")
            continue

        print(f"s-au obtinut {len(obtainedReal_URLs)}")

        logging.info(f"====search for {search_term}")
        for itr in obtainedReal_URLs:
            logging.info(f"\t\t{itr}")

        #--------
        #going deeper in some of the results
        digDeeperOption = input("Perform advances on range?(default on first 5)[d(efault),a-b(range a-b),NULL]")
        logging.info(f"deeper request = {digDeeperOption}")
        if digDeeperOption == "d":
            for itr in obtainedReal_URLs:

                DeeperResults = DigDeeper(searchTerm=search_term
                                          , targetSite=MainDomain(itr))

                print("~"*15)
                for itrDeeper in DeeperResults:
                    print(f"\t\t{itrDeeper}")
                print("*"*15)
        elif digDeeperOption.lower() == 'null':
            print("No deeper search selected")
        else:
            start_position,end_position = map(int,digDeeperOption.split('-'))
            start_position = start_position - 1
            end_position = end_position-1
            
            for index in range(start_position,end_position):
                DeeperResults=[]
                DeeperResults = DigDeeper(searchTerm=search_term,
                                      targetSite=MainDomain(obtainedReal_URLs[index]))
                print(f"====\nFor {obtainedReal_URLs[index]} deeper results are:")
                for itrDeeper in DeeperResults:
                    print(f"\t\t{itrDeeper}")
                print("*"*15) 

        #--------------
        
        screenStatus = input("Clear screen?[y/n]")
        if screenStatus == 'y':
            ClearScreen()


        askDowndload = input("Download Files?[y/n]")
        logging.info(f"\t\t\tdownload request = {askDowndload},")
        if askDowndload == 'y':

            
            downloadDirDestination = input("Give the name for download dir destination")

            MakeDir(downloadDirDestination)

            downloadRange = input("Give range to download[a-b]")
            logging.info(f"\t\t\tdownload range = {downloadRange}")
            start_positionDown,end_positionDown = map(int,digDeeperOption.split('-'))
            start_positionDown = start_positionDown - 1
            end_positionDown = end_positionDown-1

            for itr in range(start_positionDown,end_positionDown):
                download_pdf(obtainedReal_URLs[itr],downloadDirDestination)

        
        another_search = input("another search? (yes/no): ").strip().lower()
        
        if another_search != 'yes':
            break
        
    except KeyboardInterrupt:
        print("Exiting...")
        break
