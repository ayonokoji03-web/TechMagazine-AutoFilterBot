import aiohttp
import urllib.parse

async def search_torrent(query: str):
    # Query the public YTS movie API
    api_url = f"https://yts.mx/api/v2/list_movies.json?query_term={urllib.parse.quote(query)}&limit=1"
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(api_url) as response:
                if response.status != 200:
                    return None
                
                data = await response.json()
                
                # Check if the movie exists in the results
                if not data.get("data") or not data["data"].get("movies"):
                    return None
                
                movie = data["data"]["movies"][0]
                title = movie.get("title_long", "Unknown Title")
                
                # Extract the torrent hash for the highest seeded quality
                torrents = movie.get("torrents", [])
                if not torrents:
                    return None
                    
                torrent_hash = torrents[0]["hash"]
                safe_title = urllib.parse.quote(title)
                
                # Construct the copyable magnet link
                magnet_link = f"magnet:?xt=urn:btih:{torrent_hash}&dn={safe_title}"
                
                return {
                    "title": f"🎬 {title}",
                    "source": magnet_link
                }
    except Exception:
        return None

async def download_file(source_url: str):
    # Halt the cloud download and dispatch the link to the Telegram chat
    raise Exception(
        f"🧲 **Tap the link below to copy it:**\n\n"
        f"`{source_url}`\n\n"
        f"💡 *Paste this into LibreTorrent to start downloading!*"
    )
