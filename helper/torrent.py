import requests
import feedparser

async def search_torrent(query: str):
    # Closes bot's default formatting and adds an easy instruction guide for users
    results = "`\n\n"
    results += "📌 **HOW TO USE:**\n"
    results += "1. Find your preferred quality (1080p, 720p, etc.) below.\n"
    results += "2. Tap directly on the link box to copy it instantly.\n"
    results += "3. Paste it into LibreTorrent, TorrDroid, or your torrent app to download!\n\n"
    results += "━━━━━━━━━━━━━━━━━━━━━━\n\n"
    
    found = False
    
    # 1. Search TorrentCSV for Hollywood & Indian Films
    csv_url = f"https://torrents-csv.com/service/search?q={query}&size=3"
    try:
        csv_data = requests.get(csv_url, timeout=5).json()
        if "torrents" in csv_data and len(csv_data["torrents"]) > 0:
            found = True
            results += "🎬 **Movies (TorrentCSV):**\n\n"
            for t in csv_data["torrents"]:
                title = t.get('name', 'Unknown')
                infohash = t.get('infohash', '')
                results += f"🔹 **{title}**\n👉 Tap to copy:\n`magnet:?xt=urn:btih:{infohash}`\n\n"
    except Exception:
        pass

    # 2. Search Nyaa RSS for Anime
    nyaa_url = f"https://nyaa.si/?page=rss&q={query}"
    try:
        feed = feedparser.parse(nyaa_url)
        if feed.entries:
            found = True
            results += "🌸 **Anime (Nyaa):**\n\n"
            for entry in feed.entries[:3]:
                title = entry.title
                magnet_link = entry.link
                results += f"🔹 **{title}**\n👉 Tap to copy:\n`{magnet_link}`\n\n"
    except Exception:
        pass

    # 3. Search LimeTorrents RSS for Classics & Underrated Films
    lime_url = f"https://www.limetorrents.lol/searchrss/{query}/"
    try:
        lime_feed = feedparser.parse(lime_url)
        if lime_feed.entries:
            found = True
            results += "🍋 **Classics (LimeTorrents):**\n\n"
            for entry in lime_feed.entries[:3]:
                title = entry.title
                torrent_link = entry.link
                if hasattr(entry, 'enclosures') and len(entry.enclosures) > 0:
                    torrent_link = entry.enclosures[0].href
                
                results += f"🔹 **{title}**\n👉 Tap to copy:\n`{torrent_link}`\n\n"
    except Exception:
        pass
        
    if found:
        # Closing backtick to match the opening error block
        results += "`"
        return {"title": query, "source": results}
    
    return None

async def download_file(source_url: str):
    raise Exception(f"Search Results!\n{source_url}")
