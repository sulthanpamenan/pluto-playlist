# 📺 Pluto TV Auto-Generated M3U Playlist

[![Auto Update Playlist](https://github.com/sulthanpamenan/pluto-playlist/actions/workflows/auto_update.yml/badge.svg)](https://github.com/sulthanpamenan/pluto-playlist/actions/workflows/auto_update.yml)
[![GitHub Pages](https://img.shields.io/badge/GitHub%20Pages-Active-success?logo=github)](https://sulthanpamenan.github.io/pluto-playlist/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Status](https://img.shields.io/badge/Channels-400%2B%20Live-blue)](#-key-features)

A free, automated M3U playlist generator for **Pluto TV** live channels. This repository uses **GitHub Actions** to extract official JWT tokens and update channel lists every 3 hours, allowing seamless playback on IPTV players without geoblocks or expired tokens.

---

## 🔗 Ready-to-Use Playlist URLs

Use either of the following URLs in your preferred IPTV app (OTT Navigator, TiviMate, VLC, etc.):

| Format | Playlist URL | Description |
| :--- | :--- | :--- |
| **TXT / M3U** *(Recommended)* | `https://sulthanpamenan.github.io/pluto-playlist/playlist.txt` | Standard M3U8 format containing official Pluto TV player parameters |
| **M3U File Direct** | `https://sulthanpamenan.github.io/pluto-playlist/playlist.m3u` | Direct `.m3u` file format for applications requiring M3U extension |

---

## ✨ Key Features

- **🔄 Automated Background Updates (24/7 Cloud):** GitHub Actions automatically fetches fresh Pluto TV JWT tokens every **3 hours**.
- **🌐 VPN-Free Access:** Playlists are generated via US-based GitHub servers, allowing direct playback on client devices without requiring a VPN.
- **⚡ Broad Compatibility:** Tested and compatible with popular IPTV apps such as OTT Navigator, TiviMate, IPTV Smarters Pro, VLC Media Player, PotPlayer, and Perfect Player.
- **📺 Rich Metadata:** Includes EPG IDs (`tvg-id`), color logos (`tvg-logo`), and complete channel categories (`group-title`).

---

## 🚀 Setup Guide for OTT Navigator

1. Open **OTT Navigator** on your Smart TV, Android TV, or Mobile device.
2. Go to **Settings** $\rightarrow$ **Providers**.
3. Select **Add Provider** $\rightarrow$ **M3U Playlist**.
4. Enter the URL:
   ```text
   [https://sulthanpamenan.github.io/pluto-playlist/playlist.txt](https://sulthanpamenan.github.io/pluto-playlist/playlist.txt)
