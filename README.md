# 📺 Pluto TV Auto-Generated M3U Playlist

[![Auto Update Playlist](https://github.com/sulthanpamenan/pluto-playlist/actions/workflows/auto_update.yml/badge.svg)](https://github.com/sulthanpamenan/pluto-playlist/actions/workflows/auto_update.yml)
[![GitHub Pages](https://img.shields.io/badge/GitHub%20Pages-Active-success?logo=github)](https://sulthanpamenan.github.io/pluto-playlist/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Status](https://img.shields.io/badge/Channels-400%2B%20Live-blue)](#-fitur-utama)

Layanan pembuat daftar putar (*playlist*) M3U gratis untuk siaran langsung **Pluto TV**. Repository ini menggunakan **GitHub Actions** untuk mengekstrak token JWT resmi dan memperbarui daftar saluran secara otomatis setiap 3 jam sekali agar dapat langsung diputar di berbagai aplikasi pemutar IPTV tanpa terkendala *geoblock* atau token kedaluwarsa.

---

## 🔗 URL Playlist Siap Pakai

Gunakan salah satu URL di bawah ini pada aplikasi IPTV pilihan Anda (OTT Navigator, TiviMate, VLC, dll):

| Format | URL Playlist | Keterangan |
| :--- | :--- | :--- |
| **TXT / M3U** *(Disarankan)* | `https://sulthanpamenan.github.io/pluto-playlist/playlist.txt` | Format standar M3U8 dengan parameter pemutar resmi Pluto TV |
| **M3U File Direct** | `https://sulthanpamenan.github.io/pluto-playlist/playlist.m3u` | Format `.m3u` untuk aplikasi yang mewajibkan ekstensi M3U |

---

## ✨ Fitur Utama

- **🔄 Auto-Update Latar Belakang (Cloud 24/7):** GitHub Actions memperbarui token JWT resmi Pluto TV secara otomatis setiap **3 jam sekali**.
- **🌐 Bebas VPN:** Proses generasi playlist dilakukan langsung melalui server GitHub US, sehingga tayangan dapat diakses langsung tanpa perlu menyalakan VPN di perangkat Anda.
- **⚡ Kompatibilitas Luas:** Mendukung berbagai aplikasi IPTV populer seperti OTT Navigator, TiviMate, IPTV Smarters Pro, VLC Media Player, PotPlayer, dan Perfect Player.
- **📺 Metadata Lengkap:** Dilengkapi dengan EPG ID (`tvg-id`), Logo Saluran Berwarna (`tvg-logo`), serta Kategori Saluran Lengkap (`group-title`).

---

## 🚀 Cara Penggunaan di OTT Navigator

1. Buka aplikasi **OTT Navigator** di Smart TV, Android TV, atau HP Anda.
2. Masuk ke menu **Pengaturan** (Settings) $\rightarrow$ **Penyedia** (Providers).
3. Pilih **Tambahkan Penyedia** (Add Provider) $\rightarrow$ **Playlist M3U**.
4. Masukkan URL berikut:
   ```text
   [https://sulthanpamenan.github.io/pluto-playlist/playlist.txt](https://sulthanpamenan.github.io/pluto-playlist/playlist.txt)
