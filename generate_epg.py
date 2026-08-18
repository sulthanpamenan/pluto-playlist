import requests
import xml.etree.ElementTree as ET
from xml.dom import minidom
from datetime import datetime

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'application/json'
}

def format_xmltv_date(dt_str):
    try:
        dt = datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
        return dt.strftime("%Y%m%d%H%M%S +0000")
    except Exception:
        return ""

def generate_pluto_epg():
    print("[*] Mengambil data jadwal EPG dari Pluto TV...")
    
    # Menembak langsung endpoint v2 channels yang berisi struktur timeline lengkap
    url = "https://api.pluto.tv/v2/channels"
    channels = []
    try:
        res = requests.get(url, headers=headers, timeout=20)
        if res.status_code == 200:
            channels = res.json()
            print(f"[✓] Berhasil menarik data dari {len(channels)} channel.")
    except Exception as e:
        print(f"[!] Error: {e}")
        return

    tv_elem = ET.Element("tv", {"generator-info-name": "PlutoTV EPG Generator"})

    channel_count = 0
    programme_count = 0

    for ch in channels:
        ch_id = ch.get('id') or ch.get('_id')
        if not ch_id:
            continue

        ch_elem = ET.SubElement(tv_elem, "channel", id=ch_id)
        disp_name = ET.SubElement(ch_elem, "display-name")
        disp_name.text = ch.get('name', 'Pluto Channel')

        logo = ch.get('logo', '')
        if isinstance(ch.get('colorLogoPNG'), dict):
            logo = ch.get('colorLogoPNG', {}).get('path', '')
        if logo:
            ET.SubElement(ch_elem, "icon", src=logo)

        channel_count += 1

        # Ambil daftar program tayang
        timelines = ch.get('timelines', [])
        for item in timelines:
            title_text = item.get('title', '')
            if not title_text:
                continue

            desc_text = item.get('episode', {}).get('description', '') if isinstance(item.get('episode'), dict) else item.get('description', '')
            if not desc_text:
                desc_text = f"Siaran {title_text}"

            start_xml = format_xmltv_date(item.get('start', ''))
            stop_xml = format_xmltv_date(item.get('stop', ''))

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

    rough_string = ET.tostring(tv_elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    
    with open("epg.xml", "w", encoding="utf-8") as f:
        f.write(reparsed.toprettyxml(indent="  "))

    print(f"[SUCCESS] File `epg.xml` berhasil diperbarui ({channel_count} channel, {programme_count} acara).")

if __name__ == "__main__":
    generate_pluto_epg()
