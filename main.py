from gui import MainWindow
import tvdb_api as s
import xml.etree.ElementTree as ET
import asyncio
from scrapers._1337Scraper import search_1337x_async
from scrapers.piratebayScraper import search_piratebay
import realdebrid_api
import constants as c
from tkinter import Tk
import helpers as h


def get_link(torrent, update_callback):
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

    if update_callback:
        update_callback(download_link)
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
            if type_ == c.SEARCH_MOVIES:
                results = await s.search_movies(title)
                update_callback(c.SEARCH_MOVIES, results)
            else:
                print("Searching for a show")
                results = await s.search_shows(title)
                update_callback(c.SEARCH_SERIES, results)
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
            title = h.normalize_text(current_context.get('show'))

            if (current_context.get('source') == c._1337X):
                results = await search_1337x_async(title, current_context)
            elif (current_context.get('source') == c.NYAASI):
                return
            elif (current_context.get('source') == c.PIRATEBAY):
                results = await search_piratebay(title, current_context)
            elif (current_context.get('source') == c.YTS):
                return 
            else:
                print("search_sources: Unknown source")

            update_callback(c.SEARCH_SOURCES, results)
        except Exception as e:
            update_callback(["search_sources error"])

    asyncio.run(search_and_update())

def search_raw(current_context, update_callback):
    print("\tsearch_raw", current_context.get('show'))
    async def search_and_update():
        try:
            if (current_context.get('source') == c._1337X):
                results = await search_1337x_async(current_context.get("show"), current_context, raw=True)
            elif (current_context.get('source') == c.NYAASI):
                return
            elif (current_context.get('source') == c.PIRATEBAY):
                results = await search_piratebay(current_context.get("show"), current_context, raw=True)
            elif (current_context.get('source') == c.YTS):
                return 
            else:
                print("search_raw: Unknown source")

            update_callback(c.SEARCH_SOURCES, results)
        except Exception as e:
            update_callback(["search error"])

    asyncio.run(search_and_update())

def callback_manager(callback_type, payload, update_callback):
    if callback_type == c.SEARCH_MOVIES:
        search(payload, callback_type, update_callback)
    elif callback_type == c.SEARCH_RAW:
        search_raw(payload, update_callback)
    elif callback_type == c.SEARCH_SERIES:
        search(payload, callback_type, update_callback)
    elif callback_type == c.SEARCH_SEASONS:
        search_seasons(payload, update_callback)
    elif callback_type == c.SEARCH_EPISODES:
        search_episodes(payload, update_callback)
    elif callback_type == c.SEARCH_SOURCES:
        search_sources(payload, update_callback)
    elif callback_type == c.GET_LINK:
        get_link(payload, update_callback)

if __name__ == "__main__":
    h.clear_cache_if_exceeds_limit()
    window = Tk()
    app = MainWindow(
        window,
        on_callback=callback_manager,
    )
    app.start()
