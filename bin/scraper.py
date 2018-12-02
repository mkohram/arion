import urllib.request
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
import logging

logging.basicConfig(format='%(name)s - %(levelname)s - %(message)s')


def download_file(url, filename):
    """
    Helper method handling downloading large files from `url` to `filename`.
    Returns a pointer to `filename`.
    """
    chunk_size = 1024
    r = requests.get(url, stream=True)
    with open(filename, 'wb') as f:
        p_bar = tqdm(unit="B", unit_scale=True)
        for chunk in r.iter_content(chunk_size=chunk_size):
            if chunk:
                # filter out keep-alive new chunks
                p_bar.update(len(chunk))
                f.write(chunk)
    return filename


if __name__ == "__main__":
    base_url = 'http://gissmo.nmrfam.wisc.edu'
    library_url = f'{base_url}/library'

    response = urllib.request.urlopen(library_url)
    soup = BeautifulSoup(response, 'html.parser')

    tr_list = list(soup.find_all('tr'))

    for idx, tr in enumerate(tr_list):
        if idx < 85:
            continue

        children = list(tr.children)
        download_col = children[-2]

        if download_col.name == 'th':
            # skipping table header

            continue

        entry_id = children[3].text.replace(' ', '_')

        href = download_col.find('a')['href']
        download_url = f'{base_url}{href}'

        print(f'\n({idx}/{len(tr_list) - 1}) {download_url}')
        download_file(download_url, f'../data/metabolites/{entry_id}.zip')
