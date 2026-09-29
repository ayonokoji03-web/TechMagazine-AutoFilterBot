import feedparser
import urllib.parse
import aiohttp
import asyncio

async def search_torrent(query: str):
    bridge_url = "https://ayonokoji03-web.github.io/magnet-bridge/?url="
    base_header = "`\n\n📌 **HOW TO USE:**\nTap the link below your movie. It will open a page with a 🚀 button that launches LibreTorrent directly!\n━━━━━━━━━━━━━━━━━━━━━━\n\n"
    
    timeout = aiohttp.ClientTimeout(total=10)
    
    async with aiohttp.ClientSession(timeout=timeout) as session:
        
        # 1. Search TorrentCSV First
        csv_url = f"https://torrents-csv.com/service/search?q={query}&size=15"
        try:
            async with session.get(csv_url) as resp:
                if resp.status == 200:
                    csv_data = await resp.json()
                    if "torrents" in csv_data and len(csv_data["torrents"]) > 0:
                        results = base_header + "🎬 **Movies (TorrentCSV):**\n\n"
                        # We use [:15] here to ensure it safely stops at 15 results
                        for t in csv_data["torrents"][:15]: 
                            title = t.get('name', 'Unknown')
                            infohash = t.get('infohash', '')
                            magnet = f"magnet:?xt=urn:btih:{infohash}"
                            encoded_magnet = urllib.parse.quote(magnet, safe='')
                            results += f"🔹 **{title}**\n▶️ [Tap here to Download]({bridge_url}{encoded_magnet})\n\n"
                        results += "`"
                        return {"title": query, "source": results} # Returns immediately!
        except Exception as e:
            print(f"CSV Error: {e}")

        # 2. If CSV found nothing (or crashed), fallback to Nyaa
        nyaa_url = f"https://nyaa.si/?page=rss&q={query}"
        try:
            async with session.get(nyaa_url) as resp:
                if resp.status == 200:
                    xml_data = await resp.text()
                    feed = feedparser.parse(xml_data) 
                    if feed.entries:
                        results = base_header + "🌸 **Anime (Nyaa):**\n\n"
                        for entry in feed.entries[:15]:
                            encoded_magnet = urllib.parse.quote(entry.link, safe='')
                            results += f"🔹 **{entry.title}**\n▶️ [Tap here to Download]({bridge_url}{encoded_magnet})\n\n"
                        results += "`"
                        return {"title": query, "source": results} # Returns immediately!
        except Exception as e:
            print(f"Nyaa Error: {e}")

        # 3. If Nyaa also found nothing, fallback to LimeTorrents
        lime_url = f"https://www.limetorrents.lol/searchrss/{query}/"
        try:
            async with session.get(lime_url) as resp:
                if resp.status == 200:
                    xml_data = await resp.text()
                    lime_feed = feedparser.parse(xml_data)
                    if lime_feed.entries:
                        results = base_header + "🍋 **Classics (LimeTorrents):**\n\n"
                        for entry in lime_feed.entries[:15]:
                            torrent_link = entry.link
                            if hasattr(entry, 'enclosures') and len(entry.enclosures) > 0:
                                torrent_link = entry.enclosures[0].href
                            encoded_magnet = urllib.parse.quote(torrent_link, safe='')
                            results += f"🔹 **{entry.title}**\n▶️ [Tap here to Download]({bridge_url}{encoded_magnet})\n\n"
                        results += "`"
                        return {"title": query, "source": results} # Returns immediately!
        except Exception as e:
            print(f"Lime Error: {e}")

    # If ALL THREE sites fail to find anything, return None to trigger your bot's "Not found" message
    return None

async def download_file(source_url: str):
    raise Exception(f"Search Results!\n{source_url}")
