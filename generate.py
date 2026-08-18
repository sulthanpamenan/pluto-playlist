import requests
import uuid

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
    'Accept': 'application/json',
    'Origin': 'https://pluto.tv',
    'Referer': 'https://pluto.tv/'
}

EPG_URL = "https://sulthanpamenan.github.io/pluto-playlist/epg.xml"

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
    
    token, channels = "", []
    try:
        res = requests.get(boot_url, headers=headers, timeout=15)
        if res.status_code == 200:
            d = res.json()
            token = d.get('sessionToken', '')
            channels = d.get('channels', [])
    except Exception as e:
        print(f"[!] Boot error: {e}")

    if not channels:
        try:
            res_v2 = requests.get("https://api.pluto.tv/v2/channels", headers=headers, timeout=15)
            if res_v2.status_code == 200:
                channels = res_v2.json()
        except Exception:
            pass

    return token, device_id, session_id, client_id, channels

def fetch_vod(token, client_id, device_id, session_id):
    vod_items = []
    if not token:
        return vod_items

    # Fetch VOD Categories V3
    url = f"https://api.pluto.tv/v3/vod/categories?jwt={token}&masterJWTPassthrough=true"
    try:
        res = requests.get(url, headers=headers, timeout=20)
        if res.status_code == 200:
            cats = res.json().get('categories', [])
            for c in cats:
                c_name = c.get('name', 'VOD')
                for item in c.get('items', []):
                    i_id = item.get('_id')
                    name = item.get('name', 'VOD Item')
                    covers = item.get('covers', [])
                    logo = covers[0].get('url', '') if covers else ''
                    
                    # Tambahkan URL VOD HLS Stitcher
                    vod_items.append({
                        'id': f"vod_{i_id}",
                        'name': name,
                        'logo': logo,
                        'group': f"VOD - {c_name}",
                        'stitch_id': i_id
                    })
    except Exception as e:
        print(f"[!] Error VOD: {e}")

    return vod_items

def build_m3u():
    token, device_id, session_id, client_id, channels = get_session()
    
    m3u = [f'#EXTM3U url-tvg="{EPG_URL}"\n']

    # 1. Live TV Streams
    for ch in channels:
        ch_id = ch.get('id') or ch.get('_id')
        if not ch_id:
            continue

        name = ch.get('name', 'Pluto Channel')
        logo = ch.get('logo', '')
        if isinstance(ch.get('colorLogoPNG'), dict):
            logo = ch.get('colorLogoPNG', {}).get('path', '')

        group = ch.get('category', 'Pluto TV')

        link = (
            f"https://cfd-v4-service-channel-stitcher-use1-1.prd.pluto.tv/v2/stitch/hls/channel/{ch_id}/master.m3u8"
            f"?appName=web&appVersion=9.22.0&clientDeviceType=0&clientID={client_id}"
            f"&deviceId={device_id}&deviceMake=chrome&deviceModel=web&deviceType=web"
            f"&marketingRegion=US&sessionID={session_id}&jwt={token}&masterJWTPassthrough=true"
        )

        m3u.append(f'#EXTINF:-1 tvg-id="{ch_id}" tvg-name="{name}" tvg-logo="{logo}" group-title="{group}",{name}')
        m3u.append(link)

    # 2. VOD Items
    vods = fetch_vod(token, client_id, device_id, session_id)
    for v in vods:
        v_link = (
            f"https://cfd-v4-service-vod-stitcher-use1-1.prd.pluto.tv/v2/stitch/hls/episode/{v['stitch_id']}/master.m3u8"
            f"?appName=web&clientID={client_id}&deviceId={device_id}&sessionID={session_id}&jwt={token}"
        )
        m3u.append(f'#EXTINF:-1 tvg-id="{v["id"]}" tvg-name="{v["name"]}" tvg-logo="{v["logo"]}" group-title="{v["group"]}",{v["name"]}')
        m3u.append(v_link)

    content = "\n".join(m3u)
    with open("playlist.m3u", "w", encoding="utf-8") as f:
        f.write(content)
    with open("playlist.txt", "w", encoding="utf-8") as f:
        f.write(content)

    print(f"[SUCCESS] Playlist dibuat dengan {len(channels)} Live Channel & {len(vods)} VOD Item.")

if __name__ == "__main__":
    build_m3u()
