import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
import requests

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/152.0.0.0 Safari/537.36',
    'Accept': 'application/json'
}

MIRROR_EPG_URL = "https://raw.githubusercontent.com/matthuisman/i.mjh.nz/master/PlutoTV/us.xml"

def clean_xml_text(val):
    if not val:
        return ""
    val_str = str(val)
    return "".join(ch for ch in val_str if (
        ch in ("\t", "\n", "\r") or
        (0x20 <= ord(ch) <= 0xD7FF) or
        (0xE000 <= ord(ch) <= 0xFFFD) or
        (0x10000 <= ord(ch) <= 0x10FFFF)
    )).strip()

def format_xmltv_date(dt_str):
    try:
        dt = datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
        return dt.strftime("%Y%m%d%H%M%S +0000")
    except Exception:
        return ""

def fetch_pluto_timelines():
    """Fetch 24-hour EPG timelines from Pluto TV v3 API"""
    now = datetime.now(timezone.utc)
    start_time = now.strftime("%Y-%m-%dT%H:00:00.000Z")
    stop_time = (now + timedelta(hours=24)).strftime("%Y-%m-%dT%H:00:00.000Z")
    
    url = f"https://api.pluto.tv/v3/trending/timelines?start={start_time}&stop={stop_time}"
    try:
        res = requests.get(url, headers=HEADERS, timeout=20)
        if res.status_code == 200:
            return res.json().get('data', [])
    except Exception as e:
        print(f"[!] Error fetching v3 timelines: {e}")
    return []

def generate_pluto_epg():
    print("[*] Starting Pluto TV EPG generation process...")
    channels = []
    
    # 1. Direct Pluto TV API channel request
    try:
        res = requests.get("https://api.pluto.tv/v2/channels", headers=HEADERS, timeout=15)
        if res.status_code == 200:
            channels = res.json()
            print(f"[✓] Successfully fetched {len(channels)} channels via API.")
    except Exception as e:
        print(f"[!] Direct API fetch error: {e}")

    # 2. Fallback mirror if channels API completely fails
    if not channels:
        print("[*] Downloading EPG from public mirror fallback...")
        try:
            res_mirror = requests.get(MIRROR_EPG_URL, timeout=30)
            if res_mirror.status_code == 200:
                with open("epg.xml", "wb") as f:
                    f.write(res_mirror.content)
                    f.flush()
                print("[SUCCESS] File `epg.xml` successfully updated via public mirror!")
                return
        except Exception as e:
            print(f"[!] Mirror fetch error: {e}")
            return

    # 3. Fetch Timelines data
    print("[*] Fetching Pluto TV EPG Timelines...")
    timelines_data = fetch_pluto_timelines()
    
    # Mapping timelines based on channel ID
    timelines_map = {}
    for t_item in timelines_data:
        c_id = t_item.get('channelId') or t_item.get('id')
        if c_id:
            timelines_map[str(c_id)] = t_item.get('timelines', [])

    # 4. Building the XMLTV Structure
    tv_elem = ET.Element("tv", {"generator-info-name": "PlutoTV EPG Generator"})
    p_count = 0

    for ch in channels:
        ch_id = str(ch.get('id') or ch.get('_id') or '').strip()
        if not ch_id:
            continue

        ch_elem = ET.SubElement(tv_elem, "channel", id=ch_id)
        disp_name = ET.SubElement(ch_elem, "display-name")
        disp_name.text = clean_xml_text(ch.get('name', 'Pluto Channel'))

        logo = ch.get('logo', '')
        if isinstance(ch.get('colorLogoPNG'), dict):
            logo = ch.get('colorLogoPNG', {}).get('path', '')
        if logo:
            ET.SubElement(ch_elem, "icon", src=clean_xml_text(logo))

        # Get timelines from map or channel object fallback
        timelines = timelines_map.get(ch_id, ch.get('timelines', []))

        for item in timelines:
            title_text = clean_xml_text(item.get('title', ''))
            if not title_text:
                continue

            desc_text = item.get('episode', {}).get('description', '') if isinstance(item.get('episode'), dict) else item.get('description', f"Broadcast of {title_text}")
            desc_text = clean_xml_text(desc_text)
            
            start_xml = format_xmltv_date(item.get('start', ''))
            stop_xml = format_xmltv_date(item.get('stop', ''))

            if start_xml and stop_xml:
                prog_elem = ET.SubElement(tv_elem, "programme", {
                    "start": start_xml,
                    "stop": stop_xml,
                    "channel": ch_id
                })
                ET.SubElement(prog_elem, "title", lang="en").text = title_text
                ET.SubElement(prog_elem, "desc", lang="en").text = desc_text
                p_count += 1

    # 5. Fallback to public mirror if no programme elements were parsed
    if p_count == 0:
        print("[!] No programs parsed. Falling back to public mirror EPG...")
        try:
            res_mirror = requests.get(MIRROR_EPG_URL, timeout=30)
            if res_mirror.status_code == 200:
                with open("epg.xml", "wb") as f:
                    f.write(res_mirror.content)
                    f.flush()
                print("[SUCCESS] File `epg.xml` updated via public mirror fallback!")
                return
        except Exception as e:
            print(f"[!] Mirror fetch error: {e}")
            return

    try:
        ET.indent(tv_elem, space="  ")
    except AttributeError:
        pass

    tree = ET.ElementTree(tv_elem)
    with open("epg.xml", "wb") as f:
        tree.write(f, encoding="utf-8", xml_declaration=True)
        f.flush()

    print(f"[SUCCESS] File `epg.xml` generated successfully with {p_count} programs.")

if __name__ == "__main__":
    generate_pluto_epg()
