import requests
import urllib.parse

async def get(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()

async def search_piratebay(title, current_context, raw=False):
    print("search_piratebay()")
    search_type = ""
    if (current_context.get('type') == "series"):
        season = current_context.get('season')
        episode = current_context.get('episode')
        query = f"{title}%20s{int(season):02}e{int(episode):02}"
        search_type = "&cat=205" # TV Shows
    elif (raw):
         query = urllib.parse.quote(title)
    else:
        year = current_context.get('year')
        query = f"{title}%20{int(year)}"
        search_type = "&cat=201" # Movies

    #search_url = f'https://thepiratebay.org/search.php?q={query}&all=on&search=Pirate+Search&page=0{search_type}'
    search_url = f'https://apibay.org/q.php?q={query}{search_type}'

    raw_results = await get(search_url)

    results = []
    for result in raw_results:
        a = {
            "torrentName": result.get('name'),
            "torrentSize": f"{int(result.get('size')) / (1024 ** 3):.2f} GB",
            "magnet": f"""magnet:?xt=urn:btih:{result.get('info_hash')}&dn={urllib.parse.quote(result.get('name', ''))}
&tr=udp://tracker.opentrackr.org:1337/announce
&tr=udp://open.stealth.si:80/announce
&tr=udp://tracker.torrent.eu.org:451/announce
&tr=udp://tracker.bittor.pw:1337/announce
&tr=udp://public.popcorn-tracker.org:6969/announce
&tr=udp://tracker.dler.org:6969/announce
&tr=udp://exodus.desync.com:6969
&tr=udp://open.demonii.com:1337/announce""",
        }
        results.append(a)

    return results
