# 🎥 Advanced YouTube Downloader with Streamlit

[![Python](https://img.shields.io/badge/python-3.7%2B-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/built%20with-Streamlit-orange)](https://streamlit.io)
[![yt-dlp](https://img.shields.io/badge/yt--dlp-supported-yellowgreen)](https://github.com/yt-dlp/yt-dlp)
[![License: MIT](https://img.shields.io/badge/license-MIT-lightgrey.svg)](LICENSE)

> A **modern, elegant YouTube video downloader** — powered by [Streamlit](https://streamlit.io) and [yt-dlp](https://github.com/yt-dlp/yt-dlp) — supporting high-quality downloads (360p to 4K), audio-only extraction, and automatic merging with FFmpeg.

---
---

## ✨ Features

- ✅ One-click downloads for any YouTube video
- 🎞️ Quality selection: 360p, 720p, 1080p, 4K, etc.
- 🔄 Automatic video+audio merging via FFmpeg
- 🎵 Audio-only extraction (MP3/AAC/Opus)
- 🧠 Smart format selection (best quality & size)
- 📊 Live download progress and status
- 💡 Clear error messages and troubleshooting tips
- 🖥️ No command line or coding required

---

## 🏗️ Architecture Overview

```plaintext
Streamlit UI (you_dlp.py)
│
├── Paste URL → Validate → Fetch Metadata
├── Show Available Formats
├── Select Format & Merge Option
├── Download Logic
│   ├── Complete (Single File)
│   ├── Video+Audio → Merge (FFmpeg)
│   └── Video & Audio → Separate Files
└── Save to ~/Downloads/YouTube_Downloads
```

---

## 🎮 Getting Started

### 📦 Requirements

- Python 3.7+
- [yt-dlp](https://github.com/yt-dlp/yt-dlp)
- [Streamlit](https://streamlit.io/)
- [FFmpeg](https://ffmpeg.org/) (recommended for merging)

---

### 🔧 Installation

```bash
# 1. Clone the repository
git clone https://github.com/your-username/youtube-downloader.git
cd youtube-downloader

# 2. Install dependencies
pip install -r requirements.txt

# 3. (Optional) Install FFmpeg and add it to your system PATH
```

---

### ▶️ Usage

```bash
streamlit run you_dlp.py
```

- The app will open in your browser.
- Paste a YouTube video URL.
- Select quality and merge option.
- Click **Start Download**.
- Files are saved to:

```bash
~/Downloads/YouTube_Downloads/
```

---

## 📚 User Guide

1. Paste the YouTube URL.
2. Select desired video quality (e.g. 1080p).
3. Choose merge option (auto or separate).
4. Start the download — watch live progress.
5. Done! Enjoy your video/audio 🎉

> 🧠 **Note**: YouTube serves high-quality formats (720p+) as separate video and audio. This app merges them automatically using FFmpeg.

---

## 🧪 Developer Notes

- URL validation via regex
- Format sorting by resolution & bitrate
- Merge behavior toggle (auto / merge / separate)
- Safe filename sanitization
- Cross-platform download support
- Logging and exception handling

---

## 🩺 Troubleshooting

| Issue                     | Solution                                              |
|--------------------------|--------------------------------------------------------|
| ❌ No formats found       | Ensure the video URL is valid and publicly accessible |
| ❌ FFmpeg not found       | Install FFmpeg and add it to your system PATH         |
| ❌ Format unavailable     | Try selecting a different quality                     |
| ❌ App not opening        | Ensure Streamlit is installed correctly               |

---

## 📜 License

**MIT License** — See [`LICENSE`](LICENSE) for full details.

> 🔒 This project is for **educational and personal use only**. Please respect YouTube’s [Terms of Service](https://www.youtube.com/t/terms).

---

## 🙌 Acknowledgements

- [Streamlit](https://streamlit.io/)
- [yt-dlp](https://github.com/yt-dlp/yt-dlp)
- [FFmpeg](https://ffmpeg.org/)

---

**Crafted with  by [Ahsan Zubair]([https://github.com/your-username](https://github.com/ahsanzubair172/YouTube-video-Downloader))**
