import requests
from dotenv import load_dotenv
import os

load_dotenv('.api_keys')
REAL_DEBRID_API_KEY = os.getenv("REAL_DEBRID_API_KEY")

API_URL = "https://api.real-debrid.com/rest/1.0/"

def get_headers():
    return {
        "Authorization": f"Bearer {REAL_DEBRID_API_KEY}",
        "Content-Type": "application/json"
    }

def stream_file(file_id):
    url = f"{API_URL}streaming/transcode/{file_id}"
    headers = get_headers()

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        for format_type, qualities in data.items():
            print(f"Format: {format_type}")
            if isinstance(qualities, dict):
                for quality, value in qualities.items():
                    print(f"  Quality: {quality}, Value: {value}")
            print("-" * 50)
        else:
            print("Error: No streaming link found.")
            return None
    else:
        print(f"Error streaming file: {response.status_code}")
        return None

#/torrents
def get_user_torrents(page=1, limit=100):
    url = f"{API_URL}torrents"
    headers = get_headers()
    params = {
        "page": page,
        "limit": limit,
    }

    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        file_list = response.json()
        if not file_list:
            print("No files found.")
            return

        for file in file_list:
            print(f"ID: {file.get('id', 'N/A')}")
            print(f"Filename: {file.get('filename', 'N/A')}")
            print(f"Link: {file.get('links', 'N/A')}")
            print("-" * 50)

            links = file.get('links')
            if links and len(links) > 0:
                return links[0]

        return 'N/A'
    else:
        print(f"Error fetching torrents: {response.text}")
        return None

#/torrents/info/{id}
def get_torrent_info(torrent_id):
    url = f"{API_URL}torrents/info/{torrent_id}"
    headers = get_headers()
    params = {}

    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        response_json = response.json()
        print(f"Torrent Filename: {response_json.get('filename', 'N/A')}")

        print("\nFiles:")
        files = response_json.get('files', [])
        if files:
            for file in files:
                print(f"  - File ID: {file.get('id', 'N/A')}, Path: {file.get('path', 'N/A')}, Size: {file.get('bytes', 0)} bytes")
        else:
            print("  No files found.")

        return response_json
    else:
        print(f"Error fetching torrents: HTTP {response.status_code} - {response.text}")
        return None

#/torrents/addMagnet
def upload_magnet(magnet_link):
    url = f"{API_URL}torrents/addMagnet"
    headers = get_headers()
    data = {"magnet": magnet_link}

    # Make POST request to add magnet
    response = requests.post(url, headers=headers, data=data)

    if response.status_code == 201:
        return response.json()

    else:
        print(f"Error uploading magnet: {response.text}")
        return False

#/torrents/selectFiles/{id}
def select_files(torrent_id, files="all"):
    url = f"{API_URL}torrents/selectFiles/{torrent_id}"
    headers = get_headers()
    data = {"files": files}


    response = requests.post(url, headers=headers, data=data)

    if response.status_code == 204:
        return True
    else:
        print(f"Error selecting files for torrent ID {torrent_id}: {response.text}")
        return False

#/torrents/availableHosts
def check_if_cached(magnet_link):
    url = f"{API_URL}torrents/availableHosts"
    headers = get_headers()
    data = {"host": magnet_link}

    response = requests.post(url, headers=headers, data=data)

    if response.status_code == 200:
        available_hosts = response.json()
        if available_hosts:
            return True
        else:
            return False
    else:
        print(f"Error checking if cached: {response.text}")
        return False

def check_link(url):
    url = f"{API_URL}unrestrict/check"
    headers = get_headers()
    payload = {
        "link": url
    }

    response = requests.post(url, headers=headers, data=payload)

    if response.status_code == 200:
        data = response.json()

        print("check_link link:", data.get('link'))
        print("check_link supported:", data.get('supported'))

        if "supported" in data:
            return data.get("supported")
        else:
            print("Error: No supported field found.")
            return False
    else:
        print(f"Error checking link: {response.status_code}")
        return False

#/unrestrict/link
def unrestrict_link(link, password=None, remote=0):
    url = f"{API_URL}unrestrict/link"
    headers = get_headers()
    payload = {
        "link": link,
        "password": password if password else "",
        "remote": remote
    }

    response = requests.post(url, headers=headers, data=payload)
    if response.status_code == 200:
        data = response.json()
        if "download" in data:
            return data.get("download")
        else:
            print("Error: No download link found.")
            return None
    else:
        print(f"Error fetching download link: {response.status_code}")
        print(response.text)
        return None

#/downloads
def get_user_downloads(page=1, limit=100):
    url = f"{API_URL}downloads"
    headers = get_headers()
    params = {
        "page": page,
        "limit": limit,
    }

    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching downloads: {response.text}")
        return None

#/torrents/activeCount
def get_active_count():
    url = f"{API_URL}torrents/activeCount"
    headers = get_headers()

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        return data.get("nb")
    else:
        print(f"Error fetching active count: {response.text}")
        return None