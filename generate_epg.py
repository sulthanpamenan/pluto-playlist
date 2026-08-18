import requests
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
    try:
        dt = datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
        return dt.strftime("%Y%m%d%H%M%S +0000")
    except Exception:
        return ""

def generate_pluto_epg():
    print("[*] Mengambil data EPG langsung dari endpoint channel...")
    
    # Endpoint v2 yang menyajikan data channel beserta array 'timelines' bawaan
    url = "https://api.pluto.tv/v2/channels"
    channels = []
    
    try:
        res = requests.get(url, headers=headers, timeout=25)
        if res.status_code == 200:
            channels = res.json()
            print(f"[✓] Berhasil menarik {len(channels)} channel EPG.")
    except Exception as e:
        print(f"[!] Error EPG fetch: {e}")
        return

    tv_elem = ET.Element("tv", {"generator-info-name": "PlutoTV EPG Generator"})

    channel_count = 0
    programme_count = 0

    for ch in channels:
        ch_id = ch.get('id') or ch.get('_id')
        if not ch_id:
            continue

        # Tag <channel>
        ch_elem = ET.SubElement(tv_elem, "channel", id=ch_id)
        disp_name = ET.SubElement(ch_elem, "display-name")
        disp_name.text = ch.get('name', 'Pluto Channel')

        logo = ''
        if isinstance(ch.get('colorLogoPNG'), dict):
            logo = ch.get('colorLogoPNG', {}).get('path', '')
        elif isinstance(ch.get('logo'), str):
            logo = ch.get('logo')

        if logo:
            ET.SubElement(ch_elem, "icon", src=logo)

        channel_count += 1

        # Tag <programme> (Jadwal Acara)
        timelines = ch.get('timelines', [])
        for item in timelines:
            title_text = item.get('title', '')
            if not title_text:
                continue

            desc_text = ""
            if isinstance(item.get('episode'), dict):
                desc_text = item.get('episode', {}).get('description', '')
            if not desc_text:
                desc_text = item.get('description', f"Siaran {title_text}")

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

    rough_str = ET.tostring(tv_elem, 'utf-8')
    reparsed = minidom.parseString(rough_str)
    
    with open("epg.xml", "w", encoding="utf-8") as f:
        f.write(reparsed.toprettyxml(indent="  "))

    print(f"[SUCCESS] File `epg.xml` berhasil dibuat ({channel_count} channel, {programme_count} acara terdaftar).")

if __name__ == "__main__":
    generate_pluto_epg()
