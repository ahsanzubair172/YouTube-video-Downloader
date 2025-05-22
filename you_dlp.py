
# Import required libraries
import streamlit as st  # For building the web UI
import yt_dlp  # For downloading and extracting YouTube video info
import os  # For file and directory operations
import re  # For regular expressions (URL and filename validation)
import shutil  # For file operations (not used directly here)
from pathlib import Path  # For cross-platform file paths
import tempfile  # For temporary files (not used directly here)
import logging  # For logging errors and info
import subprocess  # For running system commands (FFmpeg check)


# Configure logging for debugging and error tracking
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def is_valid_url(url):
    """
    Check if the provided URL is a valid YouTube video URL.
    Supports various YouTube URL formats (watch, youtu.be, embed, etc).
    Returns True if valid, False otherwise.
    """
    if not url:
        return False
    # List of regex patterns for different YouTube URL types
    patterns = [
        r'^https?://(?:www\.)?youtube\.com/watch\?v=([a-zA-Z0-9_-]{11})',
        r'^https?://(?:www\.)?youtu\.be/([a-zA-Z0-9_-]{11})',
        r'^https?://(?:www\.)?youtube\.com/embed/([a-zA-Z0-9_-]{11})',
        r'^https?://(?:www\.)?youtube\.com/v/([a-zA-Z0-9_-]{11})',
        r'^https?://(?:m\.)?youtube\.com/watch\?v=([a-zA-Z0-9_-]{11})'
    ]
    # Check if any pattern matches the input URL
    return any(re.match(pattern, url.strip()) for pattern in patterns)


def check_ffmpeg():
    """
    Check if FFmpeg is installed and available in the system PATH.
    Returns (True, version_info) if found, otherwise (False, error_message).
    """
    try:
        # Run 'ffmpeg -version' and capture output
        result = subprocess.run(['ffmpeg', '-version'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            version_line = result.stdout.split('\n')[0]
            return True, version_line
        return False, "FFmpeg not working properly"
    except (subprocess.TimeoutExpired, FileNotFoundError, Exception):
        return False, "FFmpeg not found"


def get_video_info(url):
    """
    Retrieve basic information about a YouTube video (title, duration, uploader, etc).
    Returns a dictionary with video info, or None if extraction fails.
    """
    ydl_opts = {
        'quiet': True,  # Suppress yt_dlp output
        'no_warnings': True,
        'extractor_args': {
            'youtube': {
                'player_client': ['web', 'android'],  # Use web and android clients for extraction
                'skip': ['dash', 'hls']  # Skip certain streaming formats
            }
        }
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return {
                'title': info.get('title', 'Unknown Title'),
                'duration': info.get('duration', 0),
                'uploader': info.get('uploader', 'Unknown'),
                'id': info.get('id', ''),
                'thumbnail': info.get('thumbnail', ''),
                # Truncate description for display
                'description': info.get('description', '')[:200] + '...' if info.get('description') else ''
            }
    except Exception as e:
        logger.error(f"Error getting video info: {e}")
        return None


def get_video_formats(url, show_all=False):
    """
    Retrieve all available video (and optionally audio) formats for a YouTube video.
    Returns a list of dictionaries describing each format (quality, merge info, etc).
    show_all: If True, includes audio-only and video-only formats.
    """
    ydl_opts = {
        'quiet': True,  # Suppress yt_dlp output
        'no_warnings': True,
        'listformats': True,  # List all formats
        'extractor_args': {
            'youtube': {
                'player_client': ['web', 'android'],
                'skip': ['dash', 'hls']
            }
        }
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            result = ydl.extract_info(url, download=False)
            # If no formats found, return empty list
            if not result or 'formats' not in result:
                return []
            formats = []
            seen_formats = set()

            # Find the best audio-only format (for merging with video-only formats)
            audio_formats = [f for f in result['formats'] if f.get('acodec') != 'none' and f.get('vcodec') == 'none']
            best_audio = max(audio_formats, key=lambda x: x.get('abr', 0)) if audio_formats else None

            # Sort formats by quality (height, width, bitrate)
            sorted_formats = sorted(
                result['formats'], 
                key=lambda x: (x.get('height', 0), x.get('width', 0), x.get('tbr', 0)), 
                reverse=True
            )

            for f in sorted_formats:
                if not f or not f.get('format_id'):
                    continue
                format_id = f.get('format_id', '')
                vcodec = f.get('vcodec', 'none')
                acodec = f.get('acodec', 'none')
                height = f.get('height')
                fps = f.get('fps')
                ext = f.get('ext', 'mp4')
                filesize = f.get('filesize') or f.get('filesize_approx', 0)
                vbr = f.get('vbr', 0)

                # Only show video formats by default, unless show_all is True
                if vcodec == 'none' and not show_all:
                    continue

                # Build a user-friendly description for each format
                if vcodec != 'none' and height:
                    # Video format (with or without audio)
                    fps_str = f"@{fps}fps" if fps else ""
                    size_str = f" ({filesize//1024//1024}MB)" if filesize > 0 else ""
                    if acodec != 'none':
                        # Video+audio (complete)
                        quality_desc = f"{height}p{fps_str} ✅ Complete{size_str}"
                        format_key = f"complete_{height}_{fps or 0}"
                        merge_needed = False
                        priority = 1  # Highest priority
                    else:
                        # Video-only (needs merging with audio)
                        audio_info = ""
                        if best_audio:
                            audio_info = f" + {best_audio.get('abr', 128)}kbps audio"
                        quality_desc = f"{height}p{fps_str} 🔄 Auto-merge{audio_info}{size_str}"
                        format_key = f"video_merge_{height}_{fps or 0}"
                        merge_needed = True
                        priority = 2  # Second priority
                elif acodec != 'none' and show_all:
                    # Audio-only format (if show_all enabled)
                    abr = f.get('abr', 'unknown')
                    quality_desc = f"🎵 Audio Only - {abr}kbps ({ext.upper()})"
                    format_key = f"audio_only_{abr}"
                    merge_needed = False
                    priority = 3  # Lowest priority
                else:
                    continue

                # Avoid duplicate entries for the same quality
                if format_key not in seen_formats:
                    seen_formats.add(format_key)
                    formats.append({
                        'format_id': format_id,
                        'resolution': quality_desc,
                        'has_video': vcodec != 'none',
                        'has_audio': acodec != 'none',
                        'height': height or 0,
                        'ext': ext,
                        'filesize': filesize,
                        'merge_needed': merge_needed,
                        'best_audio_id': best_audio.get('format_id') if best_audio and merge_needed else None,
                        'priority': priority,
                        'fps': fps or 0
                    })

            # Sort formats: complete first, then by quality
            formats.sort(key=lambda x: (x['priority'], -x['height'], -x['fps']))
            return formats
    except Exception as e:
        logger.error(f"Error fetching formats: {e}")
        st.error(f"❌ Error fetching formats: {str(e)}")
        return []


def sanitize_filename(title):
    """
    Clean up the video title to make it safe for use as a filename on all operating systems.
    Removes illegal characters and trims length.
    """
    if not title:
        return "video"
    # Remove illegal filename characters
    sanitized = re.sub(r'[<>:"/\\|?*\x00-\x1f]', '', title)
    # Replace multiple spaces with a single space
    sanitized = re.sub(r'\s+', ' ', sanitized).strip()
    # Limit filename length
    sanitized = sanitized[:200] if len(sanitized) > 200 else sanitized
    return sanitized or "video"


def download_video(url, format_info, output_path, progress_container, progress_bar, merge_option="auto"):
    """
    Download the selected video format (and audio if needed) to the specified output path.
    Handles merging video+audio (if required) using FFmpeg, or downloads separately.
    Shows progress in the Streamlit UI.
    Returns True if successful, False otherwise.
    """
    # Ensure output directory exists
    try:
        os.makedirs(output_path, exist_ok=True)
    except Exception as e:
        st.error(f"❌ Cannot create output directory: {e}")
        return False

    # Check write permissions
    if not os.access(output_path, os.W_OK):
        st.error(f"❌ No write permission for directory: {output_path}")
        return False

    # Progress hook for yt_dlp to update Streamlit UI
    def progress_hook(d):
        try:
            if d['status'] == 'downloading':
                total = d.get('total_bytes') or d.get('total_bytes_estimate', 0)
                downloaded = d.get('downloaded_bytes', 0)
                filename = d.get('filename', '').split('/')[-1]
                if total > 0:
                    percent = min((downloaded / total) * 100, 100)
                    progress_bar.progress(percent / 100)
                    progress_container.markdown(f"**📥 Downloading {filename}: {percent:.1f}%**")
                else:
                    progress_container.markdown(f"**📥 Downloading {filename}...**")
            elif d['status'] == 'finished':
                progress_bar.progress(1.0)
                progress_container.markdown("**✅ Download complete! Processing...**")
        except Exception as e:
            logger.error(f"Progress hook error: {e}")

    # Get video info for filename
    video_info = get_video_info(url)
    if not video_info:
        st.error("❌ Could not retrieve video information")
        return False

    # Sanitize the video title for use as a filename
    safe_title = sanitize_filename(video_info['title'])

    try:
        format_id = format_info['format_id']
        merge_needed = format_info.get('merge_needed', False)

        # If merging is needed and user chose to merge
        if merge_needed and merge_option == "merge":
            # Download video-only + best audio and merge into a single file
            format_string = f"{format_id}+bestaudio/best"
            output_template = os.path.join(output_path, f'{safe_title}_merged.%(ext)s')
            ydl_opts = {
                'format': format_string,
                'outtmpl': output_template,
                'quiet': True,
                'no_warnings': True,
                'progress_hooks': [progress_hook],
                'extractor_args': {
                    'youtube': {
                        'player_client': ['web', 'android'],
                        'skip': ['dash', 'hls']
                    }
                },
                # Use FFmpeg to merge video and audio into MP4
                'postprocessors': [
                    {
                        'key': 'FFmpegVideoConvertor',
                        'preferedformat': 'mp4',
                    }
                ]
            }

        # If merging is needed but user chose to keep separate files
        elif merge_needed and merge_option == "separate":
            # Download video and audio as separate files
            progress_container.markdown("**📥 Downloading video and audio separately...**")
            # Download video-only
            video_opts = {
                'format': format_id,
                'outtmpl': os.path.join(output_path, f'{safe_title}_video.%(ext)s'),
                'quiet': True,
                'progress_hooks': [progress_hook],
                'extractor_args': {
                    'youtube': {
                        'player_client': ['web', 'android'],
                        'skip': ['dash', 'hls']
                    }
                }
            }
            with yt_dlp.YoutubeDL(video_opts) as ydl:
                ydl.download([url])
            # Download audio-only
            audio_opts = {
                'format': 'bestaudio',
                'outtmpl': os.path.join(output_path, f'{safe_title}_audio.%(ext)s'),
                'quiet': True,
                'progress_hooks': [progress_hook],
                'extractor_args': {
                    'youtube': {
                        'player_client': ['web', 'android'],
                        'skip': ['dash', 'hls']
                    }
                }
            }
            with yt_dlp.YoutubeDL(audio_opts) as ydl:
                ydl.download([url])
            progress_container.markdown("**🎉 Video and audio downloaded separately!**")
            return True

        else:
            # Download as-is (complete format or audio-only)
            ydl_opts = {
                'format': format_id,
                'outtmpl': os.path.join(output_path, f'{safe_title}.%(ext)s'),
                'quiet': True,
                'no_warnings': True,
                'progress_hooks': [progress_hook],
                'extractor_args': {
                    'youtube': {
                        'player_client': ['web', 'android'],
                        'skip': ['dash', 'hls']
                    }
                }
            }

        # Execute the download (for merged or complete formats)
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        progress_container.markdown("**🎉 Download completed successfully!**")
        return True

    except yt_dlp.DownloadError as e:
        # Handle common download errors and show user-friendly messages
        error_msg = str(e)
        if "requested format not available" in error_msg.lower():
            st.error("❌ The selected quality is no longer available. Please try a different quality.")
        elif "video unavailable" in error_msg.lower():
            st.error("❌ Video is unavailable or private.")
        elif "ffmpeg" in error_msg.lower():
            st.error("❌ FFmpeg error during merging. Try downloading separately or install FFmpeg.")
        else:
            st.error(f"❌ Download error: {error_msg}")
        return False
    except Exception as e:
        logger.error(f"Download failed: {e}")
        st.error(f"❌ Download failed: {str(e)}")
        return False


def main():
    """
    Main function to run the Streamlit YouTube downloader app.
    Sets up the UI, handles user input, and coordinates video info, format selection, and download.
    """
    # Set Streamlit page configuration
    st.set_page_config(
        page_title="YouTube Video Downloader",
        page_icon="🎥",
        layout="wide"
    )

    st.title("🎥 Advanced YouTube Video Downloader")

    # Define the default download directory (in user's Downloads folder)
    download_path = Path.home() / "Downloads" / "YouTube_Downloads"

    # Check if FFmpeg is available for merging
    ffmpeg_available, ffmpeg_info = check_ffmpeg()

    # Sidebar: Show download location, system status, instructions, and help
    with st.sidebar:
        st.markdown("## 📁 Download Location")
        st.code(str(download_path))

        st.markdown("## 🛠️ System Status")
        if ffmpeg_available:
            st.success("✅ FFmpeg Available")
            st.caption(ffmpeg_info)
        else:
            st.error("❌ FFmpeg Not Found")
            st.caption("Install FFmpeg for video merging")

        st.markdown("## 📋 Instructions")
        st.markdown("""
        1. **Paste YouTube URL**
        2. **Select video quality**
        3. **Choose merge option** (if applicable)
        4. **Click Download**
        """)

        st.markdown("## 🔄 Quality Explained")
        st.markdown("""
        **Why only 360p shows as 'Complete'?**

        YouTube changed how videos are served:
        - **Low quality** (360p, 480p): Complete files
        - **High quality** (720p, 1080p, 4K): Separate video + audio

        **This app automatically merges high-quality formats!**
        """)

        st.markdown("## 📋 How It Works")
        st.markdown("""
        1. **Select any quality** (even 4K!)
        2. **App downloads** video + audio
        3. **FFmpeg merges** them automatically
        4. **You get** single high-quality MP4
        """)

        st.markdown("## ⚙️ Troubleshooting")
        st.markdown("""
        - **Only 360p showing?** ✅ Normal behavior
        - **Want 1080p?** Choose "Auto-merge" option
        - **Merge failed?** Try "Keep Separate"
        - **No FFmpeg?** Install it for merging
        """)

    # Main interface: User input for YouTube URL
    video_url = st.text_input(
        "📋 Enter YouTube URL:",
        placeholder="https://www.youtube.com/watch?v=...",
        help="Paste any valid YouTube video URL"
    )

    # Option to show all formats (including audio-only)
    col1, col2 = st.columns([1, 1])
    with col1:
        show_all_formats = st.checkbox(
            "🔍 Show all formats",
            help="Include video-only and audio-only formats"
        )

    # Option to set default merge behavior
    with col2:
        if ffmpeg_available:
            merge_preference = st.selectbox(
                "🔄 Default merge behavior:",
                ["auto", "merge", "separate"],
                help="How to handle video-only formats"
            )
        else:
            merge_preference = "separate"
            st.info("ℹ️ Only separate downloads available (FFmpeg not found)")

    # If user entered a URL, process it
    if video_url:
        # Validate the URL
        if not is_valid_url(video_url):
            st.error("❌ Please enter a valid YouTube URL")
        else:
            # Get video information (title, channel, etc)
            with st.spinner("🔍 Getting video information..."):
                video_info = get_video_info(video_url)

            if video_info:
                # Show video info to the user
                st.success("✅ Video found!")

                col1, col2 = st.columns([2, 1])
                with col1:
                    st.markdown(f"### 📹 {video_info['title']}")
                    st.markdown(f"**👤 Channel:** {video_info['uploader']}")
                    if video_info['description']:
                        st.markdown(f"**📝 Description:** {video_info['description']}")

                with col2:
                    duration = video_info.get('duration', 0)
                    if duration:
                        minutes, seconds = divmod(duration, 60)
                        st.metric("⏱️ Duration", f"{minutes}:{seconds:02d}")

                # Get available download formats for this video
                with st.spinner("🔍 Loading available formats..."):
                    formats = get_video_formats(video_url, show_all_formats)

                if formats:
                    st.markdown("### 🎞️ Available Quality Options")

                    # Expandable help for format types
                    with st.expander("ℹ️ Understanding Quality Options", expanded=False):
                        st.markdown("""
                        **✅ Complete**: Video and audio in one file (ready to play)

                        **🔄 Auto-merge**: High quality video + audio combined automatically

                        **🎵 Audio Only**: Audio-only formats (when 'Show all formats' is enabled)

                        💡 **Note**: YouTube serves high-quality videos (720p+) separately from audio. 
                        We automatically combine them for you!
                        """)

                    # Build a mapping from description to format info
                    format_options = {}
                    for fmt in formats:
                        format_options[fmt['resolution']] = fmt

                    # Let user select the desired quality
                    selected_resolution = st.selectbox(
                        "Choose video quality:",
                        options=list(format_options.keys()),
                        help="✅ = Ready to play | 🔄 = Will be merged automatically"
                    )

                    selected_format = format_options[selected_resolution]

                    # If merging is needed, show merge options
                    merge_option = merge_preference
                    if selected_format.get('merge_needed'):
                        st.markdown("#### 🔄 This quality requires merging video + audio")

                        if ffmpeg_available:
                            st.success("✅ FFmpeg detected - automatic merging available")

                            merge_col1, merge_col2 = st.columns(2)

                            with merge_col1:
                                st.info("**🔄 Auto-Merge (Recommended)**\n\nDownloads video + audio and combines them into a single MP4 file")

                            with merge_col2:
                                st.info("**📁 Keep Separate**\n\nDownloads video and audio as separate files for manual control")

                            # Let user choose merge or separate
                            merge_choice = st.radio(
                                "Select merge option:",
                                ["Auto-merge into single file", "Keep as separate files"],
                                index=0 if merge_preference == "merge" else 1
                            )

                            merge_option = "merge" if "Auto-merge" in merge_choice else "separate"

                        else:
                            st.warning("⚠️ FFmpeg not found - will download as separate files")
                            st.info("**📁 Separate Files Mode**\n\nVideo and audio will be downloaded as separate files. Install FFmpeg for automatic merging.")
                            merge_option = "separate"

                    # Download section
                    st.markdown("### ⬇️ Download")

                    if st.button("🚀 Start Download", type="primary", use_container_width=True):
                        progress_container = st.empty()
                        progress_bar = st.progress(0)

                        # Show what will happen
                        if selected_format.get('merge_needed'):
                            if merge_option == "merge":
                                st.info("🔄 Will download video and audio, then merge them")
                            else:
                                st.info("📁 Will download video and audio as separate files")
                        else:
                            st.info("📥 Will download complete file")

                        # Start the download
                        success = download_video(
                            video_url, 
                            selected_format, 
                            str(download_path),
                            progress_container,
                            progress_bar,
                            merge_option
                        )

                        if success:
                            st.balloons()
                            st.success(f"🎉 Download successful!")
                            st.info(f"📁 Files saved to: `{download_path}`")

                            # Show what was downloaded
                            if merge_option == "separate" and selected_format.get('merge_needed'):
                                st.info("📄 Downloaded files:\n- Video file (no audio)\n- Audio file")
                                if ffmpeg_available:
                                    st.info("💡 You can manually merge them later using FFmpeg")

                        # Clear progress bars
                        progress_container.empty()
                        progress_bar.empty()

                else:
                    st.warning("⚠️ No downloadable formats found for this video.")
            else:
                st.error("❌ Could not retrieve video information. Please check the URL.")


# Entry point for the script
if __name__ == "__main__":
    main()

# To run the app, use the following command in your terminal:
# streamlit run you_dlp.py