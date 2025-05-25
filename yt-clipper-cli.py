import yt_dlp
import subprocess
import os
import time
import argparse

def download_and_trim_clip(url, start_time, end_time, output_folder, title):
    # Create output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)
    
    # Generate file paths
    temp_file = os.path.join(output_folder, "temp_full_video.mp4")
    output_file = os.path.join(output_folder, "optimized_clip.mp4")

    # Initialize timers
    start_total = time.time()
    download_time = 0
    process_time = 0

    # Step 1: Download full video (temporarily)
    ydl_opts = {
        'format': 'best[height<=360]',  # 360p or lower
        'outtmpl': temp_file.replace('.mp4', '.%(ext)s'),
        'quiet': False,
    }

    try:
        print("Starting download...")
        download_start = time.time()
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        
        download_time = time.time() - download_start
        print(f"Download completed in {download_time:.2f} seconds")

        # Step 2: Trim and encode with custom FFmpeg parameters
        print("Starting video processing...")
        process_start = time.time()
        
        subprocess.run([
            'ffmpeg',
            '-i', temp_file,
            '-ss', start_time,
            '-to', end_time,
            '-vf', 'scale=256:144',          # Resize to 256x144
            '-c:v', 'libx264',               # H.264 video codec
            '-vf', (
                        f'scale=256:144,'
                        f'drawtext='
                        f'text=\'{title}\':'  # Telugu text here
                        f'fontfile=/Library/Fonts/Arial\\ Unicode.ttf:'  # Path to Gurajada font
                        f'fontsize=16:'
                        f'fontcolor=white:'
                        f'box=1:boxcolor=black@0.5:'
                        f'x=(w-text_w)/2:y=h-text_h-10'
                    ),            
            '-preset', 'medium',               # Better compression
            '-b:v', '86k',                 # Video bitrate
            '-maxrate', '86k',             # same as bitrate
            '-bufsize', '172k',             # 2× the target bitrate
            '-c:a', 'aac',                  # AAC audio codec
            '-b:a', '64k',                  # Audio bitrate
            '-movflags', '+faststart',      # Enable streaming
            output_file
        ], check=True)
        
        process_time = time.time() - process_start
        print(f"Processing completed in {process_time:.2f} seconds")

        total_time = time.time() - start_total
        print("\nSummary:")
        print(f"  - Download time: {download_time:.2f}s")
        print(f"  - Processing time: {process_time:.2f}s")
        print(f"  - Total time: {total_time:.2f}s")
        print(f"\nSuccess! Optimized clip saved as: {output_file}")

    except subprocess.CalledProcessError as e:
        print(f"FFmpeg error: {e.stderr}")
    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        # Clean up
        if os.path.exists(temp_file):
            os.remove(temp_file)
            print("\nTemporary file removed.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Download and trim YouTube clips')
    parser.add_argument('--url', '-u', required=True, help='YouTube video URL')
    parser.add_argument('--start', '-s', required=True, help='Start time in HH:MM:SS format')
    parser.add_argument('--end', '-e', required=True, help='End time in HH:MM:SS format')
    parser.add_argument('--output', '-o', default='./', 
                       help='Output folder (default: current directory)')
    parser.add_argument('--title', '-t', required=True, help='title text')    
    args = parser.parse_args()
    
    download_and_trim_clip(
        args.url,
        args.start,
        args.end,
        args.output,
        args.title
    )