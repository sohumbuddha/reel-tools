import yt_dlp
import subprocess
import os
import time
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

class YouTubeClipDownloader:
    def __init__(self, root):
        self.root = root
        root.title("YouTube Clip Downloader")
        root.geometry("500x400")
        
        # Variables
        self.url_var = tk.StringVar()
        self.start_var = tk.StringVar(value="00:00:00")
        self.end_var = tk.StringVar(value="00:00:30")
        self.path_var = tk.StringVar()
        self.status_var = tk.StringVar(value="Ready")
        self.progress_var = tk.DoubleVar()
        
        # GUI Elements
        self.create_widgets()
        
    def create_widgets(self):
        # URL Input
        tk.Label(self.root, text="YouTube URL:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        tk.Entry(self.root, textvariable=self.url_var, width=50).grid(row=0, column=1, padx=10, pady=5)
        
        # Time Inputs
        tk.Label(self.root, text="Start Time (HH:MM:SS):").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        tk.Entry(self.root, textvariable=self.start_var, width=15).grid(row=1, column=1, padx=10, pady=5, sticky="w")
        
        tk.Label(self.root, text="End Time (HH:MM:SS):").grid(row=2, column=0, padx=10, pady=5, sticky="w")
        tk.Entry(self.root, textvariable=self.end_var, width=15).grid(row=2, column=1, padx=10, pady=5, sticky="w")
        
        # Path Selection
        tk.Label(self.root, text="Download Folder:").grid(row=3, column=0, padx=10, pady=5, sticky="w")
        tk.Entry(self.root, textvariable=self.path_var, width=40).grid(row=3, column=1, padx=10, pady=5)
        tk.Button(self.root, text="Browse", command=self.browse_folder).grid(row=3, column=2, padx=5, pady=5)
        
        # Progress Bar
        ttk.Progressbar(self.root, variable=self.progress_var, maximum=100).grid(row=4, column=0, columnspan=3, padx=10, pady=10, sticky="ew")
        
        # Status Label
        tk.Label(self.root, textvariable=self.status_var).grid(row=5, column=0, columnspan=3, padx=10, pady=5)
        
        # Download Button
        tk.Button(self.root, text="Download Clip", command=self.start_download, bg="green", fg="white").grid(row=6, column=0, columnspan=3, pady=15)
        
    def browse_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.path_var.set(folder)
    
    def start_download(self):
        url = self.url_var.get()
        start = self.start_var.get()
        end = self.end_var.get()
        path = self.path_var.get()
        
        if not all([url, start, end, path]):
            messagebox.showerror("Error", "Please fill all fields")
            return
            
        try:
            self.status_var.set("Starting download...")
            self.root.update()
            
            # Run download in background
            self.root.after(100, lambda: self.download_and_process(url, start, end, path))
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    def download_and_process(self, url, start_time, end_time, path):
        try:
            start_total = time.time()
            temp_file = os.path.join(path, "temp_video.mp4")
            output_file = os.path.join(path, f"clip_{time.strftime('%Y%m%d_%H%M%S')}.mp4")
            
            # Download
            self.status_var.set("Downloading video...")
            self.progress_var.set(20)
            self.root.update()
            
            download_start = time.time()
            ydl_opts = {
                'format': '18',  # Using specific format code instead of quality filter
                'outtmpl': temp_file,
                'noprogress': False,
                'progress_hooks': [self.download_progress],
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            
            download_time = time.time() - download_start
            
            # Processing
            self.status_var.set("Processing video...")
            self.progress_var.set(70)
            self.root.update()
            
            process_start = time.time()
            subprocess.run([
                'ffmpeg',
                '-i', temp_file,
                '-ss', start_time,
                '-to', end_time,
                '-vf', 'scale=256:144',
                '-c:v', 'libx264',
                '-preset', 'slow',
                '-b:v', '414k',
                '-c:a', 'aac',
                '-b:a', '64k',
                '-movflags', '+faststart',
                output_file
            ], check=True)
            
            process_time = time.time() - process_start
            total_time = time.time() - start_total
            
            # Cleanup
            if os.path.exists(temp_file):
                os.remove(temp_file)
            
            # Update UI
            self.progress_var.set(100)
            self.status_var.set(
                f"Done! Downloaded in {download_time:.1f}s, "
                f"Processed in {process_time:.1f}s, "
                f"Total: {total_time:.1f}s\n"
                f"Saved to: {output_file}"
            )
            
            messagebox.showinfo("Success", "Clip downloaded and processed successfully!")
            
        except Exception as e:
            self.status_var.set("Error occurred")
            messagebox.showerror("Error", str(e))
        finally:
            self.progress_var.set(0)
    
    def download_progress(self, d):
        if d['status'] == 'downloading':
            try:
                # Safely handle percentage conversion
                percent_str = d.get('_percent_str', '0%').strip('%')
                percent = float(percent_str) if percent_str.replace('.', '').isdigit() else 0
                
                # Scale to 0-50% for download phase (processing will take it to 100%)
                self.progress_var.set(percent/2)
                
                # Update status with available information
                status_parts = [
                    f"Downloading... {percent:.1f}%",
                    f"Speed: {d.get('_speed_str', 'N/A')}",
                    f"ETA: {d.get('_eta_str', 'N/A')}"
                ]
                self.status_var.set(" | ".join(status_parts))
                self.root.update()
            except Exception as e:
                # If progress parsing fails, just show basic status
                self.status_var.set("Downloading... (progress unavailable)")
                self.root.update()

if __name__ == "__main__":
    root = tk.Tk()
    app = YouTubeClipDownloader(root)
    root.mainloop()