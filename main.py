from PIL import Image, ImageTk
from gui import MainWindow
import requests
import io
import tvdb_api as s
import xml.etree.ElementTree as ET
import asyncio
from scrapers._1337Scraper import search_1337x_async
import realdebrid_api
import subprocess
from tkinter import Tk
import helpers as h


def get_link(torrent, callback):
    magnet_link = torrent.get('magnet')


    upload_response = realdebrid_api.upload_magnet(magnet_link)
    t_id = upload_response.get('id')

    torrent_info = realdebrid_api.get_torrent_info(t_id)

    realdebrid_api.select_files(t_id, get_largest_file_id(torrent_info))


    link = realdebrid_api.get_user_torrents()
    print(link)

    download_link = realdebrid_api.unrestrict_link(link)

    print("\nUser downloads")
    realdebrid_api.get_user_downloads()

    if callback:
        callback(download_link)
    h.open_in_player(download_link)

def get_largest_file_id(torrent_info):
    if 'files' not in torrent_info or not torrent_info['files']:
        print("No files found in the torrent.")
        return None

    largest_file_id = None
    largest_file_size = 0

    for file in torrent_info['files']:
        if file['bytes'] > largest_file_size:
            largest_file_size = file['bytes']
            largest_file_id = file['id']

    return largest_file_id

def search(title, type_, update_callback):

    h.normalize_text(title)
    print("\tsearch")
    async def search_and_update():
        try:
            if type_ == "movie":
                results = await s.search_movies(title, type_)
                update_callback("search_movie", results)
            else:
                print("Searching for a show")
                results = await s.search_shows(title, type_)
                update_callback("search_series", results)
        except Exception as e:
            update_callback(["search error"])

    asyncio.run(search_and_update())

def search_seasons(id_, update_callback):
    print("\tsearch_seasons", id_)
    async def search_and_update():
        try:
            results = await s.search_seasons(id_)

            update_callback("search_seasons", results)
        except Exception as e:
            update_callback(["search_seasons error"])

    asyncio.run(search_and_update())


def search_episodes(season_id, update_callback):
    async def search_and_update():
        try:
            results = await s.search_episodes_for_season(season_id)

            update_callback("search_episodes", results)
        except Exception as e:
            update_callback(["search_seasons error"])

    asyncio.run(search_and_update())

def search_sources(current_context, update_callback):
    async def search_and_update():
        try:
            query_1337x = None
            title = h.normalize_text(current_context.get('show'))
            if (current_context.get('type') == "series"):
                season = current_context.get('season')
                episode = current_context.get('episode')
                query_1337x = f"{title}%20s{int(season):02}e{int(episode):02}"
            else:
                year = current_context.get('year')
                query_1337x = f"{title}%20{int(year)}"

            torrents_1337 = await search_1337x_async(query_1337x)

            update_callback("search_sources", torrents_1337)
        except Exception as e:
            update_callback(["search_sources error"])

    asyncio.run(search_and_update())

if __name__ == "__main__":
    h.clear_cache_if_exceeds_limit()
    window = Tk()
    app = MainWindow(
        window,
        on_search_callback=search,
        on_seasons_callback=search_seasons,
        on_episodes_callback=search_episodes,
        on_sources_callback=search_sources,
        on_magnet_callback=get_link
    )
    app.start()