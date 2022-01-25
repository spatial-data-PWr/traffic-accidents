import os
import requests 
from src import STORAGE_PATH, TMP_PATH
from src.config import CITY

DATA_DIRECTORY = STORAGE_PATH / 'shapefiles'
EXTENSIONS_TO_COPY = ['.shp', '.shx', '.dbf']

def download(url, filename):
    output_dir = TMP_PATH
    output_file = f'file_{filename}'
    output_path = output_dir / output_file
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    try:
        with requests.get(url, stream=True, allow_redirects=True) as r:
            r.raise_for_status()
            with open(output_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=16384): 
                    f.write(chunk)
    except Exception as ex:
        return None, None
    return output_path, output_file


def unzip(path, filename):
    output_dir = TMP_PATH / f'directory_{filename}'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    try:
        import patoolib
        patoolib.extract_archive(path, outdir=output_dir, verbosity=-1)
    except ModuleNotFoundError:
        try:
            import shutil
            shutil.unpack_archive(path, output_dir)
        except ModuleNotFoundError:
            try:
                from zipfile import ZipFile
                ZipFile(path).extractall(output_dir)
            except ModuleNotFoundError:
                print('Patoollib, shutil or zipfile is needed for the script to work correctly!')
                return None

    if os.path.isfile(path):
        os.remove(path)
    return output_dir


def move_correct_files(directory):
    files_to_copy = []
    if not os.path.exists(DATA_DIRECTORY):
        os.makedirs(DATA_DIRECTORY)
    
    directories_to_search_through = [directory]
    while len(directories_to_search_through) > 0:
        directory = directories_to_search_through.pop()

        for filename in os.listdir(directory):
            if os.path.isfile(f'{directory}/{filename}'):
                _, ext = os.path.splitext(filename)
                if ext in EXTENSIONS_TO_COPY:
                    os.rename(f'{directory}/{filename}', f'{DATA_DIRECTORY}/{filename}')
            
            elif os.path.isdir(f'{directory}/{filename}'):
                directories_to_search_through.append(f'{directory}/{filename}')


links_to_download = ['http://geoportal.wroclaw.pl/www/pliki/DaneRowerowe/TrasyRowerowe.zip', 'https://geoportal.wroclaw.pl/www/pliki/wypadki-kolizje.zip']
for link in links_to_download:
    url = link
    filename = link.split('/')[-1]
    path, filename = download(url, filename)
    if path is None:
        continue

    directory = unzip(path, filename)
    if directory is None:
        continue
    move_correct_files(directory)

