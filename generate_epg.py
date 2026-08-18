import requests
import uuid
import xml.etree.ElementTree as ET
from xml.dom import minidom
from datetime import datetime, timezone

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
    'Accept': 'application/json',
    'Origin': 'https://pluto.tv',
    'Referer': 'https://pluto.tv/'
}

def format_xmltv_date(dt_str):
    """Mengubah format ISO date Pluto ke XMLTV format."""
    try:
        dt = datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
        return dt.strftime("%Y%m%d%H%M%S +0000")
    except Exception:
        return ""

def generate_pluto_epg():
    print("[*] Mengambil data jadwal EPG dari Pluto TV...")
    
    device_id = str(uuid.uuid4())
    session_id = str(uuid.uuid4())
    client_id = str(uuid.uuid4())
    
    # 1. Ambil session token dari endpoint start Pluto TV
    boot_url = (
        f"https://boot.pluto.tv/v4/start"
        f"?appName=web&appVersion=9.22.0&clientDeviceType=0&clientID={client_id}"
        f"&deviceId={device_id}&deviceMake=chrome&deviceModel=web&deviceType=web"
        f"&marketingRegion=US&sessionID={session_id}"
    )
    
    token = ""
    channels = []
    try:
        res = requests.get(boot_url, headers=headers, timeout=15)
        if res.status_code == 200:
            data = res.json()
            token = data.get('sessionToken', '')
            channels = data.get('channels', [])
            print(f"[✓] Berhasil mengambil {len(channels)} channel dari Pluto TV.")
    except Exception as e:
        print(f"[!] Error boot: {e}")

    # Fallback mengambil channel jika boot_url tidak mengembalikan channels
    if not channels:
        try:
            res_v2 = requests.get("https://api.pluto.tv/v2/channels", headers=headers, timeout=15)
            if res_v2.status_code == 200:
                channels = res_v2.json()
        except Exception as e:
            print(f"[!] Error fetching fallback channels: {e}")

    # 2. Ambil timeline EPG (Jadwal Acara)
    # Gunakan rentang waktu UTC saat ini
    now = datetime.now(timezone.utc)
    start_time = now.strftime("%Y-%m-%dT%H:00:00.000Z")
    
    # Coba request EPG dari V3 Timelines
    guide_url = f"https://api.pluto.tv/v3/guide/timelines?start={start_time}&duration=480"
    if token:
        guide_url += f"&jwt={token}"
        
    epg_channels_data = []
    try:
        g_res = requests.get(guide_url, headers=headers, timeout=20)
        if g_res.status_code == 200:
            epg_channels_data = g_res.json().get('channels', [])
            print(f"[✓] Berhasil mengambil EPG timeline untuk {len(epg_channels_data)} channel.")
        else:
            print(f"[!] Warning: Guide API merespon status {g_res.status_code}")
    except Exception as e:
        print(f"[!] Error fetching guide: {e}")

    # 3. Susun XMLTV Struktur
    tv_elem = ET.Element("tv", {"generator-info-name": "PlutoTV EPG Generator"})

    # Map EPG channel ke dictionary agar mudah dicari
    timeline_map = {ch.get('id'): ch.get('timelines', []) for ch in epg_channels_data}

    # Tag <channel> & <programme>
    channel_count = 0
    programme_count = 0

    for ch in channels:
        ch_id = ch.get('id') or ch.get('_id')
        if not ch_id:
            continue
        
        # Tambahkan elemen <channel>
        ch_elem = ET.SubElement(tv_elem, "channel", id=ch_id)
        disp_name = ET.SubElement(ch_elem, "display-name")
        disp_name.text = ch.get('name', 'Pluto Channel')
        
        logo = ch.get('logo', '')
        if isinstance(ch.get('colorLogoPNG'), dict):
            logo = ch.get('colorLogoPNG', {}).get('path', '')
        if logo:
            ET.SubElement(ch_elem, "icon", src=logo)

        channel_count += 1

        # Ambil timeline acara untuk channel ini
        timelines = timeline_map.get(ch_id, [])
        
        # Jika API v3 tidak mengembalikan timeline channel ini, pakai data 'timelines' bawaan objek channel (v2)
        if not timelines and 'timelines' in ch:
            timelines = ch.get('timelines', [])

        for item in timelines:
            title_text = item.get('title', '')
            if not title_text:
                continue

            desc_text = item.get('episode', {}).get('description', f"Program {title_text}")
            if not desc_text and 'title' in item:
                desc_text = item.get('title')

            start_iso = item.get('start', '')
            stop_iso = item.get('stop', '')
            
            start_xml = format_xmltv_date(start_iso)
            stop_xml = format_xmltv_date(stop_iso)
            
            if start_xml and stop_xml:
                prog_elem = ET.SubElement(tv_elem, "programme", {
                    "start": start_xml,
                    "stop": stop_xml,
                    "channel": ch_id
                })
                t_elem = ET.SubElement(prog_elem, "title", lang="en")
                t_elem.text = title_text
                d_elem = ET.SubElement(prog_elem, "desc", lang="en")
                d_elem.text = desc_text
                programme_count += 1

    # Simpan ke file epg.xml
    rough_string = ET.tostring(tv_elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    pretty_xml = reparsed.toprettyxml(indent="  ")

    with open("epg.xml", "w", encoding="utf-8") as f:
        f.write(pretty_xml)

    print(f"[SUCCESS] Selesai! `epg.xml` berhasil diperbarui ({channel_count} channel, {programme_count} acara).")

if __name__ == "__main__":
    generate_pluto_epg()
