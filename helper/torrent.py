import requests
import feedparser

def search_fallback_torrents(query):
    results = ""
    
    # 1. Search TorrentCSV for Hollywood & Indian Films
    csv_url = f"https://torrents-csv.com/service/search?q={query}&size=3"
    try:
        csv_data = requests.get(csv_url, timeout=5).json()
        if "torrents" in csv_data and len(csv_data["torrents"]) > 0:
            results += "🎬 **Movie Results:**\n"
            for t in csv_data["torrents"]:
                title = t.get('name', 'Unknown')
                infohash = t.get('infohash', '')
                results += f"🔹 {title}\n🧲 `magnet:?xt=urn:btih:{infohash}`\n\n"
    except Exception as e:
        print(f"TorrentCSV error: {e}")

    # 2. Search Nyaa RSS for Anime
    nyaa_url = f"https://nyaa.si/?page=rss&q={query}"
    try:
        feed = feedparser.parse(nyaa_url)
        if feed.entries:
            results += "🌸 **Anime Results:**\n"
            for entry in feed.entries[:3]:
                title = entry.title
                magnet_link = entry.link
                results += f"🔹 {title}\n🧲 `{magnet_link}`\n\n"
    except Exception as e:
        print(f"Nyaa error: {e}")
        
    return results if results else "No files found in the channel or fallback torrent databases."
