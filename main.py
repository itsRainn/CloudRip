import tkinter as tk
from tkinter import messagebox, ttk, filedialog
import urllib.request
import threading
import yt_dlp
import sys
import os
import json
import time
import re
import subprocess
import webbrowser

CURRENT_VERSION = "0.0.1"
VERSION_URL = "https://raw.githubusercontent.com/itsRainn/Universal-Media-Downloader/refs/heads/main/version.json?token=GHSAT0AAAAAAEI3AJ6A32FOGEWFMZKKAFA62VGU3UQ"

def get_base_path():
    """Returns the base operational folder directory path, whether compiled or raw code format."""
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


URL_INPUT_BOX_WIDTH = 35
SAVE_PATH_BOX_WIDTH = 32
VIDEO_FORMAT_BOX_WIDTH = 15
AUDIO_FORMAT_BOX_WIDTH = 15
AUDIO_BITRATE_BOX_WIDTH = 27
SLIDER_LAYOUT_WIDTH = 280


def get_settings_path():
    app_data_dir = os.path.join(os.path.expanduser('~'), 'AppData', 'Local', 'UnivMediaDldr')
    os.makedirs(app_data_dir, exist_ok=True)
    return os.path.join(app_data_dir, "config.json")

SETTINGS_FILE = get_settings_path()
is_downloading = False
is_dark_mode = False

class ToolTip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tip_window = None
        self.widget.bind("<Enter>", self.show_tip)
        self.widget.bind("<Leave>", self.hide_tip)

    def show_tip(self, event=None):
        if self.tip_window or not self.text:
            return
        x = self.widget.winfo_rootx() + self.widget.winfo_width() + 10
        y = self.widget.winfo_rooty() - 5
        self.tip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        bg = "#2d2d2d" if is_dark_mode else "#ffffcc"
        fg = "#ffffff" if is_dark_mode else "#000000"
        label = tk.Label(tw, text=self.text, justify=tk.LEFT, background=bg, foreground=fg,
                         relief=tk.SOLID, borderwidth=1, font=("Arial", 9, "normal"), padx=5, pady=3)
        label.pack(ipadx=1)

    def hide_tip(self, event=None):
        tw = self.tip_window
        self.tip_window = None
        if tw:
            tw.destroy()

def load_settings():
    user_videos_path = os.path.join(os.path.expanduser('~'), 'Videos')
    default_path = os.path.join(user_videos_path, 'UnivMediaDldr')
    os.makedirs(default_path, exist_ok=True)
    defaults = {
        "save_directory": default_path,
        "video_quality_index": 0,
        "video_format": "MP4",
        "video_fps_index": 0,
        "video_audio_bitrate": "320 kbps",
        "audio_format": "MP3",
        "audio_bitrate": "320 kbps",
        "selected_tab": 0,
        "dark_mode": False
    }
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r") as f:
                saved_data = json.load(f)
                defaults.update(saved_data)
                if not os.path.isdir(defaults["save_directory"]):
                    defaults["save_directory"] = default_path
        except Exception:
            pass
    return defaults

def save_current_settings():
    try:
        settings_data = {
            "save_directory": dir_entry.get().strip(),
            "video_quality_index": int(video_quality_slider.get()),
            "video_format": format_combobox.get(),
            "video_fps_index": int(video_fps_slider.get()),
            "video_audio_bitrate": video_audio_bitrate_combobox.get(),
            "audio_format": audio_format_combobox.get(),
            "audio_bitrate": bitrate_combobox.get(),
            "selected_tab": notebook.index(notebook.select()),
            "dark_mode": is_dark_mode
        }
        with open(SETTINGS_FILE, "w") as f:
            json.dump(settings_data, f)
    except Exception:
        pass

def choose_directory():
    selected_dir = filedialog.askdirectory()
    if selected_dir:
        dir_entry.delete(0, tk.END)
        dir_entry.insert(0, selected_dir)
        save_current_settings()

def remove_selection_highlight(event):
    root.focus_set()

def toggle_theme():
    global is_dark_mode
    is_dark_mode = not is_dark_mode
    update_theme_ui()
    save_current_settings()

def update_theme_ui():
    bg_color = "#1e1e1e" if is_dark_mode else "#f0f0f0"
    frame_bg = "#2d2d2d" if is_dark_mode else "#f5f5f5"
    entry_bg = "#3c3c3c" if is_dark_mode else "#ffffff"
    fg_color = "#ffffff" if is_dark_mode else "#000000"
    entry_fg = "#ffffff" if is_dark_mode else "#000000"
    
    root.config(bg=bg_color)
    top_frame.config(bg=bg_color)
    progress_frame.config(bg=bg_color)
    bottom_frame.config(bg=bg_color)
    
    url_label.config(bg=bg_color, fg=fg_color)
    url_subtext.config(bg=bg_color, fg="gray" if not is_dark_mode else "#aaaaaa")
    dir_label.config(bg=bg_color, fg=fg_color)
    percent_label.config(bg=bg_color, fg=fg_color)
    status_label.config(bg=bg_color)
    
    if not is_downloading:
        status_label.config(fg="gray" if not is_dark_mode else "#aaaaaa")
        
    try:
        url_subtext_two.config(bg=bg_color, fg="gray" if not is_dark_mode else "#aaaaaa")
    except:
        pass
        
    dir_label.config(bg=bg_color, fg=fg_color)
    try:
        app_watermark_label.config(
            bg=bg_color, fg="#888888" if not is_dark_mode else "#555555"
        )
    except:
        pass
        
    a_format_label.config(bg=frame_bg, fg=fg_color)
    
    theme_button.config(
        text="☀️" if is_dark_mode else "🌙",
        bg="#3c3c3c" if is_dark_mode else "#ffffff",
        fg="#ffffff" if is_dark_mode else "#000000",
        activebackground="#505050" if is_dark_mode else "#e0e0e0"
    )
    url_entry.config(bg=entry_bg, fg=entry_fg, insertbackground=fg_color)
    dir_entry.config(bg=entry_bg, fg=entry_fg, insertbackground=fg_color)
    video_tab.config(bg=frame_bg)
    audio_tab.config(bg=frame_bg)
    v_quality_row.config(bg=frame_bg)
    v_quality_label.config(bg=frame_bg, fg=fg_color)
    v_quality_value.config(bg=frame_bg, fg="#4CAF50" if is_dark_mode else "#2E7D32")
    v_format_label.config(bg=frame_bg, fg=fg_color)
    v_fps_row.config(bg=frame_bg)
    v_fps_label.config(bg=frame_bg, fg=fg_color)
    v_fps_value.config(bg=frame_bg, fg="#4CAF50" if is_dark_mode else "#2E7D32")
    v_audio_bitrate_label.config(bg=frame_bg, fg=fg_color)

    # Dark Mode container block background matching overrides
    try:
        v_form_row.config(bg=frame_bg)
        v_bit_row.config(bg=frame_bg)
        a_bit_row.config(bg=frame_bg)
        a_format_row.config(bg=frame_bg)
        
        v_format_label.config(bg=frame_bg, fg=fg_color)
        v_audio_bitrate_label.config(bg=frame_bg, fg=fg_color)
        a_bitrate_label.config(bg=frame_bg, fg=fg_color)
        
        v_fps_help.config(bg=frame_bg, fg="#347aeb" if is_dark_mode else "#0000ee")
        v_form_help.config(bg=frame_bg, fg="#347aeb" if is_dark_mode else "#0000ee")
        v_bit_help.config(bg=frame_bg, fg="#347aeb" if is_dark_mode else "#0000ee")
        a_bit_help.config(bg=frame_bg, fg="#347aeb" if is_dark_mode else "#0000ee")
        a_help_label.config(bg=frame_bg, fg="#347aeb" if is_dark_mode else "#0000ee")
    except:
        pass
        
    video_quality_slider.config(bg=frame_bg, fg=fg_color, highlightbackground=frame_bg, activebackground=frame_bg)
    video_fps_slider.config(bg=frame_bg, fg=fg_color, highlightbackground=frame_bg, activebackground=frame_bg)
    help_label.config(bg=frame_bg, fg="#347aeb" if is_dark_mode else "#0000ee")
    
    style = ttk.Style()
    style.theme_use('clam')
    style.configure("Horizontal.TProgressbar", thickness=3, troughcolor="#e0e0e0" if not is_dark_mode else "#333333", background="#4CAF50", borderwidth=0)
    
    if is_dark_mode:
        style.configure("TNotebook", background=bg_color, borderwidth=0)
        style.configure("TNotebook.Tab", background=frame_bg, foreground=fg_color, borderwidth=1)
        style.map("TNotebook.Tab", background=[("selected", bg_color)], foreground=[("selected", fg_color)])
        style.configure("TCombobox", fieldbackground="#252526", background="#333333", foreground="#ffffff", arrowcolor="#ffffff")
        style.map("TCombobox", fieldbackground=[("readonly", "#252526"), ("focus", "#252526")], foreground=[("readonly", "#ffffff"), ("focus", "#ffffff")], selectbackground=[("readonly", "#252526"), ("focus", "#252526")], selectforeground=[("readonly", "#ffffff"), ("focus", "#ffffff")])
    else:
        style.configure("TNotebook", background=bg_color, borderwidth=0)
        style.configure("TNotebook.Tab", background=frame_bg, foreground=fg_color, borderwidth=1)
        style.map("TNotebook.Tab", background=[("selected", bg_color)], foreground=[("selected", fg_color)])
        style.configure("TCombobox", fieldbackground="#ffffff", background="#e0e0e0", foreground="#000000", arrowcolor="#000000")
        style.map("TCombobox", fieldbackground=[("readonly", "#ffffff"), ("focus", "#ffffff")], foreground=[("readonly", "#000000"), ("focus", "#000000")], selectbackground=[("readonly", "#347aeb"), ("focus", "#347aeb")], selectforeground=[("readonly", "#ffffff"), ("focus", "#ffffff")])

def start_download():
    global is_downloading
    url = url_entry.get().strip()
    save_dir = dir_entry.get().strip()
    
    if not url:
        messagebox.showerror("Error", "Please enter a valid URL link.")
        return
    if not save_dir or not os.path.isdir(save_dir):
        messagebox.showerror("Error", "Please select a valid folder.")
        return
        
    save_current_settings()
    is_downloading = True
    download_button.config(state="disabled")
    status_label.config(text="Status: Connecting and analyzing streams...", fg="orange")
    progress_bar['value'] = 0
    percent_label.config(text="0.0%")
    
    sub_idx = notebook.index(notebook.select())
    if sub_idx == 0:
        quality_str = video_quality_options[int(video_quality_slider.get())].strip()
        fps_str = fps_options[int(video_fps_slider.get())].strip()
        thread = threading.Thread(target=run_video_ytdlp, args=(url, save_dir, quality_str, format_combobox.get().lower(), fps_str, video_audio_bitrate_combobox.get()), daemon=True)
    else:
        thread = threading.Thread(target=run_audio_ytdlp, args=(url, save_dir, audio_format_combobox.get().lower(), bitrate_combobox.get()), daemon=True)
    thread.start()

def update_gui_metrics(percent, status_text):
    if is_downloading:
        progress_bar['value'] = percent
        percent_label.config(text=f"{percent:.1f}%")
        status_label.config(text=status_text, fg="orange" if percent < 95 else "blue")

def ytdlp_live_logger_hook(d):
    if d['status'] == 'downloading':
        total = d.get('total_bytes') or d.get('total_bytes_estimate') or 0
        downloaded = d.get('downloaded_bytes', 0)
        if total > 0:
            pct = (downloaded / total) * 100
            root.after(0, lambda p=pct: update_gui_metrics(p, "Status: Downloading stream fragments live..."))
    elif d['status'] == 'finished':
        root.after(0, lambda: update_gui_metrics(95.0, "Status: Finalizing media tracks..."))

def get_height_filter(quality_choice):
    if quality_choice == "Best":
        return 'bestvideo+bestaudio/best'
    h = int(quality_choice.replace("p", ""))
    return f'bestvideo[height<={h}]+bestaudio/best[height<={h}]/worst'

def sanitize_filename_component(text):
    clean = re.sub(r'[\/:*?"<>|()\[\]\s,\']', '_', text)
    clean = re.sub(r'_{2,}', '_', clean)
    return clean.strip('_')

def run_video_ytdlp(url, save_dir, quality_choice, ext_format, fps_choice, video_bitrate_str):
    global is_downloading
    clean_res = quality_choice.strip().lower()
    clean_fps = fps_choice.strip().lower().replace("+", "")
    clean_bitrate = video_bitrate_str.strip().lower()
    is_lossless = "Lossless" in video_bitrate_str
    bitrate_parts = video_bitrate_str.split()
    bitrate_numeric = 0 if is_lossless else (int(bitrate_parts[0]) if bitrate_parts else 320)
    
    save_dir = os.path.join(save_dir, "Videos")
    os.makedirs(save_dir, exist_ok=True)
    
    video_temp_dir = os.path.join(save_dir, "Temp")
    os.makedirs(video_temp_dir, exist_ok=True)
    temp_id = str(int(time.time()))
    temp_video_path = os.path.join(video_temp_dir, f'temp_v_{temp_id}.%(ext)s')
    
    ydl_opts = {
        'format': get_height_filter(quality_choice),
        'outtmpl': temp_video_path,
        'color': False,
        'progress_hooks': [ytdlp_live_logger_hook],
        'compat_opts': ['no-format-id', 'multiline-cookies'],
        'noplaylist': True,
        'soundclouddownloader': True,
        'ffmpeg_location': get_base_path(),
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            raw_title = info.get('title', 'Video')
            raw_uploader = info.get('uploader', 'UnknownChannel')
            downloaded_ext = info.get('ext', 'mp4')
            
            actual_temp_file = os.path.join(video_temp_dir, f'temp_v_{temp_id}.{downloaded_ext}')
            clean_title = sanitize_filename_component(raw_title)
            clean_uploader = sanitize_filename_component(raw_uploader)
            
            final_name = f"{clean_title}.{clean_uploader}.{clean_res}.{clean_fps}fps.{clean_bitrate}.{ext_format}"
            final_output_path = os.path.join(save_dir, final_name)
            
            ffmpeg_cmd = ['ffmpeg', '-y', '-i', actual_temp_file]
            if fps_choice == "Default":
                ffmpeg_cmd.extend(['-c:v', 'copy'])
            else:
                fps_val = 60 if fps_choice == "60+" else int(fps_choice)
                ffmpeg_cmd.extend(['-vf', f'fps={fps_val}', '-c:v', 'libx264', '-preset', 'ultrafast', '-crf', '28'])
                
            is_webm = ext_format.lower() == 'webm'
            
            if is_lossless:
                if is_webm:
                    ffmpeg_cmd.extend(['-c:a', 'libvorbis'])
                else:
                    ffmpeg_cmd.extend(['-c:a', 'copy'])
            elif bitrate_numeric < 32:
                if is_webm:
                    ffmpeg_cmd.extend(['-c:a', 'libvorbis', '-b:a', f'{bitrate_numeric}k', '-ar', '22050', '-ac', '1'])
                else:
                    ffmpeg_cmd.extend(['-c:a', 'libmp3lame', '-b:a', f'{bitrate_numeric}k', '-ar', '22050', '-ac', '1'])
            else:
                if is_webm:
                    ffmpeg_cmd.extend(['-c:a', 'libvorbis', '-b:a', f'{bitrate_numeric}k', '-ar', '44100'])
                else:
                    ffmpeg_cmd.extend(['-c:a', 'aac', '-b:a', f'{bitrate_numeric}k', '-ar', '44100'])
                    
            ffmpeg_cmd.append(final_output_path)
            result = subprocess.run(ffmpeg_cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                raise Exception(f"FFmpeg conversion failed:\n{result.stderr}")
                
            for root_dir, _, files in os.walk(video_temp_dir):
                for file in files:
                    try:
                        os.remove(os.path.join(root_dir, file))
                    except Exception:
                        pass
            try:
                os.rmdir(video_temp_dir)
            except Exception:
                pass
                
            is_downloading = False
            root.after(0, lambda: download_finished(True, "File processed and saved successfully!"))
    except Exception as err:
        is_downloading = False
        err_msg = str(err)
        root.after(0, lambda msg=err_msg: download_finished(False, f"Error: {msg}"))

def run_audio_ytdlp(url, save_dir, audio_fmt, bitrate_choice_str):
    global is_downloading
    is_lossless = "Lossless" in bitrate_choice_str
    bitrate_parts = bitrate_choice_str.split()
    bitrate_numeric = 0 if is_lossless else (int(bitrate_parts[0]) if bitrate_parts else 320)
    
    save_dir = os.path.join(save_dir, "Audios")
    os.makedirs(save_dir, exist_ok=True)
    
    audio_temp_dir = os.path.join(save_dir, "Temp")
    os.makedirs(audio_temp_dir, exist_ok=True)
    temp_id = str(int(time.time()))
    download_template = os.path.join(audio_temp_dir, f'ytdlp_temp_{temp_id}.%(ext)s')
    
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': download_template,
        'color': False,
        'progress_hooks': [ytdlp_live_logger_hook],
        'compat_opts': ['no-format-id', 'multiline-cookies'],
        'noplaylist': True,
        'soundclouddownloader': True,
        'ffmpeg_location': get_base_path(),
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            raw_title = info.get('title', 'Audio')
            downloaded_ext = info.get('ext', 'mp4')
            
            actual_temp = os.path.join(audio_temp_dir, f'ytdlp_temp_{temp_id}.{downloaded_ext}')
            clean_title = sanitize_filename_component(raw_title)
            clean_bitrate = bitrate_choice_str.strip().lower()
            
            final_name = f"{clean_title}.{clean_bitrate}.{audio_fmt}"
            final_output_path = os.path.join(save_dir, final_name)
            
            ffmpeg_cmd = ['ffmpeg', '-y', '-i', actual_temp, '-vn']

            if is_lossless:
                if audio_fmt == 'wav':
                    ffmpeg_cmd.extend(['-c:a', 'pcm_s16le', '-ar', '44100'])
                elif audio_fmt == 'm4a':
                    ffmpeg_cmd.extend(['-c:a', 'copy'])
                elif audio_fmt == 'mp3':
                    ffmpeg_cmd.extend(['-c:a', 'libmp3lame', '-b:a', '320k', '-ar', '44100'])
            elif bitrate_numeric < 32:
                if audio_fmt in ['mp3', 'm4a', 'wav']:
                    codec = 'libmp3lame' if audio_fmt in ['mp3', 'wav'] else 'aac'
                    ffmpeg_cmd.extend(['-c:a', codec, '-b:a', f'{bitrate_numeric}k', '-ar', '22050', '-ac', '1'])
            else:
                if audio_fmt == 'wav':
                    ffmpeg_cmd.extend(['-c:a', 'pcm_s16le', '-ar', '44100'])
                elif audio_fmt == 'mp3':
                    ffmpeg_cmd.extend(['-c:a', 'libmp3lame', '-b:a', f'{bitrate_numeric}k', '-ar', '44100'])
                elif audio_fmt == 'm4a':
                    ffmpeg_cmd.extend(['-c:a', 'aac', '-b:a', f'{bitrate_numeric}k', '-ar', '44100'])
                    
            ffmpeg_cmd.append(final_output_path)
            result = subprocess.run(ffmpeg_cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                raise Exception(f"Audio extraction failed:\n{result.stderr}")
                
            for root_dir, _, files in os.walk(audio_temp_dir):
                for file in files:
                    try:
                        os.remove(os.path.join(root_dir, file))
                    except Exception:
                        pass
            try:
                os.rmdir(audio_temp_dir)
            except Exception:
                pass
                
            is_downloading = False
            root.after(0, lambda: download_finished(True, "Video downloaded successfully!"))
    except Exception as err:
        is_downloading = False
        err_msg = str(err)
        root.after(0, lambda msg=err_msg: download_finished(False, f"Error: {msg}"))

def download_finished(success, message):
    download_button.config(state="normal")
    if success:
        progress_bar['value'] = 100
        percent_label.config(text="100.0%")
        status_label.config(text="Status: Idle", fg="green")
        messagebox.showinfo("Success", message)
    else:
        progress_bar['value'] = 0
        percent_label.config(text="0.0%")
        status_label.config(text="Status: Failed", fg="red")
        messagebox.showerror("Error", message)

# --- Slider Value Snap Handlers ---
def snap_quality_slider(value):
    idx = round(float(value))
    video_quality_slider.set(idx)
    v_quality_value.config(text=f"[{video_quality_options[idx]}]")
    save_current_settings()

def snap_fps_slider(value):
    idx = round(float(value))
    video_fps_slider.set(idx)
    v_fps_value.config(text=f"[{fps_options[idx]} FPS]" if fps_options[idx] != "Default" else "[Default]")
    save_current_settings()

# gui
root = tk.Tk()
root.title("Universal Media Downloader")
root.geometry("540x550")
root.resizable(False, False)

try:
    ico_path = os.path.join(get_base_path(), "icon.ico")
    root.iconbitmap(ico_path)
except:
    pass

def run_background_update_check():
    try:
        req = urllib.request.Request(VERSION_URL, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=4) as response:
            data = json.loads(response.read().decode())
            latest_version = data.get("version")
            setup_download_url = data.get("url")
            if latest_version and latest_version != CURRENT_VERSION:
                if messagebox.askyesno("Update Available", f"A new version ({latest_version}) of UnivMediaDldr is ready!\nWould you like to download and install the update now?"):
                    webbrowser.open_new_tab(setup_download_url)
    except:
        pass

threading.Thread(target=run_background_update_check, daemon=True).start()

top_frame = tk.Frame(root)
top_frame.pack(pady=10, fill="x", padx=20)

url_label = tk.Label(top_frame, text="URL Link:", font=("Arial", 10, "bold"), width=10, anchor="w")
url_label.grid(row=0, column=0, pady=5)

url_entry = tk.Entry(top_frame, font=("Arial", 11), width=URL_INPUT_BOX_WIDTH)
url_entry.grid(row=0, column=1, columnspan=2, sticky="w", padx=5)
url_entry.focus()

global url_subtext
url_subtext = tk.Label(top_frame, text="Supports links from YouTube, SoundCloud, Medal.tv, Instagram, Facebook, X, etc.", font=("Arial", 8, "italic"))
url_subtext.grid(row=1, column=1, columnspan=2, sticky="w", padx=5, pady=0)

EXTRA_SUBTEXT_LINE = "Ensure you are logged into Microsoft Edge for account-locked stream downloads."
global url_subtext_two
url_subtext_two = tk.Label(top_frame, text="Known unsupported links: Spotify, Bilibili, Any streaming platform", font=("Arial", 8, "italic"))
url_subtext_two.grid(row=2, column=1, columnspan=2, sticky="w", padx=5, pady=(0, 5))

dir_label = tk.Label(top_frame, text="Save To:", font=("Arial", 10, "bold"), width=10, anchor="w")
dir_label.grid(row=3, column=0, pady=5)

dir_entry = tk.Entry(top_frame, font=("Arial", 11), width=SAVE_PATH_BOX_WIDTH)
dir_entry.grid(row=3, column=1, sticky="w", padx=5)

notebook = ttk.Notebook(root)
notebook.pack(fill="both", expand=True, padx=20, pady=5)

video_quality_options = ["Best", "2160p", "1440p", "1080p", "720p", "480p", "360p", "240p", "144p"]
fps_options = ["Default", "60+", "60", "45", "30", "15", "10", "7", "5", "2", "1"]
format_options = ["MP4", "MKV", "MOV", "WEBM"]
video_bitrate_options = ["Lossless (MKV only)", "320 kbps", "256 kbps", "192 kbps", "128 kbps", "96 kbps", "64 kbps", "32 kbps", "16 kbps", "8 kbps"]
audio_bitrate_options = ["Lossless (M4A and WAV only)", "320 kbps", "256 kbps", "192 kbps", "128 kbps", "96 kbps", "64 kbps", "32 kbps", "16 kbps", "8 kbps"]

video_tab = tk.Frame(notebook)
notebook.add(video_tab, text=" Video Downloader ")

global v_quality_row
v_quality_row = tk.Frame(video_tab)
v_quality_row.pack(fill="x", padx=15, pady=(10, 0))

v_quality_label = tk.Label(v_quality_row, text="Resolution Quality:", font=("Arial", 10))
v_quality_label.pack(side="left")

help_label = tk.Label(v_quality_row, text="?", font=("Arial", 10, "bold", "underline"), cursor="hand2")
help_label.pack(side="left", padx=5)

v_quality_value = tk.Label(v_quality_row, text="[Best]", font=("Arial", 10, "bold"))
v_quality_value.pack(side="left", padx=10)

video_quality_slider = tk.Scale(video_tab, from_=0, to=len(video_quality_options)-1, orient="horizontal", showvalue=False, command=snap_quality_slider, length=SLIDER_LAYOUT_WIDTH)
video_quality_slider.pack(anchor="w", padx=15, pady=(0, 10))

global v_fps_row
v_fps_row = tk.Frame(video_tab)
v_fps_row.pack(fill="x", padx=15, pady=(5, 0))

v_fps_label = tk.Label(v_fps_row, text="Frame Rate Speed:", font=("Arial", 10))
v_fps_label.pack(side="left")

v_fps_value = tk.Label(v_fps_row, text="[Default]", font=("Arial", 10, "bold"))
v_fps_value.pack(side="left", padx=10)

video_fps_slider = tk.Scale(video_tab, from_=0, to=len(fps_options)-1, orient="horizontal", showvalue=False, command=snap_fps_slider, length=SLIDER_LAYOUT_WIDTH)
video_fps_slider.pack(anchor="w", padx=15, pady=(0, 10))

for widget in v_fps_row.winfo_children():
    widget.destroy()

v_fps_label = tk.Label(v_fps_row, text="Frame Rate (FPS):", font=("Arial", 10))
v_fps_label.pack(side="left")

v_fps_help = tk.Label(v_fps_row, text="?", font=("Arial", 10, "bold", "underline"), cursor="hand2")
v_fps_help.pack(side="left", padx=5)

v_fps_value = tk.Label(v_fps_row, text="[Default]", font=("Arial", 10, "bold"))
v_fps_value.pack(side="left", padx=10)

v_form_row = tk.Frame(video_tab)
v_form_row.pack(fill="x", padx=15, pady=(4, 2))

v_format_label = tk.Label(v_form_row, text="Video Format:", font=("Arial", 10))
v_format_label.pack(side="left")

v_form_help = tk.Label(v_form_row, text="?", font=("Arial", 10, "bold", "underline"), cursor="hand2")
v_form_help.pack(side="left", padx=5)

format_combobox = ttk.Combobox(video_tab, values=format_options, state="readonly", font=("Arial", 10), width=VIDEO_FORMAT_BOX_WIDTH)
format_combobox.pack(anchor="w", padx=15, pady=2)
format_combobox.bind("<<ComboboxSelected>>", remove_selection_highlight)

v_bit_row = tk.Frame(video_tab)
v_bit_row.pack(fill="x", padx=15, pady=(4, 2))

v_audio_bitrate_label = tk.Label(v_bit_row, text="Audio Compression Quality (Bitrate):", font=("Arial", 10))
v_audio_bitrate_label.pack(side="left")

v_bit_help = tk.Label(v_bit_row, text="?", font=("Arial", 10, "bold", "underline"), cursor="hand2")
v_bit_help.pack(side="left", padx=5)

video_audio_bitrate_combobox = ttk.Combobox(video_tab, values=video_bitrate_options, state="readonly", font=("Arial", 10), width=AUDIO_BITRATE_BOX_WIDTH)
video_audio_bitrate_combobox.pack(anchor="w", padx=15, pady=2)
video_audio_bitrate_combobox.bind("<<ComboboxSelected>>", remove_selection_highlight)

audio_tab = tk.Frame(notebook)
notebook.add(audio_tab, text=" Audio Extractor ")

global a_format_row
a_format_row = tk.Frame(audio_tab)
a_format_row.pack(fill="x", padx=15, pady=(15, 2))

a_format_label = tk.Label(a_format_row, text="Audio Codec Output Format:", font=("Arial", 10))
a_format_label.pack(side="left")

a_help_label = tk.Label(a_format_row, text="?", font=("Arial", 10, "bold", "underline"), cursor="hand2")
a_help_label.pack(side="left", padx=5)

audio_format_options = ["MP3", "M4A", "WAV"]
audio_format_combobox = ttk.Combobox(audio_tab, values=audio_format_options, state="readonly", font=("Arial", 10), width=AUDIO_FORMAT_BOX_WIDTH)
audio_format_combobox.pack(anchor="w", padx=15, pady=5)
audio_format_combobox.bind("<<ComboboxSelected>>", remove_selection_highlight)

a_bit_row = tk.Frame(audio_tab)
a_bit_row.pack(fill="x", padx=15, pady=(10, 2))

a_bitrate_label = tk.Label(a_bit_row, text="Audio Bitrate Quality:", font=("Arial", 10))
a_bitrate_label.pack(side="left")

a_bit_help = tk.Label(a_bit_row, text="?", font=("Arial", 10, "bold", "underline"), cursor="hand2")
a_bit_help.pack(side="left", padx=5)

bitrate_combobox = ttk.Combobox(audio_tab, values=audio_bitrate_options, state="readonly", font=("Arial", 10), width=AUDIO_BITRATE_BOX_WIDTH)
bitrate_combobox.pack(anchor="w", padx=15, pady=5)
bitrate_combobox.bind("<<ComboboxSelected>>", remove_selection_highlight)

config = load_settings()
dir_entry.insert(0, config["save_directory"])

q_idx = config.get("video_quality_index", 0)
f_idx = config.get("video_fps_index", 0)

if q_idx >= len(video_quality_options): q_idx = 0
if f_idx >= len(fps_options): f_idx = 0

video_quality_slider.set(q_idx)
video_fps_slider.set(f_idx)
v_quality_value.config(text=f"[{video_quality_options[q_idx]}]")
v_fps_value.config(text=f"[{fps_options[f_idx]} FPS]" if fps_options[f_idx] != "Default" else "[Default]")

format_combobox.set(config.get("video_format", "MP4"))
video_audio_bitrate_combobox.set(config.get("video_audio_bitrate", "320 kbps"))
audio_format_combobox.set(config.get("audio_format", "MP3"))
bitrate_combobox.set(config.get("audio_bitrate", "320 kbps"))

try:
    notebook.select(config["selected_tab"])
except Exception:
    pass

browse_button = tk.Button(top_frame, text="Browse...", font=("Arial", 9), command=choose_directory)
browse_button.grid(row=3, column=2, padx=5)

progress_frame = tk.Frame(root)
progress_frame.pack(pady=(10, 0), fill="x", padx=25)

progress_bar = ttk.Progressbar(progress_frame, orient="horizontal", style="Horizontal.TProgressbar", mode="determinate", maximum=100)
progress_bar.pack(side="left", fill="x", expand=True, padx=(0, 10))

percent_label = tk.Label(progress_frame, text="0.0%", font=("Arial", 11, "bold"), width=6, anchor="e")
percent_label.pack(side="right")

bottom_frame = tk.Frame(root)
bottom_frame.pack(pady=5, fill="x", padx=25)
bottom_frame.columnconfigure(0, weight=1)
bottom_frame.columnconfigure(1, weight=0)
bottom_frame.columnconfigure(2, weight=1)

download_button = tk.Button(bottom_frame, text="Start Download Process", font=("Arial", 11, "bold"), bg="#4CAF50", fg="white", command=start_download)
download_button.grid(row=0, column=1, pady=5)

theme_button = tk.Button(bottom_frame, text="🌙", font=("Arial", 12), width=3, height=1, bd=1, relief="solid", command=toggle_theme)
theme_button.grid(row=0, column=2, sticky="e", pady=5)

status_label = tk.Label(root, text="Status: Idle", font=("Arial", 10, "italic"), fg="gray")
status_label.pack(pady=(0, 5))

MY_APP_SIGNATURE = "itsRainn"
global app_watermark_label

app_watermark_label = tk.Label(root, text=f"Made by {MY_APP_SIGNATURE}", font=("Arial", 8, "italic", "underline"), cursor="hand2")
app_watermark_label.pack(side="left", anchor="s", padx=10, pady=(0, 5))

MY_YOUTUBE_URL = "https://youtube.com/@heyitsrain"

def open_youtube_link(event):
    webbrowser.open_new_tab(MY_YOUTUBE_URL)

app_watermark_label.bind("<Button-1>", open_youtube_link)
ToolTip(help_label, "Note: Higher profile streams (4K/2K) require FFmpeg installed\non your local system environment path to merge audio/video tracks.")

ToolTip(help_label, "Resolution Quality:\nSelect the vertical resolution ceiling. 'Best' gets the highest available resolution.")
ToolTip(v_fps_help, "Frame Rate (FPS):\nSelect target frames per second. High values (60) are buttery smooth. Low values (2, 1) generate slideshow files.\n60+ works if the video supports an FPS higher than 60.")
ToolTip(v_form_help, "Video Format:\n- MP4: Standard universal video wrapper compatible with all players.\n- MKV: High-profile flexible wrapper that natively supports untouched direct stream copy.\n- MOV: A high-quality format created by Apple that is often used for professional video editing, though file sizes are larger.\n- WebM: A format designed by Google specifically for smooth and fast video streaming on internet websites.")
ToolTip(v_bit_help, "Audio Quality Bitrate:\n- 320 kbps to 32 kbps: Standard compressed ranges.\n- 16 kbps & 8 kbps: Crunchy mono telephone distortion presets.\n- Lossless: Raw direct stream dump. It uses the video's default bitrate.")

ToolTip(a_help_label, "Audio Output Codec:\n- MP3: Highly compatible compressed classic layout.\n- M4A: Efficient container using standard streaming frames.\n- WAV: Pure raw uncompressed wave grid format.")
ToolTip(a_bit_help, "Audio Bitrate Compression Quality:\n- 320 kbps to 32 kbps: Standard quality targets.\n- 16 kbps & 8 kbps: Crunchy mono telephone distortion presets.\n- Lossless: Byte-for-byte original track extractor pass. Valid for M4A and WAV options.")

root.protocol("WM_DELETE_WINDOW", lambda: [save_current_settings(), root.destroy()])

is_dark_mode = config.get("dark_mode", False)
update_theme_ui()

root.mainloop()
