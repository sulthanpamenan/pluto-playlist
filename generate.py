import requests
import uuid

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
    'Accept': 'application/json',
    'Origin': 'https://pluto.tv',
    'Referer': 'https://pluto.tv/'
}

def get_pluto_session():
    """Mengambil session token resmi dari endpoint boot Pluto TV"""
    device_id = str(uuid.uuid4())
    session_id = str(uuid.uuid4())
    client_id = str(uuid.uuid4())
    
    boot_url = (
        f"https://boot.pluto.tv/v4/start"
        f"?appName=web&appVersion=9.22.0-ba99318afe50de3c8a02021f4c92fd52f2c47a00"
        f"&clientDeviceType=0&clientID={client_id}&clientModelNumber=1.0.0"
        f"&deviceId={device_id}&deviceMake=chrome&deviceModel=web&deviceType=web"
        f"&deviceVersion=143.0.0&marketingRegion=US&serverSideAds=false&sessionID={session_id}"
    )
    
    token = ""
    channels = []
    
    try:
        res = requests.get(boot_url, headers=headers, timeout=15)
        if res.status_code == 200:
            data = res.json()
            token = data.get('sessionToken', '')
            channels = data.get('channels', [])
            print(f"[INFO] Token berhasil diambil: {token[:20]}...")
    except Exception as e:
        print(f"[ERROR] Boot fetch error: {e}")

    # Fallback jika channels kosong
    if not channels:
        try:
            res_v2 = requests.get("https://api.pluto.tv/v2/channels", headers=headers, timeout=15)
            if res_v2.status_code == 200:
                channels = res_v2.json()
        except Exception as e:
            print(f"[ERROR] Channels v2 fetch error: {e}")

    return token, device_id, session_id, client_id, channels

def build_m3u():
    token, device_id, session_id, client_id, channels = get_pluto_session()
    m3u_lines = ["#EXTM3U"]

    for ch in channels:
        ch_id = ch.get('id') or ch.get('_id')
        if not ch_id:
            continue

        name = ch.get('name', 'Pluto Channel')
        
        logo = ''
        if isinstance(ch.get('colorLogoPNG'), dict):
            logo = ch.get('colorLogoPNG', {}).get('path', '')
        elif isinstance(ch.get('logo'), str):
            logo = ch.get('logo')

        group = ch.get('category', 'Pluto TV')

        # Menyusun URL Stitcher persis sesuai struktur pemutar resmi Pluto TV
        stream_link = (
            f"https://cfd-v4-service-channel-stitcher-use1-1.prd.pluto.tv/v2/stitch/hls/channel/{ch_id}/master.m3u8"
            f"?advertisingId=&appName=web&appVersion=9.22.0-ba99318afe50de3c8a02021f4c92fd52f2c47a00"
            f"&app_name=web&clientDeviceType=0&clientID={client_id}&clientModelNumber=1.0.0"
            f"&country=US&deviceDNT=false&deviceId={device_id}&deviceLat=47.3000&deviceLon=-122.3700"
            f"&deviceMake=chrome&deviceModel=web&deviceType=web&deviceVersion=143.0.0"
            f"&marketingRegion=US&serverSideAds=false&sessionID={session_id}&sid={session_id}"
            f"&userId=&jwt={token}&masterJWTPassthrough=true&includeExtendedEvents=true"
        )

        m3u_lines.append(f'#EXTINF:-1 tvg-id="{ch_id}" tvg-name="{name}" tvg-logo="{logo}" group-title="{group}",{name}')
        m3u_lines.append(stream_link)

    playlist_content = "\n".join(m3u_lines)
    
    # Simpan ke playlist.txt
    with open("playlist.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(m3u_lines))

    # Simpan JUGA ke playlist.m3u
    with open("playlist.m3u", "w", encoding="utf-8") as f:
        f.write("\n".join(m3u_lines))
        
    print("[SUCCESS] Berhasil memperbarui playlist.txt dan playlist.m3u!")

if __name__ == "__main__":
    build_m3u()
