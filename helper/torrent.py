import requests
import feedparser

async def search_torrent(query):
    results = []
    
    # 1. Search TorrentCSV for Hollywood & Indian Films
    csv_url = f"https://torrents-csv.com/service/search?q={query}&size=3"
    try:
        csv_data = requests.get(csv_url, timeout=5).json()
        if "torrents" in csv_data and len(csv_data["torrents"]) > 0:
            for t in csv_data["torrents"]:
                infohash = t.get('infohash', '')
                magnet = f"magnet:?xt=urn:btih:{infohash}"
                results.append({
                    'name': t.get('name', 'Unknown'),
                    'title': t.get('name', 'Unknown'),
                    'size': "Unknown",
                    'seeders': t.get('seeders', 0),
                    'leechers': t.get('leechers', 0),
                    'magnet': magnet,
                    'link': magnet
                })
    except Exception as e:
        print(f"TorrentCSV error: {e}")

    # 2. Search Nyaa RSS for Anime
    nyaa_url = f"https://nyaa.si/?page=rss&q={query}"
    try:
        feed = feedparser.parse(nyaa_url)
        if feed.entries:
            for entry in feed.entries[:3]:
                results.append({
                    'name': entry.title,
                    'title': entry.title,
                    'size': 'Unknown',
                    'seeders': '0',
                    'leechers': '0',
                    'magnet': entry.link,
                    'link': entry.link
                })
    except Exception as e:
        print(f"Nyaa error: {e}")
        
    return results

async def download_file(*args, **kwargs):
    pass
