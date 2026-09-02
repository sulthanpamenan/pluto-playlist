import json
import xml.etree.ElementTree as ET
from datetime import datetime
import requests

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/152.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json",
    "Content-Type": "application/json",
    "Origin": "https://pluto.tv",
    "Referer": "https://pluto.tv/us/watch/live-tv/",
    "apollo-require-preflight": "true",
    "x-apollo-operation-name": "ChannelsMany",
}

MIRROR_EPG_URL = (
    "https://raw.githubusercontent.com/matthuisman/i.mjh.nz/master/PlutoTV/us.xml"
)


def clean_xml_text(val):
    if not val:
        return ""
    val_str = str(val)
    return "".join(
        ch
        for ch in val_str
        if (
            ch in ("\t", "\n", "\r")
            or (0x20 <= ord(ch) <= 0xD7FF)
            or (0xE000 <= ord(ch) <= 0xFFFD)
            or (0x10000 <= ord(ch) <= 0x10FFFF)
        )
    ).strip()


def format_xmltv_date(dt_str):
    try:
        dt = datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
        return dt.strftime("%Y%m%d%H%M%S +0000")
    except Exception:
        return ""


def fetch_graphql_channels():
    """Fetch all channels and listings via Pluto TV GraphQL with pagination"""
    url = "https://pluto.tv/api/tn/video/graphql/"
    all_channels = []
    start = 0
    rows = 100

    extensions_dict = {
        "tnPersistedDocumentHash": (
            "a8c66dc403e590458bf86eff582a5541a7e1986d75ca7543ae2d6fd1e60b2b3a"
        )
    }

    while True:
        variables_dict = {
            "params": {
                "userRegistrationCountry": "US",
                "userState": "ANONYMOUS",
                "packageCode": "NEW_FREE_PACKAGE",
                "userProfileType": "ADULT",
                "billingVendor": "cbscomp",
                "dma": 501,
                "stationId": None,
                "channelCategorySlug": None,
                "platformType": "Desktop",
                "showListing": True,
                "hideChannelsWithoutListings": True,
                "rows": rows,
                "numOfUpcomingListings": 10,
                "filterLockedChannels": False,
                "start": start,
            }
        }

        params = {
            "extensions": json.dumps(extensions_dict),
            "variables": json.dumps(variables_dict),
            "operationName": "ChannelsMany",
        }

        try:
            res = requests.get(url, params=params, headers=HEADERS, timeout=15)
            if res.status_code == 200:
                data = res.json()
                channels = data.get("data", {}).get("channelsMany", [])
                if not channels:
                    break
                all_channels.extend(channels)
                if len(channels) < rows:
                    break
                start += rows
            else:
                break
        except Exception as e:
            print(f"[!] Error fetching GraphQL channels at start={start}: {e}")
            break

    return all_channels


def download_mirror_epg():
    """Fallback handler to download EPG directly from public mirror"""
    print("[*] Downloading EPG from public mirror fallback...")
    try:
        res_mirror = requests.get(MIRROR_EPG_URL, timeout=30)
        if res_mirror.status_code == 200:
            with open("epg.xml", "wb") as f:
                f.write(res_mirror.content)
                f.flush()
            print("[SUCCESS] File `epg.xml` successfully updated via public mirror!")
            return True
    except Exception as e:
        print(f"[!] Mirror fetch error: {e}")
    return False


def generate_pluto_epg():
    print("[*] Starting Pluto TV EPG generation process...")

    # 1. Direct GraphQL API fetch
    channels = fetch_graphql_channels()

    # 2. Build XMLTV if channels and listings exist
    tv_elem = ET.Element("tv", {"generator-info-name": "PlutoTV EPG Generator"})
    p_count = 0

    if channels:
        for ch in channels:
            ch_id = str(ch.get("id") or ch.get("_id") or "").strip()
            if not ch_id:
                continue

            ch_elem = ET.SubElement(tv_elem, "channel", id=ch_id)
            disp_name = ET.SubElement(ch_elem, "display-name")
            disp_name.text = clean_xml_text(ch.get("name", "Pluto Channel"))

            logo = ""
            color_logo = ch.get("colorLogoPNG")
            if isinstance(color_logo, dict):
                logo = color_logo.get("path", "")
            elif isinstance(ch.get("logo"), str):
                logo = ch.get("logo")

            if logo:
                ET.SubElement(ch_elem, "icon", src=clean_xml_text(logo))

            listings = ch.get("listings", [])
            for item in listings:
                title_text = clean_xml_text(item.get("title", ""))
                if not title_text:
                    continue

                desc_text = item.get("description") or f"Broadcast of {title_text}"
                desc_text = clean_xml_text(desc_text)

                start_xml = format_xmltv_date(item.get("start", ""))
                stop_xml = format_xmltv_date(item.get("stop", ""))

                if start_xml and stop_xml:
                    prog_elem = ET.SubElement(tv_elem, "programme", {
                        "start": start_xml,
                        "stop": stop_xml,
                        "channel": ch_id,
                    })
                    ET.SubElement(prog_elem, "title", lang="en").text = title_text
                    ET.SubElement(prog_elem, "desc", lang="en").text = desc_text
                    p_count += 1

    # 3. If GraphQL failed or returned 0 programs due to silent geoblock, fallback to public mirror
    if p_count == 0:
        print("[!] No programs parsed from official API. Triggering fallback...")
        download_mirror_epg()
        return

    # 4. Save XMLTV Output
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
