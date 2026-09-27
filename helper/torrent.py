async def search_torrent(query: str):
    # Generates a test result matching the query
    mock_title = f"📁 {query} (Test Dispatcher Mode)"
    
    # Official, open-source Ubuntu desktop ISO test magnet
    mock_magnet = "magnet:?xt=urn:btih:3b245504cf5f11bbdbe1201cea6a6bf45aee1bc0&dn=ubuntu-22.04.3-desktop-amd64.iso"
    
    return {"title": mock_title, "source": mock_magnet}

async def download_file(source_url: str):
    # Halts container downloading and routes the magnet text to the chat
    raise Exception(
        f"🧲 **Tap the link below to copy it:**\n\n"
        f"`{source_url}`\n\n"
        f"💡 *Paste this into LibreTorrent to start downloading!*"
    )
