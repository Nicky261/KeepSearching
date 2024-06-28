import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import requests
import time
from urllib.parse import quote

# escape special LaTeX characters
def escape_latex(text):
    special_chars = {
        '&': r'\&',
        '%': r'\%',
        '$': r'\$',
        '#': r'\#',
        '_': r'\_',
        '{': r'\{',
        '}': r'\}',
        '~': r'\textasciitilde ',
        '^': r'\textasciicircum ',
        '\\': r'\textbackslash '
    }
    return ''.join(special_chars.get(char, char) for char in text)

# Setup Chrome options
chrome_options = Options()
chrome_options.add_argument("--headless")  
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

webdriver_service = Service('/usr/local/bin/chromedriver')  

driver = webdriver.Chrome(service=webdriver_service, options=chrome_options)

queryToPerform = input("Give query to search: ")

query_encoded = quote(queryToPerform)
inputURL = f'https://duckduckgo.com/?t=h_&q={query_encoded}&iar=news&ia=news'
driver.get(inputURL)

time.sleep(3)

# Extract the page source and parse it with BeautifulSoup
soup = BeautifulSoup(driver.page_source, 'html.parser')

# Find all news items
news_items = soup.find_all('div', class_='result__body')

# Create a directory to save images
os.makedirs('news_images', exist_ok=True)
os.system('cd news_images && rm *')
news_data = []

for idx, item in enumerate(news_items):
    # find title
    title_tag = item.find('a', class_='result__a')
    title = escape_latex(title_tag.text) if title_tag else 'N/A'

    # find url
    url = title_tag['href'] if title_tag else 'N/A'

    # time 
    time_tag = item.find('span', class_='result__timestamp')
    time_ago = time_tag.text if time_tag else 'N/A'

    # image url
    image_tag = item.find('img', class_='result__image__img')
    image_url = 'https:' + image_tag['src'] if image_tag and 'src' in image_tag.attrs else 'N/A'

    # short descr
    snippet_tag = item.find('div', class_='result__snippet')
    snippet = escape_latex(snippet_tag.text) if snippet_tag else 'N/A'

    # down image
    if image_url != 'N/A':
        try:
            image_response = requests.get(image_url)
            image_response.raise_for_status()  # error if case
            image_content = image_response.content
            if image_content.startswith(b'\xff\xd8'):  # header check
                image_path = f'news_images/news_image_{idx}.jpg'
                with open(image_path, 'wb') as file:
                    file.write(image_content)
            else:
                image_path = 'N/A'
                print(f"Error: Invalid JPEG format for {image_url}")
        except requests.exceptions.RequestException as e:
            image_path = 'N/A'
            print(f"Error downloading image: {e}")
    else:
        image_path = 'N/A'

    # news item to the list
    news_data.append({
        'title': title,
        'url': url,
        'time_ago': time_ago,
        'image_path': image_path,
        'snippet': snippet  # snippet in news_data
    })

# close br
driver.quit()

# LaTeX document
latex_template = r'''
\documentclass{article}
\usepackage[T1]{fontenc}
\usepackage[utf8]{inputenc}
\usepackage{graphicx}
\usepackage{hyperref}
\usepackage{geometry}  % Adjust margins
\geometry{a4paper, margin=1in}

\title{News Report}
\author{}
\date{}

\begin{document}

\maketitle

\section*{Query}
Query: \url{$queryURL}

$newsContent

\end{document}
'''

# Prepare the news content section
news_content = ''
for news in news_data:
    news_content += rf'''
\section*{{{news['title']}}}
URL: \url{{{news['url']}}} \\
Time Ago: {news['time_ago']} \\
Snippet: {news['snippet']}

'''

    if news['image_path'] != 'N/A' and os.path.exists(news['image_path']):
        news_content += rf'''
\begin{{center}}
\includegraphics[width=0.8\textwidth]{{{news['image_path']}}}
\end{{center}}

'''
    else:
        news_content += 'Image not available\n\n'


latex_content = latex_template.replace('$queryURL', inputURL).replace('$newsContent', news_content)


latex_filename = 'news_report.tex'
with open(latex_filename, 'w', encoding='utf-8') as f:
    f.write(latex_content)

print(f"LaTeX document generated: {latex_filename}")


import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import os

def send_email(subject, body, to_email, file_path=None):
    # CONFIGURAREA EMAIL
    from_email = "nicolai.gaitan261@gmail.com"
    password = "wukt olgw oeqk hfpc"
    smtp_server = "smtp.gmail.com"
    smtp_port = 587 

    # CREARE EMAIL
    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject

    # ATASAREA BODY-ULUI
    msg.attach(MIMEText(body, 'plain'))

    # ATASAREA FIȘIERULUI
    if file_path is not None:
        try:
            with open(file_path, "rb") as attachment:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(attachment.read())
            
            encoders.encode_base64(part)
            part.add_header(
                "Content-Disposition",
                f"attachment; filename= {os.path.basename(file_path)}",
            )
            msg.attach(part)
        except Exception as e:
            print(f"Failed to attach file: {e}")
            return

    # TRIMITE EMAIL
    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(from_email, password)
        server.sendmail(from_email, to_email, msg.as_string())
        server.quit()
        print("Email sent successfully!")
    except Exception as e:
        print(f"Failed to send email: {e}")


send_email("test", "test", "nicolai.gaitan261@gmail.com", "./news_report.tex")

os.system("pdflatex news_report.tex")
send_email(f"{queryToPerform}", "Acesta este buletinul de stiri", "nicolai.gaitan261@gmail.com", "./news_report.pdf")
