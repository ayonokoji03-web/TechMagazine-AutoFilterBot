import requests
import feedparser

async def search_torrent(query: str):
    results = ""
    
    # 1. Search TorrentCSV for Hollywood & Indian Films
    csv_url = f"https://torrents-csv.com/service/search?q={query}&size=3"
    try:
        csv_data = requests.get(csv_url, timeout=5).json()
        if "torrents" in csv_data and len(csv_data["torrents"]) > 0:
            results += "🎬 **Movies:**\n"
            for t in csv_data["torrents"]:
                title = t.get('name', 'Unknown')
                infohash = t.get('infohash', '')
                results += f"🔹 {title}\n🧲 `magnet:?xt=urn:btih:{infohash}`\n\n"
    except Exception:
        pass

    # 2. Search Nyaa RSS for Anime
    nyaa_url = f"https://nyaa.si/?page=rss&q={query}"
    try:
        feed = feedparser.parse(nyaa_url)
        if feed.entries:
            results += "🌸 **Anime:**\n"
            for entry in feed.entries[:3]:
                title = entry.title
                magnet_link = entry.link
                results += f"🔹 {title}\n🧲 `{magnet_link}`\n\n"
    except Exception:
        pass
        
    if results:
        # Wrap our results in the exact dictionary structure the main bot expects
        return {"title": query, "source": results}
    
    return None

async def download_file(source_url: str):
    # Developer Trick: Intentionally throw an error containing our magnet links!
    # pm_filter.py will catch this exception and print it directly in the chat.
    raise Exception(f"Magnet Links!\n\n{source_url}")
