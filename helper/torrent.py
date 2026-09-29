import feedparser
import urllib.parse
import aiohttp
import asyncio

async def search_torrent(query: str):
    bridge_url = "https://ayonokoji03-web.github.io/magnet-bridge/?url="
    results_text = "`\n\n📌 **HOW TO USE:**\nTap the link below your movie. It will open a page with a 🚀 button that launches LibreTorrent directly!\n━━━━━━━━━━━━━━━━━━━━━━\n\n"
    
    target_results = 15
    current_results = 0
    found_any = False
    
    # 1. Search TorrentCSV (This part was working fine)
    csv_url = f"https://torrents-csv.com/service/search?q={query}&size=15"
    try:
        timeout = aiohttp.ClientTimeout(total=10)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(csv_url) as resp:
                if resp.status == 200:
                    csv_data = await resp.json()
                    torrents = csv_data.get("torrents", [])
                    if torrents:
                        results_text += "🎬 **Movies (TorrentCSV):**\n\n"
                        for t in torrents:
                            if current_results >= target_results: break
                            title = t.get('name', 'Unknown')
                            infohash = t.get('infohash', '')
                            magnet = f"magnet:?xt=urn:btih:{infohash}"
                            encoded = urllib.parse.quote(magnet, safe='')
                            results_text += f"🔹 **{title}**\n▶️ [Tap here to Download]({bridge_url}{encoded})\n\n"
                            current_results += 1
                            found_any = True
    except Exception as e:
        print(f"CSV Error: {e}")

    # 2. Nyaa (Restored to your original working feedparser method)
    if current_results < target_results:
        nyaa_url = f"https://nyaa.si/?page=rss&q={query}"
        try:
            # Runs your original code in the background so it doesn't cause a 502 error
            feed = await asyncio.to_thread(feedparser.parse, nyaa_url) 
            if feed.entries:
                results_text += "🌸 **Anime (Nyaa):**\n\n"
                for entry in feed.entries:
                    if current_results >= target_results: break
                    encoded = urllib.parse.quote(entry.link, safe='')
                    results_text += f"🔹 **{entry.title}**\n▶️ [Tap here to Download]({bridge_url}{encoded})\n\n"
                    current_results += 1
                    found_any = True
        except Exception as e:
            print(f"Nyaa Error: {e}")

    # 3. LimeTorrents (Restored to your EXACT original working method)
    if current_results < target_results:
        lime_url = f"https://www.limetorrents.lol/searchrss/{query}/"
        try:
            # Runs your original code in the background so it doesn't cause a 502 error
            lime_feed = await asyncio.to_thread(feedparser.parse, lime_url)
            if lime_feed.entries:
                results_text += "🍋 **Classics (LimeTorrents):**\n\n"
                for entry in lime_feed.entries:
                    if current_results >= target_results: break
                    torrent_link = entry.link
                    if hasattr(entry, 'enclosures') and len(entry.enclosures) > 0:
                        torrent_link = entry.enclosures[0].href
                    encoded = urllib.parse.quote(torrent_link, safe='')
                    results_text += f"🔹 **{entry.title}**\n▶️ [Tap here to Download]({bridge_url}{encoded})\n\n"
                    current_results += 1
                    found_any = True
        except Exception as e:
            print(f"Lime Error: {e}")

    if found_any:
        results_text += "`"
        return {"title": query, "source": results_text}
    
    return None

async def download_file(source_url: str):
    raise Exception(f"Search Results!\n{source_url}")
