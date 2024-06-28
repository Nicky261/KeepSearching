import os
import requests

def download_pdf(url, save_path):
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        
        file_name = url.split('/')[-1]
        save_file_path = os.path.join(save_path, file_name)

        with open(save_file_path, 'wb') as f:
            f.write(response.content)
        print(f"PDF downloaded ok to {save_file_path}")
    else:
        print(f"failed to download PDF. code: {response.status_code}")

#example
pdf_url = 'https://math-cs.gordon.edu/courses/mat230/notes/combinatorics.pdf'  
save_directory = './HAHA'  


if not os.path.exists(save_directory):
    os.makedirs(save_directory)

download_pdf(pdf_url, save_directory)
