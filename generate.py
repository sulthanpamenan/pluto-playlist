import requests
import uuid
import json

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
    'Accept': 'application/json',
    'Origin': 'https://pluto.tv',
    'Referer': 'https://pluto.tv/'
}

def get_jwt_token():
    """Mengambil JWT Token otentikasi menggunakan UUID anonim resmi Pluto TV"""
    token = ""
    device_id = str(uuid.uuid4())
    
    # Endpoint Auth resmi Pluto TV untuk membuat Session JWT Token baru
    auth_url = f"https://boot.pluto.tv/v1/auth/local?appName=web&appVersion=9.22.0&deviceId={device_id}&deviceMake=chrome&deviceModel=web&deviceType=web"
    
    try:
        res = requests.get(auth_url, headers=headers, timeout=12)
        if res.status_code == 200 or res.status_code == 201:
            data = res.json()
            token = data.get('sessionToken', '')
            if token:
                print(f"[SUCCESS] Token JWT berhasil didapat: {token[:25]}...")
    except Exception as e:
        print(f"[ERROR] Gagal mendapatkan JWT Token: {e}")

    # Fallback Auth jika endpoint v1 tidak memberikan response
    if not token:
        try:
            boot_url = "https://boot.pluto.tv/v4/start?appName=web&appVersion=9.22.0&clientDeviceType=0&deviceMake=chrome&deviceModel=web&deviceType=web"
            res_boot = requests.get(boot_url, headers=headers, timeout=12)
            if res_boot.status_code == 200:
                token = res_boot.json().get('sessionToken', '')
        except Exception as e:
            print(f"[ERROR] Fallback Auth Error: {e}")
            
    return token

def get_channels():
    """Mengambil daftar seluruh saluran Pluto TV"""
    try:
        res = requests.get("https://api.pluto.tv/v2/channels", headers=headers, timeout=15)
        if res.status_code == 200:
            return res.json()
    except Exception as e:
        print(f"[ERROR] Fetch Channels Error: {e}")
    return []

def build_m3u():
    token = get_jwt_token()
    channels = get_channels()
    
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

        # Format URL Stitcher Lengkap dengan JWT Token
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
        
    print(f"[SUCCESS] Berhasil memperbarui playlist.txt (Total: {len(channels)} saluran)!")

if __name__ == "__main__":
    build_m3u()
