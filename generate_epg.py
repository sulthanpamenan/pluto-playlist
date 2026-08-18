import requests
import uuid
import xml.etree.ElementTree as ET
from xml.dom import minidom
from datetime import datetime

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
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
    
    # 1. Ambil session token dan daftar channel
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
    except Exception as e:
        print(f"[!] Error boot: {e}")
        return

    # 2. Ambil timeline EPG (jadwal acara 8 jam ke depan)
    start_time = datetime.utcnow().strftime("%Y-%m-%dT%H:00:00.000Z")
    guide_url = f"https://api.pluto.tv/v3/guide/timelines?start={start_time}&duration=480&jwt={token}"
    
    epg_data = {}
    try:
        g_res = requests.get(guide_url, headers=headers, timeout=20)
        if g_res.status_code == 200:
            epg_data = g_res.json()
    except Exception as e:
        print(f"[!] Error fetching guide: {e}")

    # 3. Susun XMLTV Struktur
    tv_elem = ET.Element("tv", {"generator-info-name": "PlutoTV EPG Generator"})

    # Tambahkan Tag <channel>
    for ch in channels:
        ch_id = ch.get('id') or ch.get('_id')
        if not ch_id:
            continue
        
        ch_elem = ET.SubElement(tv_elem, "channel", id=ch_id)
        disp_name = ET.SubElement(ch_elem, "display-name")
        disp_name.text = ch.get('name', '')
        
        logo = ch.get('logo', '')
        if isinstance(ch.get('colorLogoPNG'), dict):
            logo = ch.get('colorLogoPNG', {}).get('path', '')
        if logo:
            ET.SubElement(ch_elem, "icon", src=logo)

    # Tambahkan Tag <programme> (Jadwal Acara)
    for timeline_ch in epg_data.get('channels', []):
        ch_id = timeline_ch.get('id')
        for timelines in timeline_ch.get('timelines', []):
            title_text = timelines.get('title', '')
            desc_text = timelines.get('episode', {}).get('description', f"Program {title_text}")
            start_iso = timelines.get('start', '')
            stop_iso = timelines.get('stop', '')
            
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

    # Simpan ke file epg.xml
    rough_string = ET.tostring(tv_elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    pretty_xml = reparsed.toprettyxml(indent="  ")

    with open("epg.xml", "w", encoding="utf-8") as f:
        f.write(pretty_xml)

    print(f"[SUCCESS] File `epg.xml` Pluto TV berhasil dibuat!")

if __name__ == "__main__":
    generate_pluto_epg()
