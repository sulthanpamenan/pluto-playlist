import requests
import json

# Headers lengkap agar dianggap sebagai browser valid di wilayah US
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
    'Accept': 'application/json',
    'X-Forwarded-For': '185.220.101.5',
    'CF-IPCountry': 'US'
}

def get_pluto_channels():
    channels = []
    token = ""

    # Percobaan 1: Menggunakan API Boot v4
    try:
        boot_url = (
            "https://boot.pluto.tv/v4/start"
            "?appName=web&appVersion=9.22.0"
            "&clientDeviceType=0&deviceMake=chrome&deviceModel=web&deviceType=web"
            "&marketingRegion=US&serverSideAds=false"
        )
        res = requests.get(boot_url, headers=headers, timeout=15)
        if res.status_code == 200:
            data = res.json()
            token = data.get('sessionToken', '')
            channels = data.get('channels', [])
    except Exception as e:
        print(f"Boot API Error: {e}")

    # Percobaan 2: Fallback ke API v2 jika v4 kosong
    if not channels:
        try:
            print("Memakai API v2 Fallback...")
            v2_url = "https://api.pluto.tv/v2/channels"
            res_v2 = requests.get(v2_url, headers=headers, timeout=15)
            if res_v2.status_code == 200:
                channels = res_v2.json()
        except Exception as e:
            print(f"V2 API Error: {e}")

    return token, channels

def build_m3u():
    token, channels = get_pluto_channels()
    m3u_lines = ["#EXTM3U"]

    for ch in channels:
        # Penanganan ID dari berbagai versi API Pluto
        ch_id = ch.get('id') or ch.get('_id')
        if not ch_id:
            continue

        name = ch.get('name', 'Pluto Channel')
        
        # Penanganan struktur Logo
        logo = ''
        if isinstance(ch.get('colorLogoPNG'), dict):
            logo = ch.get('colorLogoPNG', {}).get('path', '')
        elif isinstance(ch.get('logo'), str):
            logo = ch.get('logo')

        group = ch.get('category', 'Pluto TV')

        # Format URL Stitcher
        stream_link = (
            f"https://cfd-v4-service-channel-stitcher-use1-1.prd.pluto.tv/v2/stitch/hls/channel/{ch_id}/master.m3u8"
            f"?appName=web&appVersion=9.22.0&clientDeviceType=0&deviceMake=chrome&deviceModel=web&deviceType=web"
            f"&serverSideAds=false&jwt={token}&masterJWTPassthrough=true"
        )

        m3u_lines.append(f'#EXTINF:-1 tvg-id="{ch_id}" tvg-name="{name}" tvg-logo="{logo}" group-title="{group}",{name}')
        m3u_lines.append(stream_link)

    playlist_content = "\n".join(m3u_lines)
    
    with open("playlist.txt", "w", encoding="utf-8") as f:
        f.write(playlist_content)
        
    print(f"Berhasil menukarkan {len(channels)} saluran ke playlist.txt!")

if __name__ == "__main__":
    build_m3u()
