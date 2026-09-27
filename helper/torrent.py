import aiohttp
import urllib.parse

async def search_torrent(query: str):
    # Disguise the bot as a standard Chrome web browser to bypass Cloudflare
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept": "application/json"
    }
    
    api_url = f"https://yts.mx/api/v2/list_movies.json?query_term={urllib.parse.quote(query)}&limit=1"
    
    try:
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.get(api_url) as response:
                if response.status != 200:
                    return None
                
                data = await response.json()
                
                if not data.get("data") or not data["data"].get("movies"):
                    return None
                
                movie = data["data"]["movies"][0]
                title = movie.get("title_long", "Unknown Title")
                
                torrents = movie.get("torrents", [])
                if not torrents:
                    return None
                    
                torrent_hash = torrents[0]["hash"]
                safe_title = urllib.parse.quote(title)
                
                magnet_link = f"magnet:?xt=urn:btih:{torrent_hash}&dn={safe_title}"
                
                return {
                    "title": f"🎬 {title}",
                    "source": magnet_link
                }
    except Exception:
        return None

async def download_file(source_url: str):
    raise Exception(
        f"🧲 **Tap the link below to copy it:**\n\n"
        f"`{source_url}`\n\n"
        f"💡 *Paste this into LibreTorrent to start downloading!*"
    )
