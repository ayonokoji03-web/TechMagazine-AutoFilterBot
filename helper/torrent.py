import feedparser
import urllib.parse
import aiohttp
import asyncio
import re

async def search_torrent(query: str):
    bridge_url = "https://ayonokoji03-web.github.io/magnet-bridge/?url="
    results_text = "`\n\n📌 **HOW TO USE:**\nTap the link below your movie. It will open a page with a 🚀 button that launches LibreTorrent directly!\n━━━━━━━━━━━━━━━━━━━━━━\n\n"
    
    target_results = 15
    current_results = 0
    found_any = False
    
    safe_query = urllib.parse.quote(query)
    
    # 1. Search TorrentCSV (Fetch 40 results to ensure a good pool to sort)
    csv_url = f"https://torrents-csv.com/service/search?q={safe_query}&size=40"
    try:
        timeout = aiohttp.ClientTimeout(total=10)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(csv_url) as resp:
                if resp.status == 200:
                    csv_data = await resp.json()
                    torrents = csv_data.get("torrents", [])
                    
                    # Sort torrents by highest seeders first
                    torrents = sorted(torrents, key=lambda x: int(x.get('seeders', 0)), reverse=True)
                    
                    if torrents:
                        results_text += "🎬 **Movies (TorrentCSV):**\n\n"
                        for t in torrents:
                            if current_results >= target_results: break
                            
                            seeders = int(t.get('seeders', 0))
                            if seeders == 0: continue # Skip dead links entirely
                            
                            title = t.get('name', 'Unknown')
                            infohash = t.get('infohash', '')
                            magnet = f"magnet:?xt=urn:btih:{infohash}"
                            encoded = urllib.parse.quote(magnet, safe='')
                            results_text += f"🔹 **{title}** (🌱 {seeders})\n▶️ [Tap here to Download]({bridge_url}{encoded})\n\n"
                            current_results += 1
                            found_any = True
    except Exception as e:
        print(f"CSV Error: {e}")

    # 2. Nyaa
    if current_results < target_results:
        nyaa_url = f"https://nyaa.si/?page=rss&q={safe_query}"
        try:
            feed = await asyncio.to_thread(feedparser.parse, nyaa_url) 
            if feed.entries:
                # Sort Nyaa entries by their dedicated seeders tag
                sorted_nyaa = sorted(feed.entries, key=lambda x: int(x.get('nyaa_seeders', 0)), reverse=True)
                
                results_text += "🌸 **Anime (Nyaa):**\n\n"
                for entry in sorted_nyaa:
                    if current_results >= target_results: break
                    
                    seeds = int(entry.get('nyaa_seeders', 0))
                    if seeds == 0: continue # Skip dead links
                    
                    encoded = urllib.parse.quote(entry.link, safe='')
                    results_text += f"🔹 **{entry.title}** (🌱 {seeds})\n▶️ [Tap here to Download]({bridge_url}{encoded})\n\n"
                    current_results += 1
                    found_any = True
        except Exception as e:
            print(f"Nyaa Error: {e}")

    # 3. LimeTorrents
    if current_results < target_results:
        lime_url = f"https://www.limetorrents.lol/searchrss/{safe_query}/"
        try:
            lime_feed = await asyncio.to_thread(feedparser.parse, lime_url)
            if lime_feed.entries:
                
                # Function to extract seeders from LimeTorrents description text
                def get_lime_seeds(entry):
                    match = re.search(r'Seeds\s*:\s*(\d+)', getattr(entry, 'description', ''))
                    return int(match.group(1)) if match else 0
                
                # Sort by highest seeders
                sorted_lime = sorted(lime_feed.entries, key=get_lime_seeds, reverse=True)
                
                if sorted_lime:
                    results_text += "🍋 **Classics (LimeTorrents):**\n\n"
                    for entry in sorted_lime:
                        if current_results >= target_results: break
                        
                        seeds = get_lime_seeds(entry)
                        if seeds == 0: continue # Skip dead links
                        
                        torrent_link = entry.link
                        if hasattr(entry, 'enclosures') and len(entry.enclosures) > 0:
                            torrent_link = entry.enclosures[0].href
                        encoded = urllib.parse.quote(torrent_link, safe='')
                        results_text += f"🔹 **{entry.title}** (🌱 {seeds})\n▶️ [Tap here to Download]({bridge_url}{encoded})\n\n"
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
