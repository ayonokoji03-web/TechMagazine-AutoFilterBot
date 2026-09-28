import requests
import feedparser

async def search_torrent(query: str):
    # The first backtick closes the bot's default error formatting for 1-tap copy!
    results = "`\n\n"
    found = False
    
    # 1. Search TorrentCSV for Hollywood & Indian Films
    csv_url = f"https://torrents-csv.com/service/search?q={query}&size=3"
    try:
        csv_data = requests.get(csv_url, timeout=5).json()
        if "torrents" in csv_data and len(csv_data["torrents"]) > 0:
            found = True
            results += "🎬 **Movies (TorrentCSV):**\n"
            for t in csv_data["torrents"]:
                title = t.get('name', 'Unknown')
                infohash = t.get('infohash', '')
                results += f"🔹 **{title}**\n🧲 `magnet:?xt=urn:btih:{infohash}`\n\n"
    except Exception:
        pass

    # 2. Search Nyaa RSS for Anime
    nyaa_url = f"https://nyaa.si/?page=rss&q={query}"
    try:
        feed = feedparser.parse(nyaa_url)
        if feed.entries:
            found = True
            results += "🌸 **Anime (Nyaa):**\n"
            for entry in feed.entries[:3]:
                title = entry.title
                magnet_link = entry.link
                results += f"🔹 **{title}**\n🧲 `{magnet_link}`\n\n"
    except Exception:
        pass

    # 3. Search LimeTorrents RSS for Underrated/Classic Films
    lime_url = f"https://www.limetorrents.lol/searchrss/{query}/"
    try:
        lime_feed = feedparser.parse(lime_url)
        if lime_feed.entries:
            found = True
            results += "🍋 **Classics (LimeTorrents):**\n"
            for entry in lime_feed.entries[:3]:
                title = entry.title
                torrent_link = entry.link
                if hasattr(entry, 'enclosures') and len(entry.enclosures) > 0:
                    torrent_link = entry.enclosures[0].href
                
                results += f"🔹 **{title}**\n🧲 `{torrent_link}`\n\n"
    except Exception:
        pass
        
    if found:
        # The final backtick pairs with the bot's default closing tag
        results += "`"
        return {"title": query, "source": results}
    
    return None

async def download_file(source_url: str):
    # This intentionally "crashes" the download process to instantly print the links
    raise Exception(f"Magnet Links!{source_url}")
