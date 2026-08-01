import requests
import json

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
    'Accept': 'application/json'
}

def get_jwt_token():
    """Mengambil JWT Token otentikasi resmi dari Pluto TV secara langsung"""
    token = ""
    
    # Method 1: Tembak endpoint anonim Pluto Token
    try:
        auth_url = "https://boot.pluto.tv/v4/start?appName=web&appVersion=9.22.0&clientDeviceType=0&deviceMake=chrome&deviceModel=web&deviceType=web"
        res = requests.get(auth_url, headers=headers, timeout=10)
        if res.status_code == 200:
            token = res.json().get('sessionToken', '')
    except Exception as e:
        print(f"Auth Method 1 Error: {e}")

    # Method 2: Fallback ke session auth v2 jika Method 1 kosong
    if not token:
        try:
            auth_url2 = "https://api.pluto.tv/v2/config"
            res2 = requests.get(auth_url2, headers=headers, timeout=10)
            if res2.status_code == 200:
                token = res2.json().get('sessionToken', '')
        except Exception as e:
            print(f"Auth Method 2 Error: {e}")
            
    return token

def get_channels():
    """Mengambil daftar seluruh saluran Pluto TV"""
    try:
        res = requests.get("https://api.pluto.tv/v2/channels", headers=headers, timeout=15)
        if res.status_code == 200:
            return res.json()
    except Exception as e:
        print(f"Fetch Channels Error: {e}")
    return []

def build_m3u():
    token = get_jwt_token()
    channels = get_channels()
    
    print(f"[INFO] Status JWT Token: {'TERISI (' + token[:20] + '...)' if token else 'KOSONG'}")

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

        # Link Stream M3U8 Lengkap Wajib Terisi JWT
        stream_link = (
            f"https://cfd-v4-service-channel-stitcher-use1-1.prd.pluto.tv/v2/stitch/hls/channel/{ch_id}/master.m3u8"
            f"?appName=web&appVersion=9.22.0&clientDeviceType=0&deviceMake=chrome&deviceModel=web"
            f"&deviceType=web&deviceVersion=123.0.0&includeExtendedEvents=false&serverSideAds=false"
            f"&jwt={token}&masterJWTPassthrough=true"
        )

        m3u_lines.append(f'#EXTINF:-1 tvg-id="{ch_id}" tvg-name="{name}" tvg-logo="{logo}" group-title="{group}",{name}')
        m3u_lines.append(stream_link)

    playlist_content = "\n".join(m3u_lines)
    
    with open("playlist.txt", "w", encoding="utf-8") as f:
        f.write(playlist_content)
        
    print(f"[SUCCESS] Berhasil membuat playlist.txt (Total: {len(channels)} saluran)!")

if __name__ == "__main__":
    build_m3u()
