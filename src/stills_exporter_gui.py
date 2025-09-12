#!/usr/bin/env python3
"""
Stills Exporter GUI - Cross-platform video frame extraction tool
Supports Windows and macOS with a simple, intuitive interface.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import subprocess
import threading
import json
from pathlib import Path
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
import shutil

class StillsExporterGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Stills Exporter")
        self.root.geometry("600x500")
        self.root.resizable(True, True)
        
        # Variables
        self.source_folder = tk.StringVar()
        self.output_folder = tk.StringVar()
        self.frames_per_clip = tk.IntVar(value=10)
        self.image_format = tk.StringVar(value="png")
        self.max_workers = tk.IntVar(value=min(4, os.cpu_count() or 1))
        
        # Check for ffmpeg
        self.ffmpeg_available = self.check_ffmpeg()
        
        self.setup_ui()
        self.load_settings()
        
    def check_ffmpeg(self):
        """Check if ffmpeg is available in PATH"""
        return shutil.which("ffmpeg") is not None
        
    def setup_ui(self):
        """Create the user interface"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        row = 0
        
        # Title
        title_label = ttk.Label(main_frame, text="Video Stills Exporter", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=row, column=0, columnspan=3, pady=(0, 20))
        row += 1
        
        # FFmpeg status
        if not self.ffmpeg_available:
            warning_frame = ttk.Frame(main_frame)
            warning_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
            warning_label = ttk.Label(warning_frame, 
                                    text="⚠️ FFmpeg not found in PATH. Please install FFmpeg first.",
                                    foreground="red")
            warning_label.pack()
            row += 1
        
        # Source folder
        ttk.Label(main_frame, text="Source Folder:").grid(row=row, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.source_folder, width=50).grid(row=row, column=1, sticky=(tk.W, tk.E), padx=5)
        ttk.Button(main_frame, text="Browse", command=self.browse_source).grid(row=row, column=2, padx=5)
        row += 1
        
        # Output folder
        ttk.Label(main_frame, text="Output Folder:").grid(row=row, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.output_folder, width=50).grid(row=row, column=1, sticky=(tk.W, tk.E), padx=5)
        ttk.Button(main_frame, text="Browse", command=self.browse_output).grid(row=row, column=2, padx=5)
        row += 1
        
        # Settings frame
        settings_frame = ttk.LabelFrame(main_frame, text="Settings", padding="10")
        settings_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        settings_frame.columnconfigure(1, weight=1)
        row += 1
        
        # Frames per clip
        ttk.Label(settings_frame, text="Frames per clip:").grid(row=0, column=0, sticky=tk.W, pady=2)
        frames_spinbox = ttk.Spinbox(settings_frame, from_=1, to=100, textvariable=self.frames_per_clip, width=10)
        frames_spinbox.grid(row=0, column=1, sticky=tk.W, padx=5)
        
        # Image format
        ttk.Label(settings_frame, text="Image format:").grid(row=1, column=0, sticky=tk.W, pady=2)
        format_combo = ttk.Combobox(settings_frame, textvariable=self.image_format, 
                                   values=["png", "jpg", "bmp", "tiff"], width=10, state="readonly")
        format_combo.grid(row=1, column=1, sticky=tk.W, padx=5)
        
        # Max workers
        ttk.Label(settings_frame, text="Parallel workers:").grid(row=2, column=0, sticky=tk.W, pady=2)
        workers_spinbox = ttk.Spinbox(settings_frame, from_=1, to=16, textvariable=self.max_workers, width=10)
        workers_spinbox.grid(row=2, column=1, sticky=tk.W, padx=5)
        
        # Progress frame
        progress_frame = ttk.LabelFrame(main_frame, text="Progress", padding="10")
        progress_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        progress_frame.columnconfigure(0, weight=1)
        row += 1
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=2)
        
        # Status label
        self.status_var = tk.StringVar(value="Ready")
        self.status_label = ttk.Label(progress_frame, textvariable=self.status_var)
        self.status_label.grid(row=1, column=0, sticky=tk.W, pady=2)
        
        # Log text area
        log_frame = ttk.LabelFrame(main_frame, text="Log", padding="5")
        log_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        main_frame.rowconfigure(row, weight=1)
        row += 1
        
        # Text widget with scrollbar
        text_frame = ttk.Frame(log_frame)
        text_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        text_frame.columnconfigure(0, weight=1)
        text_frame.rowconfigure(0, weight=1)
        
        self.log_text = tk.Text(text_frame, height=8, wrap=tk.WORD)
        scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Buttons frame
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.grid(row=row, column=0, columnspan=3, pady=10)
        
        self.export_button = ttk.Button(buttons_frame, text="Start Export", command=self.start_export)
        self.export_button.pack(side=tk.LEFT, padx=5)
        
        self.stop_button = ttk.Button(buttons_frame, text="Stop", command=self.stop_export, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(buttons_frame, text="Clear Log", command=self.clear_log).pack(side=tk.LEFT, padx=5)
        
        # Initialize
        self.export_thread = None
        self.stop_flag = threading.Event()
        
    def browse_source(self):
        folder = filedialog.askdirectory(title="Select Source Folder")
        if folder:
            self.source_folder.set(folder)
            
    def browse_output(self):
        folder = filedialog.askdirectory(title="Select Output Folder")
        if folder:
            self.output_folder.set(folder)
            
    def log_message(self, message):
        """Add message to log with timestamp"""
        import datetime
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()
        
    def clear_log(self):
        self.log_text.delete(1.0, tk.END)
        
    def update_status(self, message):
        self.status_var.set(message)
        self.root.update_idletasks()
        
    def update_progress(self, value):
        self.progress_var.set(value)
        self.root.update_idletasks()

    def get_video_files(self, folder):
        """Get all video files from the specified folder"""
        video_extensions = {'.mp4', '.mov', '.mxf', '.mkv', '.avi', '.mts', '.m2ts',
                           '.wmv', '.webm', '.3gp', '.m4v', '.flv', '.f4v'}

        video_files = []
        folder_path = Path(folder)

        for ext in video_extensions:
            video_files.extend(folder_path.glob(f"*{ext}"))
            video_files.extend(folder_path.glob(f"*{ext.upper()}"))

        return sorted(video_files)

    def get_clean_filename(self, filename):
        """Clean filename for safe file operations"""
        import re
        base = Path(filename).stem
        # Remove special characters, keep alphanumeric, hyphens, dots, parentheses, spaces
        clean = re.sub(r'[^\w\-\.\(\) ]', '', base)
        # Replace multiple spaces with underscores
        clean = re.sub(r' +', '_', clean)
        return clean

    def get_video_duration(self, video_path):
        """Get video duration using ffprobe"""
        try:
            cmd = [
                'ffprobe', '-v', 'error', '-show_entries', 'format=duration',
                '-of', 'default=nk=1:nw=1', str(video_path)
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if result.returncode == 0 and result.stdout.strip():
                return float(result.stdout.strip())
        except (subprocess.TimeoutExpired, ValueError, FileNotFoundError):
            pass
        return None

    def calculate_timestamps(self, duration, frames_count):
        """Calculate evenly spaced timestamps, avoiding head/tail"""
        timestamps = []
        epsilon = min(0.25, duration * 0.01)  # 250ms or 1% of duration

        for i in range(1, frames_count + 1):
            t = (duration * i) / (frames_count + 1)
            t = max(epsilon, min(duration - epsilon, t))
            timestamps.append(t)

        return timestamps

    def extract_frames_batch(self, video_path, timestamps, output_folder, base_name, image_format):
        """Extract multiple frames in a single ffmpeg call for better efficiency"""
        output_folder = Path(output_folder)
        output_folder.mkdir(parents=True, exist_ok=True)

        extracted_count = 0

        # Create a filter complex for multiple outputs
        if len(timestamps) > 1:
            # Use filter_complex for multiple timestamps
            filter_parts = []
            output_parts = []

            for i, timestamp in enumerate(timestamps):
                idx_str = f"{i+1:03d}"
                output_path = output_folder / f"{base_name}_{idx_str}.{image_format}"

                filter_parts.append(f"[0:v]select='eq(n,{int(timestamp * 30)})'[out{i}]")
                output_parts.extend([f"-map", f"[out{i}]", f"-frames:v", "1", str(output_path)])

            cmd = [
                'ffmpeg', '-hide_banner', '-loglevel', 'error', '-y',
                '-i', str(video_path),
                '-filter_complex', ';'.join(filter_parts)
            ] + output_parts

        else:
            # Single frame extraction
            timestamp = timestamps[0]
            output_path = output_folder / f"{base_name}_001.{image_format}"
            cmd = [
                'ffmpeg', '-hide_banner', '-loglevel', 'error', '-y',
                '-i', str(video_path), '-ss', str(timestamp),
                '-frames:v', '1', str(output_path)
            ]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            if result.returncode == 0:
                # Count successfully created files
                for i, timestamp in enumerate(timestamps):
                    idx_str = f"{i+1:03d}"
                    output_path = output_folder / f"{base_name}_{idx_str}.{image_format}"
                    if output_path.exists():
                        extracted_count += 1
            else:
                self.log_message(f"FFmpeg error for {video_path.name}: {result.stderr}")

        except subprocess.TimeoutExpired:
            self.log_message(f"Timeout extracting frames from {video_path.name}")
        except Exception as e:
            self.log_message(f"Error extracting frames from {video_path.name}: {str(e)}")

        return extracted_count

    def process_single_video(self, video_path, output_folder, frames_per_clip, image_format):
        """Process a single video file"""
        if self.stop_flag.is_set():
            return 0, 0

        base_name = self.get_clean_filename(video_path.name)

        # Get video duration
        duration = self.get_video_duration(video_path)
        if duration is None or duration <= 0:
            self.log_message(f"Could not read duration for {video_path.name}, skipping")
            return 0, 0

        # Calculate timestamps
        timestamps = self.calculate_timestamps(duration, frames_per_clip)

        # Extract frames
        extracted_count = self.extract_frames_batch(
            video_path, timestamps, output_folder, base_name, image_format
        )

        return 1, extracted_count  # processed_count, frames_count

    def export_stills(self):
        """Main export function with parallel processing"""
        source = self.source_folder.get().strip()
        output = self.output_folder.get().strip()
        frames = self.frames_per_clip.get()
        img_format = self.image_format.get()
        max_workers = self.max_workers.get()

        # Validation
        if not source or not os.path.exists(source):
            messagebox.showerror("Error", "Please select a valid source folder")
            return

        if not output:
            messagebox.showerror("Error", "Please select an output folder")
            return

        if not self.ffmpeg_available:
            messagebox.showerror("Error", "FFmpeg is not available. Please install FFmpeg first.")
            return

        # Create output directory
        os.makedirs(output, exist_ok=True)

        # Get video files
        self.log_message("Scanning for video files...")
        video_files = self.get_video_files(source)

        if not video_files:
            self.log_message("No video files found in the source folder")
            messagebox.showwarning("Warning", "No video files found in the source folder")
            return

        self.log_message(f"Found {len(video_files)} video files")
        self.log_message(f"Target: {frames} {img_format} frames per clip")
        self.log_message(f"Using {max_workers} parallel workers")
        self.log_message("Starting export...")

        # Reset progress
        self.update_progress(0)
        total_processed = 0
        total_frames = 0

        # Process videos in parallel
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all jobs
            future_to_video = {
                executor.submit(
                    self.process_single_video,
                    video_path, output, frames, img_format
                ): video_path
                for video_path in video_files
            }

            # Process completed jobs
            for future in as_completed(future_to_video):
                if self.stop_flag.is_set():
                    break

                video_path = future_to_video[future]
                try:
                    processed_count, frames_count = future.result()
                    total_processed += processed_count
                    total_frames += frames_count

                    self.log_message(f"{video_path.name} → {frames_count} frames")

                    # Update progress
                    progress = (total_processed / len(video_files)) * 100
                    self.update_progress(progress)
                    self.update_status(f"Processed {total_processed}/{len(video_files)} videos")

                except Exception as e:
                    self.log_message(f"Error processing {video_path.name}: {str(e)}")

        # Final status
        if self.stop_flag.is_set():
            self.log_message("Export stopped by user")
            self.update_status("Export stopped")
        else:
            self.log_message(f"Export completed! Processed {total_processed} videos, extracted {total_frames} frames")
            self.update_status("Export completed")
            self.update_progress(100)

        self.save_settings()

    def start_export(self):
        """Start the export process in a separate thread"""
        if self.export_thread and self.export_thread.is_alive():
            return

        self.stop_flag.clear()
        self.export_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)

        self.export_thread = threading.Thread(target=self.export_worker)
        self.export_thread.daemon = True
        self.export_thread.start()

    def export_worker(self):
        """Worker thread for export process"""
        try:
            self.export_stills()
        except Exception as e:
            self.log_message(f"Export error: {str(e)}")
        finally:
            # Re-enable UI
            self.root.after(0, self.reset_ui)

    def stop_export(self):
        """Stop the export process"""
        self.stop_flag.set()
        self.update_status("Stopping...")

    def reset_ui(self):
        """Reset UI after export completion"""
        self.export_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)

    def save_settings(self):
        """Save current settings to a config file"""
        settings = {
            'source_folder': self.source_folder.get(),
            'output_folder': self.output_folder.get(),
            'frames_per_clip': self.frames_per_clip.get(),
            'image_format': self.image_format.get(),
            'max_workers': self.max_workers.get()
        }

        try:
            config_path = Path.home() / '.stills_exporter_config.json'
            with open(config_path, 'w') as f:
                json.dump(settings, f, indent=2)
        except Exception:
            pass  # Ignore save errors

    def load_settings(self):
        """Load settings from config file"""
        try:
            config_path = Path.home() / '.stills_exporter_config.json'
            if config_path.exists():
                with open(config_path, 'r') as f:
                    settings = json.load(f)

                self.source_folder.set(settings.get('source_folder', ''))
                self.output_folder.set(settings.get('output_folder', ''))
                self.frames_per_clip.set(settings.get('frames_per_clip', 10))
                self.image_format.set(settings.get('image_format', 'png'))
                self.max_workers.set(settings.get('max_workers', min(4, os.cpu_count() or 1)))
        except Exception:
            pass  # Ignore load errors


def main():
    """Main entry point"""
    root = tk.Tk()
    app = StillsExporterGUI(root)

    # Center window on screen
    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - (root.winfo_width() // 2)
    y = (root.winfo_screenheight() // 2) - (root.winfo_height() // 2)
    root.geometry(f"+{x}+{y}")

    root.mainloop()


if __name__ == "__main__":
    main()
