import asyncio
import aiohttp
from bs4 import BeautifulSoup

# Asynchronous helper function to make HTTP requests
async def get_html(session, url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36"
    }
    async with session.get(url, headers=headers) as response:
        response.raise_for_status()
        return await response.text()

# Function to scrape the torrents list asynchronously
async def scrape_1337x(session, url):
    torrents = []
    html = await get_html(session, url)
    soup = BeautifulSoup(html, 'html.parser')
    torrents_container = soup.select('.table-list tbody tr')

    if not torrents_container:
        print("No torrents found on the page.")
        return []

    for row in torrents_container:
        # Extract torrent name and link
        torrent_name = row.select('td.coll-1 a')[1].get_text().strip()
        torrent_url = 'https://1337x.to' + row.select('td.coll-1 a')[1]['href']

        # Extract seeds, leeches, and other details
        torrent_seeds = row.select('td.coll-2')[0].get_text().strip()
        torrent_leeches = row.select('td.coll-3')[0].get_text().strip()

        # Extract size and clean it up
        size_cell = row.select('td.coll-4')[0]
        torrent_size = size_cell.contents[0].strip()  # Get only the main text before nested tags

        #print(f"Found torrent: {torrent_name}, Seeds: {torrent_seeds}, Leeches: {torrent_leeches}, Size: {torrent_size}")

        torrents.append({
            'torrentName': torrent_name,
            'torrentURL': torrent_url,
            'torrentSeeds': torrent_seeds,
            'torrentLeeches': torrent_leeches,
            'torrentSize': torrent_size,
            'actualTorrent': False
        })

    torrents = [torr for torr in torrents if torr['torrentName']]
    return torrents

# Function to get magnet link from a torrent page asynchronously
async def get_1337_magnet(session, url):
    print(f"Fetching magnet for URL: {url}")
    html = await get_html(session, url)
    soup = BeautifulSoup(html, 'html.parser')

    # Extract magnet link
    magnet = soup.select_one('.clearfix ul li a[href^="magnet:?"]')['href'] if soup.select_one('.clearfix ul li a[href^="magnet:?"]') else ""

    # Extract file size
    size_info = soup.select_one('ul.list li:contains("Total size") span')
    torrent_size = size_info.get_text().strip() if size_info else "N/A"

    # Extract downloads info
    downloads_info = soup.select_one('ul.list li:contains("Downloads")')
    torrent_downloads = downloads_info.get_text().strip() if downloads_info else "N/A"

    # Extract description
    description_info = soup.select_one('#description p')
    torrent_description = description_info.get_text().strip() if description_info else "No description"

    print(f"Size: {torrent_size}, Downloads: {torrent_downloads}")

    return {
        'magnet': magnet,
        'torrentSize': torrent_size,
        'torrentDownloads': torrent_downloads,
        'torrentDescription': torrent_description
    }

# Asynchronous function to fetch torrents and magnet links
async def search_1337x_async(query):
    print(f"Searching for query: {query}")
    search_url = f'https://1337x.to/sort-search/{query}/size/desc/1/'

    # Create an aiohttp session
    async with aiohttp.ClientSession() as session:
        # Scrape the search results page asynchronously
        torrents = await scrape_1337x(session, search_url)
        if not torrents:
            print("No torrents found.")
            return []

        # Gather magnet info for each torrent asynchronously
        tasks = []
        for torrent in torrents:
            task = asyncio.ensure_future(get_1337_magnet(session, torrent['torrentURL']))
            tasks.append(task)

        # Wait for all magnet fetching tasks to complete
        magnet_info = await asyncio.gather(*tasks)

        # Update torrents with the fetched magnet info
        for i, torrent in enumerate(torrents):
            torrent.update(magnet_info[i])

        print(f"Found {len(torrents)} torrents with magnet info.")
        return torrents
