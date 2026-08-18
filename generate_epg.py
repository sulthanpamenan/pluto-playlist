import requests
import uuid
import xml.etree.ElementTree as ET
from xml.dom import minidom
from datetime import datetime, timezone, timedelta

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
    'Accept': 'application/json',
    'Origin': 'https://pluto.tv',
    'Referer': 'https://pluto.tv/'
}

def format_xmltv_date(dt_str):
    """Mengubah format ISO date Pluto ke format standar XMLTV."""
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
    
    # 1. Ambil session token & daftar channel utama
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
            print(f"[✓] Berhasil mengidentifikasi {len(channels)} channel.")
    except Exception as e:
        print(f"[!] Boot fetch error: {e}")

    # Fallback jika boot gagal
    if not channels:
        try:
            res_v2 = requests.get("https://api.pluto.tv/v2/channels", headers=headers, timeout=15)
            if res_v2.status_code == 200:
                channels = res_v2.json()
        except Exception as e:
            print(f"[!] Fallback channels error: {e}")

    # 2. Persiapkan parameter waktu untuk API Guide (Format ISO 8601 UTC)
    now_utc = datetime.now(timezone.utc)
    start_time = now_utc.strftime("%Y-%m-%dT%H:00:00.000Z")
    stop_time = (now_utc + timedelta(hours=12)).strftime("%Y-%m-%dT%H:00:00.000Z")
    
    # 3. Request API Channels/Timelines resmi
    guide_url = f"https://api.pluto.tv/v3/guide/timelines?start={start_time}&stop={stop_time}"
    if token:
        guide_url += f"&jwt={token}"
        
    epg_channels_data = []
    try:
        g_res = requests.get(guide_url, headers=headers, timeout=25)
        if g_res.status_code == 200:
            epg_channels_data = g_res.json().get('channels', [])
            print(f"[✓] Berhasil mengambil timeline EPG untuk {len(epg_channels_data)} channel.")
        else:
            print(f"[!] Guide API merespon status {g_res.status_code}, menggunakan fallback v2.")
    except Exception as e:
        print(f"[!] Guide fetch error: {e}")

    # Map EPG channel ke dictionary berdasarkan ID
    timeline_map = {ch.get('id'): ch.get('timelines', []) for ch in epg_channels_data}

    # 4. Susun struktur XMLTV
    tv_elem = ET.Element("tv", {"generator-info-name": "PlutoTV EPG Generator"})

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

        # Dapatkan daftar acara untuk channel ini
        timelines = timeline_map.get(ch_id, [])
        if not timelines and 'timelines' in ch:
            timelines = ch.get('timelines', [])

        # Tambahkan elemen <programme>
        for item in timelines:
            title_text = item.get('title', '')
            if not title_text:
                continue

            # Menangani berbagai lokasi deskripsi dari JSON Pluto
            desc_text = ""
            if isinstance(item.get('episode'), dict):
                desc_text = item.get('episode', {}).get('description', '')
            elif isinstance(item.get('description'), str):
                desc_text = item.get('description')
            
            if not desc_text:
                desc_text = f"Siaran {title_text} di Pluto TV"

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

    # 5. Simpan Hasil ke File epg.xml
    rough_string = ET.tostring(tv_elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    pretty_xml = reparsed.toprettyxml(indent="  ")

    with open("epg.xml", "w", encoding="utf-8") as f:
        f.write(pretty_xml)

    print(f"[SUCCESS] File `epg.xml` berhasil diperbarui! ({channel_count} channel, {programme_count} acara dimasukkan).")

if __name__ == "__main__":
    generate_pluto_epg()
