# 📺 Pluto TV Auto-Generated M3U Playlist & EPG

[![Auto Update Playlist & EPG](https://github.com/sulthanpamenan/pluto-playlist/actions/workflows/auto_update.yml/badge.svg)](https://github.com/sulthanpamenan/pluto-playlist/actions/workflows/auto_update.yml)
[![GitHub Pages](https://img.shields.io/badge/GitHub%20Pages-Active-success?logo=github)](https://sulthanpamenan.github.io/pluto-playlist/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Status](https://img.shields.io/badge/Live%20TV-Active-blue)](#-key-features)

A free, automated M3U playlist and EPG XMLTV generator for **Pluto TV** live channels. This repository uses **GitHub Actions** to fetch fresh Pluto TV JWT session tokens and update channels and program guide data every 3 hours for seamless playback on IPTV players.

---

## 🔗 Ready-to-Use Playlist & EPG URLs

Use these links directly in your preferred IPTV player (OTT Navigator, TiviMate, VLC, etc.):

| Content | URL | Description |
| :--- | :--- | :--- |
| **Playlist (TXT)** *(Recommended)* | `https://sulthanpamenan.github.io/pluto-playlist/playlist.txt` | Standard M3U format with official Pluto TV player parameters |
| **Playlist (M3U)** | `https://sulthanpamenan.github.io/pluto-playlist/playlist.m3u` | Direct `.m3u` extension format for apps requiring specific extensions |
| **EPG (XMLTV)** | `https://sulthanpamenan.github.io/pluto-playlist/epg.xml` | Full Electronic Program Guide XML file containing complete show schedules |

---

## ✨ Key Features

- **🔄 Automated Background Updates (24/7 Cloud):** GitHub Actions automatically regenerates fresh Pluto TV session tokens and updates EPG schedule timelines every **3 hours**.
- **📅 Full Electronic Program Guide (EPG):** Includes complete `<programme>` schedules, show descriptions, and episode information directly linked to `epg.xml`.
- **🌐 VPN-Free Access:** Playlists and EPG are automatically fetched via cloud servers, allowing direct stream playback on client devices.
- **⚡ Broad Compatibility:** Tested and fully compatible with OTT Navigator, TiviMate, IPTV Smarters Pro, VLC Media Player, PotPlayer, Perfect Player, and Televizo.
- **📺 Rich Metadata:** Features channel logos (`tvg-logo`), channel IDs (`tvg-id`), and organized categories (`group-title`).

---

## 🚀 Setup Guides

### 📱 OTT Navigator
1. Open **OTT Navigator** on your device.
2. Go to **Settings** -> **Providers**.
3. Select **Add Provider** -> **M3U Playlist**.
4. Enter the Playlist URL:
   `https://sulthanpamenan.github.io/pluto-playlist/playlist.txt`
5. *(Optional)* If EPG is not loaded automatically, go to **EPG Source** and enter:
   `https://sulthanpamenan.github.io/pluto-playlist/epg.xml`

### 📺 TiviMate
1. Open **TiviMate** -> **Settings** -> **Playlists**.
2. Select **Add Playlist** -> **M3U Playlist**.
3. Choose **URL** and enter: `https://sulthanpamenan.github.io/pluto-playlist/playlist.m3u`
4. On the EPG setup screen, enter the TV Guide URL: `https://sulthanpamenan.github.io/pluto-playlist/epg.xml`
5. Save and enjoy watching!

### 💻 VLC / PotPlayer
1. Open **VLC Media Player**.
2. Press `Ctrl + N` (or go to **Media** -> **Open Network Stream**).
3. Paste the URL: `https://sulthanpamenan.github.io/pluto-playlist/playlist.m3u`
4. Click **Play**.

---

## ⚠️ Disclaimer

- This project is for **educational and personal use only**.
- No media files or video streams are hosted or re-transmitted on this server. All playlist links redirect directly to Pluto TV's official public servers.
- Pluto TV is a registered trademark of Paramount Streaming / Paramount Global. This project is not affiliated with, endorsed by, or connected to Pluto TV or Paramount Global.

---

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.

---

## ☕ Support the Developer

If the **pluto-playlist** project is helpful to you, consider supporting to keep this project maintained and updated!

<div align="center">

### 🇮🇩 Local Donation (QRIS / E-Wallet / Mobile Banking)

<a href="https://saweria.co/sulthanpamenan" target="_blank">
  <img width="290" height="290" alt="Saweria" src="https://github.com/user-attachments/assets/f2846d1f-a391-4daf-9ce5-a48aadc992a0" />
</a>

<br>

*Scan the QRIS code above using GoPay, DANA, OVO, ShopeePay, LinkAja, or Mobile Banking.*

<br>

<a href="https://saweria.co/sulthanpamenan" target="_blank">
  <img src="https://img.shields.io/badge/Saweria-Support_Project-orange?style=for-the-badge&logo=coffee" alt="Support via Saweria">
</a>

---

### 🌐 International Donation

<a href="https://buymeacoffee.com/sulthanpamenan" target="_blank">
  <img src="https://img.shields.io/badge/Buy_Me_A_Coffee-Donate-yellow?style=for-the-badge&logo=buy-me-a-coffee" alt="Buy Me A Coffee">
</a>

</div>
