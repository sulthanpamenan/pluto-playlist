import requests
import json

PLUTO_BOOT_URL = (
    "https://boot.pluto.tv/v4/start"
    "?appName=web&appVersion=9.22.0"
    "&clientDeviceType=0&deviceMake=chrome&deviceModel=web&deviceType=web"
    "&marketingRegion=US&serverSideAds=false"
)

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
    'Accept': 'application/json'
}

def build_m3u():
    try:
        res = requests.get(PLUTO_BOOT_URL, headers=headers, timeout=15)
        if res.status_code == 200:
            data = res.json()
            token = data.get('sessionToken', '')
            channels = data.get('channels', [])
            
            m3u_lines = ["#EXTM3U"]
            for ch in channels:
                ch_id = ch.get('id')
                name = ch.get('name', 'Pluto Channel')
                logo = ch.get('colorLogoPNG', {}).get('path', '')
                group = ch.get('category', 'Pluto TV')
                
                # Stream link langsung menggunakan Pluto Stitcher dengan JWT Token terpasang
                stream_link = (
                    f"https://cfd-v4-service-channel-stitcher-use1-1.prd.pluto.tv/v2/stitch/hls/channel/{ch_id}/master.m3u8"
                    f"?appName=web&appVersion=9.22.0&clientDeviceType=0&deviceMake=chrome&deviceModel=web&deviceType=web"
                    f"&serverSideAds=false&jwt={token}&masterJWTPassthrough=true"
                )
                
                m3u_lines.append(f'#EXTINF:-1 tvg-id="{ch_id}" tvg-name="{name}" tvg-logo="{logo}" group-title="{group}",{name}')
                m3u_lines.append(stream_link)
                
            playlist_content = "\n".join(m3u_lines)
            
            with open("playlist.m3u", "w", encoding="utf-8") as f:
                f.write(playlist_content)
            print(f"Berhasil membuat playlist.m3u dengan {len(channels)} saluran!")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    build_m3u()