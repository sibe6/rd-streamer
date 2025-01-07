# rd-streamer

## General info
Python app that uses TVDB, scraping and Real-Debrib for fetching and streaming.

### Note!  
Requires following API-keys  
- [Real-Debrid Premium](https://real-debrid.com/)
- [TVDB](https://www.thetvdb.com/api-information)

PotPlayer set as default player. Can be changed from ```./helpers.py open_in_player() ```

## Usage

Install requirements
```sh
pip install -r requirements.txt
 ```

Set api-keys  
```sh
touch .api_keys
echo -e "REAL_DEBRID_API_KEY=<your_api_key>\nTVDB_API_KEY=<your_api_key>" > .api_keys
```

Run
```
main.py
```

## TODO

- ability to search directly from torrent sites or switch to better movie-API
- rest of the scrapers 
- ui improvements
- better source filtering
- refactor code to be more clear
- popular movies and shows on the front page
