#  Advanced YouTube Downloader with Streamlit

[![Python](https://img.shields.io/badge/python-3.7%2B-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/built%20with-Streamlit-orange)](https://streamlit.io)
[![yt-dlp](https://img.shields.io/badge/yt--dlp-supported-yellowgreen)](https://github.com/yt-dlp/yt-dlp)
[![License: MIT](https://img.shields.io/badge/license-MIT-lightgrey.svg)](LICENSE)

> A **modern, elegant YouTube video downloader** — powered by [Streamlit](https://streamlit.io) and [yt-dlp](https://github.com/yt-dlp/yt-dlp) — supporting high-quality downloads (360p to 4K), audio extraction, and automatic merging with FFmpeg.

---

## 📸 Preview

<!-- Replace the below link with an actual screenshot -->
![App Screenshot](https://user-images.githubusercontent.com/your-username/demo-screenshot.png)

---

##  Features

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

---


## 🎮 Getting Started
# 📦 Requirements
Python 3.7+

yt-dlp

streamlit

ffmpeg (recommended for merging)

## 🔧 Installation
# 1. Clone the repository
git clone https://github.com/your-username/youtube-downloader.git
cd youtube-downloader

# 2. Install dependencies
pip install -r requirements.txt

# 3. (Optional) Install FFmpeg
# Ensure ffmpeg is in your system PATH

## Usage
Run the Streamlit app:

# bash
# Command 
streamlit run you_dlp.py

Open the browser link shown in terminal.

Paste a YouTube video URL.

Select quality, choose merge option, click download!

Files are saved to:

bash
Copy code
~/Downloads/YouTube_Downloads/

📚 User Guide
Paste the YouTube URL.

Select video quality (e.g. 1080p).

Choose merge option (auto or separate).

Start the download — watch live progress.

Done! Enjoy the video/audio.

🧠 Note: High-quality formats (720p+) require merging because YouTube separates video and audio streams. This is handled automatically if FFmpeg is installed.

🧪 Developer Notes
URL validation via regex

Format sorting by resolution & bitrate

Merge option toggle (auto, merge, separate)

Safe filename sanitization

Cross-platform download location

Logging and exception tracking included

🩺 Troubleshooting
Issue	Solution
❌ No formats found	Make sure the video URL is valid and not private
❌ FFmpeg not found	Install FFmpeg and add it to your system PATH
❌ Format unavailable	Try a different quality
❌ App not opening	Ensure streamlit is installed and run from the project directory

📜 License
MIT License. See LICENSE for details.

🔒 This tool is for educational and personal use only. Please respect YouTube’s Terms of Service.

🙌 Acknowledgements
Streamlit

yt-dlp

FFmpeg

