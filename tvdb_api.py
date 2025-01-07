import tvdb_v4_official
import re
from helpers import download_image
from dotenv import load_dotenv
import os

load_dotenv('.api_keys')
TVDB_API_KEY = os.getenv("TVDB_API_KEY")
tvdb = tvdb_v4_official.TVDB(TVDB_API_KEY)

async def search_shows(title, type_, limit_=20):
    results = tvdb.search(title, limit=limit_, type=type_)
    if results:
        formatted_results = []
        image_tasks = []
        show_data = []
        for result in results:
            show_details = {
                "id": get_id(result['id']),
                "title": result.get('name', 'Unknown Title'),
                "year": result.get('year', 'N/A'),
                "genres": result.get('genres', []),
                "release_date": result.get('first_air_time', 'N/A'),
                "status": result.get('status', 'N/A'),
                "image_url": result.get('image_url', 'N/A'),
                "item": get_letters(result['id']),
            }
            show_data.append(show_details)
            if show_details.get('image_url'):
                image_task = download_image(show_details['image_url'])
                image_tasks.append((image_task, show_details))
        for task, show_details in image_tasks:
            image_path = await task
            show_details['image_path'] = image_path
        return show_data
    else:
        return []

async def search_movies(title, type_, limit_=20):
    results = tvdb.search(title, limit=limit_, type=type_)
    if results:
        formatted_results = []
        image_tasks = []
        movie_data = []
        for result in results:
            movie_details = {
                "id": get_id(result['id']),
                "title": result.get('name', 'Unknown Title'),
                "year": result.get('year', 'N/A'),
                "genres": result.get('genres', []),
                "release_date": result.get('first_air_time', 'N/A'),
                "status": result.get('status', 'N/A'),
                "image_url": result.get('image_url', 'N/A'),
                "item": get_letters(result['id']),
            }
            movie_data.append(movie_details)
            if movie_details.get('image_url'):
                image_task = download_image(movie_details['image_url'])
                image_tasks.append((image_task, movie_details))
        for task, movie_details in image_tasks:
            image_path = await task
            movie_details['image_path'] = image_path
        return movie_data
    else:
        return []

async def search_seasons(id_):
    print(f"Fetching seasons for series with ID: {id_}")
    series = tvdb.get_series_extended(id_)
    aired_order_seasons = [
        season for season in series['seasons'] if season['type']['name'] == 'Aired Order'
    ]
    if aired_order_seasons:
        print(f"Aired Order seasons for {series['name']}:")
        result = []
        image_tasks = []
        season_data = []
        for season in aired_order_seasons:
            season_details = {
                "id": season['id'],
                "title": season.get('name', f"Season {season['number']}"),
                "year": season.get('lastUpdated', "").split("-")[0],
                "image_url": season.get('image', None),
                "item": "season",
                "number": season.get('number'),
            }
            season_data.append(season_details)
            if season_details.get('image_url'):
                image_task = download_image(season_details['image_url'])
                image_tasks.append((image_task, season_details))
        for task, season_details in image_tasks:
            image_path = await task
            season_details['image_path'] = image_path
        return season_data
    else:
        print("No Aired Order seasons available for this series.")
        return []

async def search_episodes_for_season(season_id):
    season = tvdb.get_season_extended(season_id)
    if 'episodes' in season:
        episodes_result = []
        image_tasks = []
        episodes_data = []
        for episode in season['episodes']:
            episode_details = {
                "id": episode['id'],
                "title": episode.get('name', f"Episode {episode['number']}"),
                "year": episode.get('number'),
                "image_url": episode.get('image', None),
                "item": "get_sources",
                "overview": episode.get('overview', "No description available."),
            }
            episodes_data.append(episode_details)

            if episode_details.get('image_url'):
                image_task = download_image(episode_details['image_url'])
                image_tasks.append((image_task, episode_details))

        for task, episode_details in image_tasks:
            image_path = await task
            episode_details['image_path'] = image_path

        return episodes_data
    else:
        print("No episodes found for this season.")
        return []

def get_id(id):
    match = re.search(r'-(\d+)', id)
    return match.group(1) if match else print("def get_id(id): Error: No match found.")

def get_letters(id):
    match = re.search(r'([a-zA-Z]+)', id)
    return match.group(1) if match else print("Error: No match found.")