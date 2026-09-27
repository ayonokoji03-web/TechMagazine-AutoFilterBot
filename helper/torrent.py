import os
import shutil
import asyncio
import aiohttp
import tarfile
import stat
import urllib.parse
import json

DOWNLOAD_DIR = "/tmp/downloads"
ARIA2_DIR = "/tmp/aria2"
ARIA2_PATH = os.path.join(ARIA2_DIR, "aria2c")

os.makedirs(DOWNLOAD_DIR, exist_ok=True)
os.makedirs(ARIA2_DIR, exist_ok=True)

async def ensure_aria2():
    if os.path.exists(ARIA2_PATH): return ARIA2_PATH
    system_aria = os.popen("which aria2c").read().strip()
    if system_aria: return system_aria
    tar_url = "https://github.com/q3aql/aria2-static-builds/releases/download/v1.36.0/aria2-1.36.0-linux-gnu-64bit-build1.tar.bz2"
    tar_path = "/tmp/aria2.tar.bz2"
    async with aiohttp.ClientSession() as session:
        async with session.get(tar_url, ssl=False) as resp:
            with open(tar_path, "wb") as f: f.write(await resp.read())
    with tarfile.open(tar_path, "r:bz2") as tar:
        for member in tar.getmembers():
            if member.name.endswith("aria2c"):
                member.name = os.path.basename(member.name)
                tar.extract(member, path=ARIA2_DIR)
                break
    os.chmod(ARIA2_PATH, stat.S_IRWXU | stat.S_IRGRP | stat.S_IXGRP)
    return ARIA2_PATH

async def search_torrent(query: str):
    # We use a public CORS Proxy to completely hide Render's IP and bypass Cloudflare
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

    try:
        async with aiohttp.ClientSession(headers=headers) as session:
            # 1. Try YTS via Proxy
            yts_url = f"https://yts.mx/api/v2/list_movies.json?query_term={urllib.parse.quote(query)}&sort_by=seeds&limit=1"
            proxy_url = f"https://api.allorigins.win/get?url={urllib.parse.quote(yts_url)}"

            async with session.get(proxy_url, timeout=15) as resp:
                if resp.status == 200:
                    proxy_data = await resp.json()
                    try:
                        real_json = json.loads(proxy_data.get("contents", "{}"))
                        movies = real_json.get("data", {}).get("movies")
                        if movies:
                            movie = movies[0]
                            best = max(movie["torrents"], key=lambda x: x.get("seeds", 0))
                            title = f"{movie['title']} ({movie['year']})"
                            return {"title": title, "source": best.get("url")}
                    except:
                        pass # Silently fallback to PirateBay if YTS fails

            # 2. Fallback to PirateBay via Proxy
            pb_url = f"https://apibay.org/q.php?q={urllib.parse.quote(query)}&cat=200"
            pb_proxy = f"https://api.allorigins.win/get?url={urllib.parse.quote(pb_url)}"

            async with session.get(pb_proxy, timeout=15) as pb_resp:
                if pb_resp.status != 200:
                    raise Exception("Proxy rejected the connection.")

                pb_proxy_data = await pb_resp.json()
                
                try:
                    pb_json = json.loads(pb_proxy_data.get("contents", "[]"))
                except:
                    raise Exception("Cloudflare blocked the Proxy Middleman.")

                if not pb_json or (isinstance(pb_json, list) and pb_json[0].get("id") == "0"):
                    raise Exception(f"'{query}' not found in any database.")

                valid_results = [item for item in pb_json if int(item.get("seeders", 0)) > 0]
                if not valid_results:
                    raise Exception("Found it, but nobody is seeding it.")

                best = sorted(valid_results, key=lambda x: int(x.get("seeders", 0)), reverse=True)[0]
                title = best.get("name")
                magnet = f"magnet:?xt=urn:btih:{best.get('info_hash')}&dn={urllib.parse.quote(title)}&tr=udp%3A%2F%2Ftracker.opentrackr.org%3A1337"
                return {"title": title, "source": magnet}

    except asyncio.TimeoutError:
        raise Exception("Search timed out.")
    except Exception as e:
        raise Exception(str(e))

async def download_file(source_url: str):
    if os.path.exists(DOWNLOAD_DIR):
        shutil.rmtree(DOWNLOAD_DIR)
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)

    aria_bin = await ensure_aria2()
    cmd = [
        aria_bin,
        "--seed-time=0",
        "--bt-stop-timeout=300",
        f"--dir={DOWNLOAD_DIR}",
        source_url
    ]
    proc = await asyncio.create_subprocess_exec(*cmd)
    await proc.communicate()
    
    video_files = []
    for root, _, files in os.walk(DOWNLOAD_DIR):
        for file in files:
            if file.endswith(('.mkv', '.mp4', '.avi', '.webm')):
                video_files.append(os.path.join(root, file))
                
    if video_files:
        return max(video_files, key=os.path.getsize)
        
    raise Exception("Download failed or got stuck.")
