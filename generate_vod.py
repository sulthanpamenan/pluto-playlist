import requests
import uuid

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
    'Accept': 'application/json',
    'Origin': 'https://pluto.tv',
    'Referer': 'https://pluto.tv/'
}

def get_session():
    device_id = str(uuid.uuid4())
    session_id = str(uuid.uuid4())
    client_id = str(uuid.uuid4())
    
    boot_url = (
        f"https://boot.pluto.tv/v4/start"
        f"?appName=web&appVersion=9.22.0&clientDeviceType=0&clientID={client_id}"
        f"&deviceId={device_id}&deviceMake=chrome&deviceModel=web&deviceType=web"
        f"&marketingRegion=US&sessionID={session_id}"
    )
    
    token = ""
    try:
        res = requests.get(boot_url, headers=headers, timeout=15)
        if res.status_code == 200:
            token = res.json().get('sessionToken', '')
            print(f"[✓] Session VOD berhasil didapatkan.")
    except Exception as e:
        print(f"[!] Error VOD Boot: {e}")

    return token, device_id, session_id, client_id

def build_vod_m3u():
    token, device_id, session_id, client_id = get_session()
    if not token:
        print("[!] Gagal mendapatkan token VOD, proses dibatalkan.")
        return

    m3u_lines = [
        "#EXTM3U",
        "<!-- PLUTO VOD ON-DEMAND PLAYLIST -->\n"
    ]

    vod_url = f"https://api.pluto.tv/v3/vod/categories?jwt={token}&masterJWTPassthrough=true"
    item_count = 0

    try:
        res = requests.get(vod_url, headers=headers, timeout=20)
        if res.status_code == 200:
            categories = res.json().get('categories', [])
            for cat in categories:
                cat_name = cat.get('name', 'Pluto VOD')
                for item in cat.get('items', []):
                    item_id = item.get('_id')
                    name = item.get('name', 'VOD Item')
                    covers = item.get('covers', [])
                    logo = covers[0].get('url', '') if covers else ''

                    stream_link = (
                        f"https://cfd-v4-service-vod-stitcher-use1-1.prd.pluto.tv/v2/stitch/hls/episode/{item_id}/master.m3u8"
                        f"?appName=web&clientID={client_id}&deviceId={device_id}&sessionID={session_id}&jwt={token}"
                    )

                    m3u_lines.append(f'#EXTINF:-1 tvg-id="vod_{item_id}" tvg-name="{name}" tvg-logo="{logo}" group-title="VOD - {cat_name}",{name}')
                    m3u_lines.append(stream_link)
                    item_count += 1
    except Exception as e:
        print(f"[!] Gagal mengekstrak VOD: {e}")

    content = "\n".join(m3u_lines)
    
    # Simpan khusus ke playlist VOD terpisah
    with open("vod_playlist.m3u", "w", encoding="utf-8") as f:
        f.write(content)

    with open("vod_playlist.txt", "w", encoding="utf-8") as f:
        f.write(content)

    print(f"[SUCCESS] Berhasil membuat `vod_playlist.m3u` dengan {item_count} item VOD.")

if __name__ == "__main__":
    build_vod_m3u()
