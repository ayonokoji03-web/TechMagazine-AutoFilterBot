import requests
import feedparser
import urllib.parse

async def search_torrent(query: str):
    # Your live GitHub Pages bridge URL
    bridge_url = "https://ayonokoji03-web.github.io/magnet-bridge/?url="
    
    # We still use the backtick trick to close the bot's default error formatting
    results = "`\n\n"
    results += "📌 **HOW TO USE:**\n"
    results += "Tap the link below your movie. It will open a page with a 🚀 button that launches LibreTorrent directly!\n"
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
                magnet = f"magnet:?xt=urn:btih:{infohash}"
                
                # Encodes the magnet link safely into the URL
                encoded_magnet = urllib.parse.quote(magnet, safe='')
                final_link = f"{bridge_url}{encoded_magnet}"
                
                results += f"🔹 **{title}**\n▶️ [Tap here to Download]({final_link})\n\n"
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
                
                encoded_magnet = urllib.parse.quote(magnet_link, safe='')
                final_link = f"{bridge_url}{encoded_magnet}"
                
                results += f"🔹 **{title}**\n▶️ [Tap here to Download]({final_link})\n\n"
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
                
                encoded_magnet = urllib.parse.quote(torrent_link, safe='')
                final_link = f"{bridge_url}{encoded_magnet}"
                
                results += f"🔹 **{title}**\n▶️ [Tap here to Download]({final_link})\n\n"
    except Exception:
        pass
        
    if found:
        results += "`"
        return {"title": query, "source": results}
    
    return None

async def download_file(source_url: str):
    raise Exception(f"Search Results!\n{source_url}")
