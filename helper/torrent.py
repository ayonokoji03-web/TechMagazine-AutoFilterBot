import os
import asyncio
import aiohttp
import tarfile
import stat
import urllib.parse

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
        async with session.get(tar_url) as resp:
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
    url = f"https://yts.mx/api/v2/list_movies.json?query_term={urllib.parse.quote(query)}&sort_by=seeds&limit=1"
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, timeout=10) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    movies = data.get("data", {}).get("movies")
                    if movies and movies[0].get("torrents"):
                        movie = movies[0]
                        best = max(movie["torrents"], key=lambda x: x.get("seeds", 0))
                        return {"title": f"{movie['title']} ({movie['year']})", "source": best.get("url")}
        except Exception: pass
    return None

async def download_file(source_url: str):
    aria_bin = await ensure_aria2()
    cmd = [aria_bin, "--follow-torrent=mem", "--seed-time=0", f"--dir={DOWNLOAD_DIR}", source_url]
    proc = await asyncio.create_subprocess_exec(*cmd)
    await proc.communicate()
    for root, _, files in os.walk(DOWNLOAD_DIR):
        for file in files:
            if file.endswith(('.mkv', '.mp4', '.avi')):
                return os.path.join(root, file)
    raise FileNotFoundError("Download failed.")
