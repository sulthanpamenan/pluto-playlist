import requests

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
    'Accept': 'application/json',
    'X-Forwarded-For': '185.220.101.5',
    'CF-IPCountry': 'US'
}

def build_m3u():
    channels = []
    
    # Ambil daftar channel langsung dari API v2
    try:
        res = requests.get("https://api.pluto.tv/v2/channels", headers=headers, timeout=15)
        if res.status_code == 200:
            channels = res.json()
    except Exception as e:
        print(f"Error: {e}")

    m3u_lines = ["#EXTM3U"]

    for ch in channels:
        ch_id = ch.get('id') or ch.get('_id')
        if not ch_id:
            continue

        name = ch.get('name', 'Pluto Channel')
        
        # Penanganan Logo
        logo = ''
        if isinstance(ch.get('colorLogoPNG'), dict):
            logo = ch.get('colorLogoPNG', {}).get('path', '')
        elif isinstance(ch.get('logo'), str):
            logo = ch.get('logo')

        group = ch.get('category', 'Pluto TV')

        # Link Stream Murni Bebas JWT (Ringkas, Pendek, dan Tidak Akan Terpotong/Spasi)
        stream_link = f"https://service-stitcher.clusters.pluto.tv/v1/stitch/embed/hls/channel/{ch_id}/master.m3u8?deviceType=web"

        m3u_lines.append(f'#EXTINF:-1 tvg-id="{ch_id}" tvg-name="{name}" tvg-logo="{logo}" group-title="{group}",{name}')
        m3u_lines.append(stream_link)

    playlist_content = "\n".join(m3u_lines)
    
    with open("playlist.txt", "w", encoding="utf-8") as f:
        f.write(playlist_content)
        
    print(f"Berhasil membuat playlist (Total: {len(channels)} saluran)!")

if __name__ == "__main__":
    build_m3u()
