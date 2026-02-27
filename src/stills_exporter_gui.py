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
try:
    from vision_tagger import VisionTagger, VISION_AVAILABLE, LANGCHAIN_AVAILABLE
except ImportError:
    try:
        from src.vision_tagger import VisionTagger, VISION_AVAILABLE, LANGCHAIN_AVAILABLE
    except ImportError:
        VISION_AVAILABLE = False
        LANGCHAIN_AVAILABLE = False
        class VisionTagger:
            def __init__(self, *args, **kwargs): pass

# Try to import the new gallery-based system
try:
    from src.ai.gallery_vision_tagger import GalleryVisionTagger
    from src.ai.gallery_manager import GalleryManager
    from src.pipeline.enhanced_video_processor import EnhancedVideoProcessor
    GALLERY_SYSTEM_AVAILABLE = True
except ImportError:
    GALLERY_SYSTEM_AVAILABLE = False
    class GalleryVisionTagger:
        def __init__(self, *args, **kwargs): pass
    class GalleryManager:
        def __init__(self, *args, **kwargs): pass
    class EnhancedVideoProcessor:
        def __init__(self, *args, **kwargs): pass

try:
    from exif_embedder import ExifEmbedder
except ImportError:
    try:
        from src.exif_embedder import ExifEmbedder
    except ImportError:
        class ExifEmbedder:
            def __init__(self): self.exiftool_available = False

try:
    from training_manager import TrainingManager
except ImportError:
    try:
        from src.training_manager import TrainingManager
    except ImportError:
        class TrainingManager:
            def __init__(self, *args): pass
            def get_api_key(self): return ""
            def get_roboflow_api_key(self): return ""
            def get_roboflow_model_id(self): return "coco-seg-0.9.7"
            def get_training_examples(self, *args): return []

class StillsExporterGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Stills Exporter")
        self.root.geometry("600x500")
        self.root.resizable(True, True)

        # Variables
        self.source_folder = tk.StringVar()
        self.output_folder = tk.StringVar()
        self.image_format = tk.StringVar(value="png")
        self.max_workers = tk.IntVar(value=min(4, os.cpu_count() or 1))
        self.enable_ai_tagging = tk.BooleanVar(value=False)
        self.embed_metadata = tk.BooleanVar(value=False)
        self.vision_credentials = tk.StringVar()

        # Settings file path
        self.settings_file = Path.home() / ".stills_exporter_config.json"

        # Initialize training manager
        self.training_manager = TrainingManager()

        # Check for ffmpeg
        self.ffmpeg_available = self.check_ffmpeg()

        self.setup_ui()
        self.load_settings()

        # Auto-detect credentials after UI is set up
        self.auto_detect_credentials()
        if self.vision_credentials.get():
            self.log_message(f"Auto-detected credentials: {self.vision_credentials.get()}")
        self.update_ai_status()
        
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
        
        # Remove frames per clip spinbox - now automatic
        # Add info label instead
        ttk.Label(settings_frame, text="Frames per video:", font=('TkDefaultFont', 9)).grid(row=0, column=0, sticky=tk.W, pady=2)
        ttk.Label(settings_frame, text="Calculated automatically based on video duration", 
                 font=('TkDefaultFont', 8), foreground='gray').grid(row=0, column=1, sticky=tk.W, padx=5)
        
        # Image format
        ttk.Label(settings_frame, text="Image format:").grid(row=1, column=0, sticky=tk.W, pady=2)
        format_combo = ttk.Combobox(settings_frame, textvariable=self.image_format, 
                                   values=["png", "jpg", "bmp", "tiff"], state="readonly", width=10)
        format_combo.grid(row=1, column=1, sticky=tk.W, padx=5)
        
        # Max workers
        ttk.Label(settings_frame, text="Parallel workers:").grid(row=2, column=0, sticky=tk.W, pady=2)
        workers_spinbox = ttk.Spinbox(settings_frame, from_=1, to=16, textvariable=self.max_workers, width=10)
        workers_spinbox.grid(row=2, column=1, sticky=tk.W, padx=5)
        
        # AI Features section (simplified)
        ai_frame = ttk.LabelFrame(main_frame, text="AI Features", padding="5")
        ai_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        row += 1
        
        # AI Tagging checkbox
        ttk.Checkbutton(ai_frame, text="Enable AI Tagging",
                       variable=self.enable_ai_tagging, command=self.on_ai_toggle).grid(row=0, column=0, sticky=tk.W, pady=2)

        # Gallery System checkbox (new)
        self.use_gallery_system = tk.BooleanVar(value=True)  # Default to new system
        gallery_cb = ttk.Checkbutton(ai_frame, text="Use Gallery Recognition (Buildings + Enhanced Filtering)",
                                   variable=self.use_gallery_system, command=self.on_gallery_toggle)
        gallery_cb.grid(row=0, column=1, sticky=tk.W, padx=20, pady=2)

        # Credentials file selection
        cred_frame = ttk.Frame(ai_frame)
        cred_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=2)
        ttk.Label(cred_frame, text="Credentials:").pack(side=tk.LEFT)
        ttk.Entry(cred_frame, textvariable=self.vision_credentials, width=40).pack(side=tk.LEFT, padx=5)
        ttk.Button(cred_frame, text="Browse", command=self.browse_credentials).pack(side=tk.LEFT)
        
        # Auto-detect credentials on startup
        self.auto_detect_credentials()
        
        # Metadata embedding checkbox
        ttk.Checkbutton(ai_frame, text="Embed Metadata", 
                       variable=self.embed_metadata).grid(row=2, column=0, sticky=tk.W, pady=2)
        
        # AI Status label
        self.ai_status = ttk.Label(ai_frame, text="", font=('TkDefaultFont', 8))
        self.ai_status.grid(row=3, column=0, sticky=tk.W, pady=2)
        self.update_ai_status()
        
        # Progress section
        progress_frame = ttk.LabelFrame(main_frame, text="Progress", padding="5")
        progress_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        progress_frame.columnconfigure(0, weight=1)
        row += 1
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=2)
        
        # Status label
        self.status_label = ttk.Label(progress_frame, text="Ready")
        self.status_label.grid(row=1, column=0, sticky=tk.W, pady=2)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=row, column=0, columnspan=3, pady=10)
        
        self.export_button = ttk.Button(button_frame, text="Start Export", command=self.start_export)
        self.export_button.grid(row=0, column=0, padx=5)
        
        self.stop_button = ttk.Button(button_frame, text="Stop", command=self.stop_export, state=tk.DISABLED)
        self.stop_button.grid(row=0, column=1, padx=5)
        
        # Log area
        log_frame = ttk.LabelFrame(main_frame, text="Log", padding="5")
        log_frame.grid(row=row+1, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        main_frame.rowconfigure(row+1, weight=1)
        
        # Text widget with scrollbar
        self.log_text = tk.Text(log_frame, height=8, wrap=tk.WORD)
        scrollbar = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Initialize threading
        self.export_thread = None
        self.stop_flag = threading.Event()

        # Log initialization completion
        self.log_message("✅ Stills Exporter initialized successfully")
        self.log_message("Click 'Browse' buttons to select source and output folders")
        
    def setup_ai_section(self, parent):
        """Setup AI tagging section"""
        ai_frame = ttk.LabelFrame(parent, text="AI Features (LangChain + Gemini)", padding="10")
        ai_frame.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
        ai_frame.columnconfigure(1, weight=1)

        # Enable AI tagging
        ttk.Checkbutton(ai_frame, text="Enable AI Tagging with Few-Shot Learning",
                       variable=self.enable_ai_tagging,
                       command=self.on_ai_toggle).grid(row=0, column=0, columnspan=3, sticky=tk.W)

        # Training examples info (using max 3 per category for efficiency)
        training_examples = self.training_manager.get_training_examples(max_per_category=3)
        training_info = ttk.Label(ai_frame,
                                 text=f"Training examples: {len(training_examples)} (3 per category for speed)",
                                 foreground="blue")
        training_info.grid(row=1, column=0, columnspan=3, sticky=tk.W, pady=(5, 0))

        # Show categories
        categories = self.training_manager.list_categories()
        if categories:
            cat_text = "Categories: " + ", ".join(categories)
            ttk.Label(ai_frame, text=cat_text, foreground="gray").grid(
                row=2, column=0, columnspan=3, sticky=tk.W, pady=(2, 0))

        # Embed metadata
        ttk.Checkbutton(ai_frame, text="Embed metadata into videos (ExifTool)",
                       variable=self.embed_metadata).grid(row=3, column=0, columnspan=2, sticky=tk.W, pady=(5, 0))

        # Status
        self.ai_status = ttk.Label(ai_frame, text="", foreground="gray")
        self.ai_status.grid(row=4, column=0, columnspan=3, sticky=tk.W, pady=(5, 0))

        self.update_ai_status()

    def auto_detect_credentials(self):
        """Auto-detect Google Cloud credentials file"""
        possible_files = [
            "google-vision-credentials.json",
            "credentials.json",
            "service-account.json",
            "vision-credentials.json"
        ]
        
        for filename in possible_files:
            if Path(filename).exists():
                self.vision_credentials.set(filename)
                # Don't log here - log_text doesn't exist yet
                break

    def on_ai_toggle(self):
        """Handle AI toggle"""
        self.update_ai_status()

    def on_gallery_toggle(self):
        """Handle gallery system toggle"""
        self.update_ai_status()

    def update_ai_status(self):
        """Update AI status display"""
        if not self.enable_ai_tagging.get():
            self.ai_status.config(text="AI tagging disabled", foreground="gray")
            return

        # Check for an API key — Roboflow takes priority over Google
        roboflow_key = self.training_manager.get_roboflow_api_key()
        google_key = self.training_manager.get_api_key()

        if not roboflow_key and not google_key:
            self.ai_status.config(
                text="⚠️ No API key configured — add roboflow_api_key to config/ai_config.json",
                foreground="orange")
            return

        # Check which system to use
        if self.use_gallery_system.get() and GALLERY_SYSTEM_AVAILABLE:
            # Gallery system status
            try:
                gallery_manager = GalleryManager()
                gallery_stats = gallery_manager.get_statistics()
                total_items = gallery_stats.get('total_items', 0)
                categories = len(gallery_stats.get('categories', {}))

                self.ai_status.config(
                    text=f"✓ Gallery System | {total_items} items, {categories} categories | Enhanced filtering",
                    foreground="green")
            except Exception as e:
                self.ai_status.config(text=f"⚠️ Gallery system error: {str(e)[:40]}...",
                                     foreground="orange")
        else:
            # Show which backend will be used
            try:
                from vision_tagger import ROBOFLOW_AVAILABLE, LANGCHAIN_AVAILABLE
                if ROBOFLOW_AVAILABLE and roboflow_key:
                    model = self.training_manager.get_roboflow_model_id()
                    self.ai_status.config(
                        text=f"✓ Roboflow | model: {model}",
                        foreground="green")
                elif LANGCHAIN_AVAILABLE and google_key:
                    training_count = len(self.training_manager.get_training_examples(max_per_category=3))
                    self.ai_status.config(
                        text=f"✓ LangChain + Gemini | {training_count} examples",
                        foreground="blue")
                elif VISION_AVAILABLE:
                    self.ai_status.config(text="✓ Using legacy Google Vision API",
                                         foreground="blue")
                else:
                    self.ai_status.config(text="⚠️ No AI libraries installed — mock mode",
                                         foreground="orange")
            except Exception as e:
                self.ai_status.config(text=f"⚠️ Error: {str(e)[:50]}...",
                                     foreground="red")

    def browse_credentials(self):
        """Browse for Google Cloud credentials JSON with proper parent window handling"""
        try:
            filename = filedialog.askopenfilename(
                title="Select Google Cloud Credentials JSON",
                parent=self.root,
                initialdir=os.path.expanduser("~"),
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
            )
            if filename:
                self.vision_credentials.set(filename)
                self.log_message(f"Credentials file selected: {filename}")
                self.update_ai_status()
            else:
                self.log_message("Credentials file selection cancelled")
        except Exception as e:
            self.log_message(f"Error selecting credentials file: {str(e)}")
            messagebox.showerror("Error", f"Failed to open file dialog: {str(e)}")
            
    def browse_source(self):
        """Browse for source folder with proper parent window handling"""
        try:
            # Ensure the dialog appears on top and is modal to this window
            folder = filedialog.askdirectory(
                title="Select Source Folder",
                parent=self.root,
                initialdir=os.path.expanduser("~")
            )
            if folder:
                self.source_folder.set(folder)
                self.log_message(f"Source folder selected: {folder}")
            else:
                self.log_message("Source folder selection cancelled")
        except Exception as e:
            self.log_message(f"Error selecting source folder: {str(e)}")
            messagebox.showerror("Error", f"Failed to open folder dialog: {str(e)}")

    def browse_output(self):
        """Browse for output folder with proper parent window handling"""
        try:
            # Ensure the dialog appears on top and is modal to this window
            folder = filedialog.askdirectory(
                title="Select Output Folder",
                parent=self.root,
                initialdir=os.path.expanduser("~")
            )
            if folder:
                self.output_folder.set(folder)
                self.log_message(f"Output folder selected: {folder}")
            else:
                self.log_message("Output folder selection cancelled")
        except Exception as e:
            self.log_message(f"Error selecting output folder: {str(e)}")
            messagebox.showerror("Error", f"Failed to open folder dialog: {str(e)}")
            
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
        self.status_label.config(text=message)
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

    def calculate_optimal_frames(self, duration_seconds):
        """Calculate optimal number of frames based on video duration"""
        if duration_seconds <= 0:
            return 5  # Default fallback
        
        # Smart frame calculation logic
        if duration_seconds <= 30:      # 0-30 seconds: 5 frames
            return 5
        elif duration_seconds <= 60:    # 30s-1min: 10 frames
            return 10
        elif duration_seconds <= 120:   # 1-2 minutes: 15 frames
            return 15
        elif duration_seconds <= 300:   # 2-5 minutes: 20 frames
            return 20
        elif duration_seconds <= 600:   # 5-10 minutes: 25 frames
            return 25
        elif duration_seconds <= 1800:  # 10-30 minutes: 30 frames
            return 30
        else:                          # 30+ minutes: 40 frames max
            return 40

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

    def process_single_video_with_ai(self, video_path, output_folder, image_format):
        """Enhanced video processing with AI tagging - frames calculated automatically"""
        if self.stop_flag.is_set():
            return 0, 0

        base_name = self.get_clean_filename(video_path.name)
        clip_stills_folder = Path(output_folder) / f"{base_name}_Stills"
        clip_stills_folder.mkdir(exist_ok=True)

        # Step 1: Get duration and calculate optimal frames
        duration = self.get_video_duration(video_path)
        if duration is None or duration <= 0:
            self.log_message(f"Could not read duration for {video_path.name}, skipping")
            return 0, 0

        # Calculate optimal frames based on duration
        frames_per_clip = self.calculate_optimal_frames(duration)
        self.log_message(f"{video_path.name}: {duration:.1f}s → {frames_per_clip} frames")

        timestamps = self.calculate_timestamps(duration, frames_per_clip)
        extracted_count = self.extract_frames_batch(
            video_path, timestamps, clip_stills_folder, base_name, image_format
        )

        if extracted_count == 0:
            return 0, 0

        # Step 2: AI Tagging (if enabled)
        if self.enable_ai_tagging.get():
            self.log_message(f"AI Tagging enabled for {video_path.name}")

            try:
                if self.use_gallery_system.get() and GALLERY_SYSTEM_AVAILABLE:
                    # Use new gallery-based system
                    self.log_message("✓ Using Gallery Recognition System")

                    # Prefer Roboflow key, fall back to Google key
                    api_key = (self.training_manager.get_roboflow_api_key()
                               or self.training_manager.get_api_key())
                    if not api_key:
                        self.log_message("❌ No API key configured — add roboflow_api_key to config/ai_config.json")
                        return 1, extracted_count

                    # Initialize enhanced processor
                    processor = EnhancedVideoProcessor(api_key=api_key)

                    # Process video with gallery system
                    result = processor.process_video_with_gallery(
                        video_path=video_path,
                        output_dir=clip_stills_folder.parent
                    )

                    if result.get('success'):
                        gallery_matches = result.get('gallery_matches', [])
                        final_tags = result.get('final_tags', [])

                        self.log_message(f"✅ Gallery processing complete:")
                        self.log_message(f"  Gallery matches: {len(gallery_matches)}")
                        self.log_message(f"  Final tags: {len(final_tags)}")

                        # Show top results
                        if gallery_matches:
                            self.log_message("  Top gallery matches:")
                            for match in gallery_matches[:3]:
                                self.log_message(f"    - {match['gallery_label']} ({match['confidence']:.2f})")

                        if final_tags:
                            self.log_message("  Top tags:")
                            for tag in final_tags[:5]:
                                self.log_message(f"    - {tag['tag']} ({tag['confidence']:.2f})")
                    else:
                        self.log_message(f"❌ Gallery processing failed: {result.get('error', 'Unknown error')}")

                else:
                    # Use legacy system
                    self.log_message("✓ Using Legacy AI System")

                    if not VISION_AVAILABLE:
                        self.log_message("⚠️ Google Vision library not available")
                        return 1, extracted_count

                    self.log_message(f"Analyzing {extracted_count} frames for {video_path.name}...")

                    # Get API keys and training examples
                    roboflow_key = self.training_manager.get_roboflow_api_key()
                    roboflow_model = self.training_manager.get_roboflow_model_id()
                    google_key = self.training_manager.get_api_key()
                    training_examples = self.training_manager.get_training_examples(max_per_category=3)

                    if training_examples:
                        self.log_message(f"Using {len(training_examples)} training examples (3 per category for speed)")
                        for ex in training_examples:
                            self.log_message(f"  - {ex['label']}: {Path(ex['image_path']).name}")

                    # Initialize tagger — Roboflow takes priority
                    vision_tagger = VisionTagger(
                        credentials_path=self.vision_credentials.get() or None,
                        api_key=google_key,
                        training_examples=training_examples,
                        roboflow_api_key=roboflow_key,
                        roboflow_model_id=roboflow_model,
                    )

                    if vision_tagger.roboflow_tagger and vision_tagger.roboflow_tagger.available:
                        self.log_message(f"✓ Using Roboflow ({roboflow_model}) for AI tagging")
                    elif vision_tagger.langchain_tagger:
                        self.log_message("✓ Using LangChain + Gemini for AI tagging")
                    elif vision_tagger.mock_mode:
                        self.log_message("⚠️ Vision tagger in mock mode — check credentials")
                    else:
                        self.log_message("✓ Using legacy Google Vision API")

                    # Get all extracted images
                    image_files = list(clip_stills_folder.glob(f"{base_name}_*.{image_format}"))
                    self.log_message(f"Found {len(image_files)} images to analyze")

                    # Analyze each image
                    analysis_results = []
                    for img_path in image_files:
                        if self.stop_flag.is_set():
                            break
                        self.log_message(f"  Analyzing {img_path.name}...")
                        result = vision_tagger.analyze_image(img_path)
                        analysis_results.append(result)

                    # Save analysis to XML
                    if analysis_results:
                        xml_path = clip_stills_folder / f"{base_name}_tags.xml"
                        vision_tagger.create_xml_tags(analysis_results, xml_path)
                        self.log_message(f"✅ Saved AI analysis to {xml_path.name}")
                    else:
                        self.log_message("❌ No analysis results to save")

            except Exception as e:
                self.log_message(f"❌ AI tagging error for {video_path.name}: {str(e)}")
                import traceback
                self.log_message(f"Full error: {traceback.format_exc()}")

        # Step 3: Metadata Embedding (if enabled and XML exists)
        if self.embed_metadata.get():
            xml_path = clip_stills_folder / f"{base_name}_tags.xml"
            if xml_path.exists():
                self.log_message(f"Embedding metadata from {xml_path.name}...")
                
                try:
                    from exif_embedder import ExifEmbedder
                    embedder = ExifEmbedder()
                    metadata = embedder.parse_xml_tags(xml_path)
                    
                    # Show what we're embedding
                    keywords = metadata.get('keywords', [])[:5]
                    self.log_message(f"  Keywords: {', '.join(keywords)}")
                    
                    # Embed into original video
                    success = embedder.embed_metadata(video_path, metadata)
                    if success:
                        self.log_message(f"✅ Metadata embedded into {video_path.name}")
                    else:
                        self.log_message(f"❌ Failed to embed metadata into {video_path.name}")
                        
                except Exception as e:
                    self.log_message(f"❌ Embedding error: {str(e)}")
            else:
                self.log_message(f"⚠️ No XML file found for embedding: {xml_path}")

        return 1, extracted_count

    def export_stills(self):
        """Main export function with parallel processing"""
        source = self.source_folder.get().strip()
        output = self.output_folder.get().strip()
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
        self.log_message(f"Output format: {img_format}")
        self.log_message(f"Using {max_workers} parallel workers")
        self.log_message("Frame count will be calculated automatically based on video duration")
        
        # Debug AI settings
        self.log_message(f"AI Tagging checkbox: {self.enable_ai_tagging.get()}")
        self.log_message(f"Credentials path: {self.vision_credentials.get()}")
        
        if self.enable_ai_tagging.get():
            self.log_message("✅ AI tagging ENABLED")
        else:
            self.log_message("❌ AI tagging DISABLED")
            
        if self.embed_metadata.get():
            self.log_message("Metadata embedding enabled")
        
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
                    self.process_single_video_with_ai,
                    video_path, output, img_format
                ): video_path
                for video_path in video_files
            }

            # Collect results
            for future in as_completed(future_to_video):
                if self.stop_flag.is_set():
                    break

                video_path = future_to_video[future]
                try:
                    processed_count, frames_count = future.result()
                    total_processed += processed_count
                    total_frames += frames_count

                    progress = (total_processed / len(video_files)) * 100
                    self.update_progress(progress)

                except Exception as e:
                    self.log_message(f"Error processing {video_path.name}: {str(e)}")

        # Final summary
        if not self.stop_flag.is_set():
            self.log_message(f"\n✅ Export completed!")
            self.log_message(f"Processed: {total_processed}/{len(video_files)} videos")
            self.log_message(f"Total frames extracted: {total_frames}")
            messagebox.showinfo("Success", f"Export completed!\n{total_processed} videos processed\n{total_frames} frames extracted")
        else:
            self.log_message("Export stopped by user")

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
        """Save current settings to file"""
        try:
            settings = {
                'source_folder': self.source_folder.get(),
                'output_folder': self.output_folder.get(),
                'image_format': self.image_format.get(),
                'max_workers': self.max_workers.get(),
                'enable_ai_tagging': self.enable_ai_tagging.get(),
                'embed_metadata': self.embed_metadata.get(),
                'vision_credentials': self.vision_credentials.get()
            }
            
            with open(self.settings_file, 'w') as f:
                json.dump(settings, f, indent=2)
        except Exception:
            pass  # Ignore save errors

    def load_settings(self):
        """Load settings from file"""
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r') as f:
                    settings = json.load(f)
                    
                    self.source_folder.set(settings.get('source_folder', ''))
                    self.output_folder.set(settings.get('output_folder', ''))
                    self.image_format.set(settings.get('image_format', 'png'))
                    self.max_workers.set(settings.get('max_workers', min(4, os.cpu_count() or 1)))
                    self.enable_ai_tagging.set(settings.get('enable_ai_tagging', False))
                    self.embed_metadata.set(settings.get('embed_metadata', False))
                    self.vision_credentials.set(settings.get('vision_credentials', ''))
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
