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
    print("[*] Mengambil session JWT token untuk EPG...")
    device_id = str(uuid.uuid4())
    session_id = str(uuid.uuid4())
    client_id = str(uuid.uuid4())

    boot_url = (
        f"https://boot.pluto.tv/v4/start"
        f"?appName=web&appVersion=9.22.0-ba99318afe50de3c8a02021f4c92fd52f2c47a00"
        f"&clientDeviceType=0&clientID={client_id}&clientModelNumber=1.0.0"
        f"&deviceId={device_id}&deviceMake=chrome&deviceModel=web&deviceType=web"
        f"&deviceVersion=143.0.0&marketingRegion=US&serverSideAds=false&sessionID={session_id}"
    )

    token = ""
    channels = []
    try:
        res = requests.get(boot_url, headers=headers, timeout=15)
        if res.status_code == 200:
            data = res.json()
            token = data.get('sessionToken', '')
            channels = data.get('channels', [])
            print(f"[✓] Berhasil mendapatkan JWT token EPG: {token[:20]}...")
    except Exception as e:
        print(f"[!] Boot EPG error: {e}")

    # Fallback ke channel v2 jika boot channels kosong
    if not channels:
        try:
            res_v2 = requests.get("https://api.pluto.tv/v2/channels", headers=headers, timeout=15)
            if res_v2.status_code == 200:
                channels = res_v2.json()
        except Exception as e:
            print(f"[!] Fallback error: {e}")

    # Request Timelines Jadwal dengan JWT
    now_utc = datetime.now(timezone.utc)
    start_iso = now_utc.strftime("%Y-%m-%dT%H:00:00.000Z")
    stop_iso = (now_utc + timedelta(hours=12)).strftime("%Y-%m-%dT%H:00:00.000Z")

    guide_url = f"https://api.pluto.tv/v3/guide/timelines?start={start_iso}&stop={stop_iso}"
    if token:
        guide_url += f"&jwt={token}"

    epg_timeline_data = []
    try:
        res_g = requests.get(guide_url, headers=headers, timeout=25)
        if res_g.status_code == 200:
            epg_timeline_data = res_g.json().get('channels', [])
            print(f"[✓] Berhasil menarik jadwal acara untuk {len(epg_timeline_data)} channel.")
        else:
            print(f"[!] Request EPG Timelines gagal dengan status code: {res_g.status_code}")
    except Exception as e:
        print(f"[!] Error request EPG timelines: {e}")

    timeline_map = {c.get('id'): c.get('timelines', []) for c in epg_timeline_data}

    tv_elem = ET.Element("tv", {"generator-info-name": "PlutoTV EPG Generator"})
    channel_count = 0
    programme_count = 0

    for ch in channels:
        ch_id = ch.get('id') or ch.get('_id')
        if not ch_id:
            continue

        ch_elem = ET.SubElement(tv_elem, "channel", id=ch_id)
        d_name = ET.SubElement(ch_elem, "display-name")
        d_name.text = ch.get('name', 'Pluto Channel')

        logo = ''
        if isinstance(ch.get('colorLogoPNG'), dict):
            logo = ch.get('colorLogoPNG', {}).get('path', '')
        elif isinstance(ch.get('logo'), str):
            logo = ch.get('logo')

        if logo:
            ET.SubElement(ch_elem, "icon", src=logo)

        channel_count += 1

        timelines = timeline_map.get(ch_id, []) or ch.get('timelines', [])
        for t in timelines:
            title = t.get('title', '')
            if not title:
                continue

            desc = ""
            if isinstance(t.get('episode'), dict):
                desc = t.get('episode', {}).get('description', '')
            if not desc:
                desc = t.get('description', f"Program {title}")

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
                programme_count += 1

    rough_str = ET.tostring(tv_elem, 'utf-8')
    reparsed = minidom.parseString(rough_str)

    with open("epg.xml", "w", encoding="utf-8") as f:
        f.write(reparsed.toprettyxml(indent="  "))

    print(f"[SUCCESS] File `epg.xml` berhasil diperbarui ({channel_count} channel, {programme_count} acara terdaftar).")

if __name__ == "__main__":
    generate_pluto_epg()
