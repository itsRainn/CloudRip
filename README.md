# Universal Media Downloader 🎬🎵

A lightweight, customized desktop application built with Python (Tkinter) and built alongside `yt-dlp` and `FFmpeg` to comfortably pull crisp, multi-platform media files.

This is mostly a <ins>**vibecoded program**</ins> (I did make my own fixes to things I do understand) using **Google Gemini** for the goal of bringing people a simple and lightweight program, while having not a lot of knowledge but smart enough to understand code, so people don't have to go onto multiple websites realizing that downloading in HD costs money or that some sites are somewhat sketchy.

This program lets you download videos in **any Resolution, FPS, **and** Audio Bitrate** as **MP4, MKV, MOV,** or **WebM** from sites like *YouTube* and *Medal*! The program also lets you strip the audio from any video in **any bitrate** as **MP3, M4A,** or **WAV** from sites like *YouTube Music* (or just regular *YouTube*) and *Soundcloud*!

Unfortunately, as of now, *Spotify*, *Threads*, and *BiliBili* are <ins>**not supported**</ins> due to certain restrictions. 

As of now, the tested and working websites to use this program on are: 
- *YouTube*
- *YouTube Music*
- *Instagram*
- *Twitch*
- *Medal* (basically *Medal Bypass*)
- *Facebook*
- *SoundCloud*
- *X/Twitter*
- *Twitter*

~~Oh by the way, the Bitrate goes from Lossless (Video/Audio's exisiting default) all the way down to 8kbps~~

---

## ✨ Features

*   **Video Downloader Tab:** Supports pulling multiple resolution ceilings (up to 4K/2K/1080p), tracking target frame rates, and container format mappings (**MP4, MKV, MOV, WEBM**).
*   **Audio Extractor Tab:** Dedicated standalone core strips video layers completely inside the buffer cache to output pure sound files (**MP3, M4A, WAV**).
*   **The Deep-Fried Grid Preset:** Includes dedicated **8 kbps** and **16 kbps** mono distortion presets using standard telephone encoding matrices to give you a crisp, crunchy, perfectly fried lofi sound signature natively.
*   **Lossless Rendering:** Supports raw, untouched direct byte-for-byte stream extraction without re-encoding quality degradation (valid for MKV video wrappers, and M4A/WAV audio tracks).

---

## 📝 Planned Features
* **Support for More Websites/Services:** Self-explanatory.
* **Abort Button:** Be able to abort/stop conversions.

---

## 🛠️ Local Development & Script Execution

### Prerequisites

Ensure you have **Python 3.10+** installed on your system environment.

### 1. Clone & Set Up Directory Workspace
```bash
git clone https://github.com
cd UnivMediaDldr
```

### 2. Install Python Core Dependencies
```bash
pip install yt-dlp
```

### 3. Add External Executable Binary Dependencies
To run the raw code script locally or compile the source engine via command-line arguments, you must place your static binaries and graphics files directly in the root project directory side-by-side:
*   **`ffmpeg.exe`** (Static binary extracted from the Gyan.dev release `/bin` folder directory).
*   **`ffprobe.exe`** (Static binary extracted from the Gyan.dev release `/bin` folder directory).
*   **`icon.ico`** (Your custom app logo graphic layer file asset).

### 4. Run the Interface Application Script
```bash
python main.py
```
```json
{
  "version": "1.1.0",
  "url": "https://github.com"
}
```

## License
Open-source, free to use, modify, or redistribute for educational and non-commercial purposes, with credit required. Reselling (original or modified) is forbidden. See our full terms in [LICENSE.md](LICENSE.md)
