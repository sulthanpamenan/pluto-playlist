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
    try:
        dt = datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
        return dt.strftime("%Y%m%d%H%M%S +0000")
    except Exception:
        return ""

def generate_pluto_epg():
    print("[*] Mengambil data EPG Pluto TV...")
    
    device_id = str(uuid.uuid4())
    session_id = str(uuid.uuid4())
    client_id = str(uuid.uuid4())
    
    # 1. Ambil Session Token
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

    if not channels:
        try:
            res_v2 = requests.get("https://api.pluto.tv/v2/channels", headers=headers, timeout=15)
            if res_v2.status_code == 200:
                channels = res_v2.json()
        except Exception as e:
            print(f"[!] Error channels: {e}")

    # 2. Ambil Guide Timeline via V3 Grid
    now_utc = datetime.now(timezone.utc)
    start_iso = now_utc.strftime("%Y-%m-%dT%H:00:00.000Z")
    stop_iso = (now_utc + timedelta(hours=8)).strftime("%Y-%m-%dT%H:00:00.000Z")
    
    guide_url = f"https://api.pluto.tv/v3/guide/timelines?start={start_iso}&stop={stop_iso}"
    if token:
        guide_url += f"&jwt={token}"

    epg_data = []
    try:
        res_g = requests.get(guide_url, headers=headers, timeout=20)
        if res_g.status_code == 200:
            epg_data = res_g.json().get('channels', [])
    except Exception as e:
        print(f"[!] Error fetch guide: {e}")

    timeline_map = {c.get('id'): c.get('timelines', []) for c in epg_data}

    # 3. Susun XMLTV
    tv_elem = ET.Element("tv", {"generator-info-name": "PlutoTV EPG Generator"})

    p_count = 0
    for ch in channels:
        ch_id = ch.get('id') or ch.get('_id')
        if not ch_id:
            continue

        ch_elem = ET.SubElement(tv_elem, "channel", id=ch_id)
        d_name = ET.SubElement(ch_elem, "display-name")
        d_name.text = ch.get('name', 'Pluto Channel')

        logo = ch.get('logo', '')
        if isinstance(ch.get('colorLogoPNG'), dict):
            logo = ch.get('colorLogoPNG', {}).get('path', '')
        if logo:
            ET.SubElement(ch_elem, "icon", src=logo)

        timelines = timeline_map.get(ch_id, []) or ch.get('timelines', [])
        for t in timelines:
            title = t.get('title', '')
            if not title:
                continue

            desc = t.get('episode', {}).get('description', '') if isinstance(t.get('episode'), dict) else t.get('description', '')
            if not desc:
                desc = f"Program {title}"

            start_xml = format_xmltv_date(t.get('start', ''))
            stop_xml = format_xmltv_date(t.get('stop', ''))

            if start_xml and stop_xml:
                p_elem = ET.SubElement(tv_elem, "programme", {
                    "start": start_xml,
                    "stop": stop_xml,
                    "channel": ch_id
                })
                t_elem = ET.SubElement(p_elem, "title", lang="en")
                t_elem.text = title
                d_elem = ET.SubElement(p_elem, "desc", lang="en")
                d_elem.text = desc
                p_count += 1

    rough_str = ET.tostring(tv_elem, 'utf-8')
    reparsed = minidom.parseString(rough_str)
    
    with open("epg.xml", "w", encoding="utf-8") as f:
        f.write(reparsed.toprettyxml(indent="  "))

    print(f"[SUCCESS] epg.xml terisi ({len(channels)} channel, {p_count} acara).")

if __name__ == "__main__":
    generate_pluto_epg()
