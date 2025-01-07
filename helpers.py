import unicodedata
import subprocess
import os
import aiohttp
import hashlib
from io import BytesIO
from PIL import Image
import shutil

CACHE_DIR = "image_cache"

if not os.path.exists(CACHE_DIR):
    os.makedirs(CACHE_DIR)

def get_folder_size(folder_path):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(folder_path):
        for filename in filenames:
            file_path = os.path.join(dirpath, filename)
            if os.path.isfile(file_path):
                total_size += os.path.getsize(file_path)
    return total_size

def clear_cache_if_exceeds_limit(folder_path="image_cache", max_size_mb=100):
    folder_size = get_folder_size(folder_path)
    if folder_size > max_size_mb * 1024 * 1024:
        print(f"Cache size exceeds {max_size_mb}MB. Clearing cache...")
        shutil.rmtree(folder_path)
        os.makedirs(folder_path)
    else:
        print(f"Cache size is within limit: {folder_size / (1024 * 1024):.2f}MB.")

def get_image_filename(image_url):

    return os.path.join(CACHE_DIR, hashlib.md5(image_url.encode('utf-8')).hexdigest() + ".png")

async def download_image(image_url, target_height=150):
    filename = get_image_filename(image_url)

    if os.path.exists(filename):
        return filename

    async with aiohttp.ClientSession() as session:
        async with session.get(image_url) as response:
            response.raise_for_status()
            image_data = await response.read()
            image = Image.open(BytesIO(image_data))
            original_width, original_height = image.size
            aspect_ratio = original_width / original_height
            target_width = int(target_height * aspect_ratio)
            image = image.resize((target_width, target_height), Image.Resampling.LANCZOS)
            image.save(filename)
            return filename

def normalize_text(text):
    return ''.join(
        (c if unicodedata.category(c) != 'Mn' else '')
        for c in unicodedata.normalize('NFD', text)
    )

def open_in_player(url):
    potplayer_path = f"C:\Program Files\DAUM\PotPlayer\PotPlayerMini64.exe"
    command = [potplayer_path, url]
    try:
        subprocess.Popen(command)
        print("PotPlayer opened successfully.")
    except Exception as e:
        print(f"Error opening PotPlayer: {e}")