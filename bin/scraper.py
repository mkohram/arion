import os.path
import urllib.request
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm


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
    data_dir = '/media/shared/arion_data'
    base_url = 'http://gissmo.nmrfam.wisc.edu'
    library_url = f'{base_url}/library'

    response = urllib.request.urlopen(library_url)
    soup = BeautifulSoup(response, 'html.parser')

    tr_list = list(soup.find_all('tr'))

    for idx, tr in enumerate(tr_list):
        children = list(tr.children)
        download_col = children[-2]

        if download_col.name == 'th':
            # skipping table header

            continue

        entry_id = children[3].text.replace(' ', '_')

        href = download_col.find('a')['href']
        download_url = f'{base_url}{href}'

        if os.path.isfile(f'{data_dir}/raw/{entry_id}.zip') or \
                os.path.isdir(f'{data_dir}/metabolites/{entry_id[5:]}'):
            continue
        else:
        #     print(f'{entry_id} not found')
        #     download_file(download_url, f'{data_dir}/raw/{entry_id}.zip')

            print(f'({idx}/{len(tr_list) - 1}) {download_url} {entry_id}')
