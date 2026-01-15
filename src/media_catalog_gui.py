import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
from pathlib import Path
import sys
import json
import subprocess
import threading
import xml.etree.ElementTree as ET
sys.path.append('.')
from src.database import CatalogDatabase
from src.file_scanner import FileScanner
from src.thumbnail_generator import ThumbnailGenerator

class MediaCatalogGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Media Catalog - NeoFinder Alternative")
        self.root.geometry("1200x800")
        
        # Initialize backend components
        self.current_catalog = None
        self.scanner = FileScanner()
        self.thumbnail_generator = ThumbnailGenerator()
        self.config_file = Path("config.json")
        
        self.setup_menu_bar()
        self.setup_toolbar()
        self.setup_three_panel_layout()  # This line is crucial!
        self.setup_status_bar()
        
        # Load previous session
        self.load_session()

    def setup_menu_bar(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New Catalog...", command=self.new_catalog)
        file_menu.add_command(label="Open Catalog...", command=self.open_catalog)
        file_menu.add_command(label="Add Folder to Catalog...", command=self.add_folder_to_catalog)
        file_menu.add_separator()
        file_menu.add_command(label="Refresh Catalog", command=self.refresh_catalog)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)

        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="AI Stills Exporter...", command=self.open_stills_exporter)
        
    def setup_toolbar(self):
        toolbar = ttk.Frame(self.root)
        toolbar.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)

        # Left side - Catalog operations
        ttk.Button(toolbar, text="New Catalog", command=self.new_catalog).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar, text="Open Catalog", command=self.open_catalog).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar, text="Add Folder", command=self.add_folder_to_catalog).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar, text="🔄 Refresh", command=self.refresh_catalog).pack(side=tk.LEFT, padx=5)

        # Separator
        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=10)

        # Right side - AI Tools
        ttk.Button(toolbar, text="🎬 AI Stills Exporter",
                  command=self.open_stills_exporter,
                  style="Accent.TButton").pack(side=tk.LEFT, padx=5)
        
    def setup_three_panel_layout(self):
        # Main container
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create three-panel layout with resizable panes
        main_paned = ttk.PanedWindow(main_frame, orient=tk.HORIZONTAL)
        main_paned.pack(fill=tk.BOTH, expand=True)
        
        # Store reference to main_paned for later use
        self.main_paned = main_paned
        
        # LEFT PANEL: Library/Catalogs (weight=1, min width)
        self.setup_library_panel(main_paned)
        
        # MIDDLE PANEL: File list (weight=2, larger default)
        self.setup_files_panel(main_paned)
        
        # RIGHT PANEL: Preview/Info (weight=1, resizable)
        self.setup_info_panel(main_paned)
        
        # Set initial pane sizes with longer delay and error handling
        self.root.after(200, self.set_initial_pane_sizes)
        
    def set_initial_pane_sizes(self):
        """Set initial pane sizes with error handling"""
        try:
            if hasattr(self, 'main_paned'):
                # Force update to ensure widgets are rendered
                self.root.update_idletasks()
                
                # Set pane positions
                self.main_paned.sashpos(0, 250)  # Left panel width
                self.main_paned.sashpos(1, 700)  # Middle panel width
                
                # Schedule another update to ensure it sticks
                self.root.after(100, lambda: self.main_paned.sashpos(0, 250))
                self.root.after(100, lambda: self.main_paned.sashpos(1, 700))
        except Exception as e:
            print(f"Error setting pane sizes: {e}")

    def setup_library_panel(self, parent):
        # Left panel for catalogs/library
        left_frame = ttk.Frame(parent)
        parent.add(left_frame, weight=1)
        
        # Library header
        ttk.Label(left_frame, text="Library", font=("Arial", 12, "bold")).pack(pady=5)
        
        # Catalogs tree
        self.catalog_tree = ttk.Treeview(left_frame, show='tree')
        self.catalog_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Add sample catalog entries
        self.catalog_tree.insert('', 'end', text='📁 My Catalogs', open=True)
        
        # Bind catalog selection
        self.catalog_tree.bind('<<TreeviewSelect>>', self.on_catalog_select)

    def setup_files_panel(self, parent):
        # Middle panel for file list
        middle_frame = ttk.Frame(parent)
        parent.add(middle_frame, weight=2)

        # Files header with view options
        files_header = ttk.Frame(middle_frame)
        files_header.pack(fill=tk.X, pady=5)

        ttk.Label(files_header, text="Files", font=("Arial", 12, "bold")).pack(side=tk.LEFT)

        # File type filter
        filter_frame = ttk.Frame(files_header)
        filter_frame.pack(side=tk.RIGHT)
        ttk.Label(filter_frame, text="Show:").pack(side=tk.LEFT, padx=5)
        self.file_type_filter = tk.StringVar(value="all")
        ttk.Radiobutton(filter_frame, text="All", variable=self.file_type_filter,
                       value="all", command=self.apply_file_type_filter).pack(side=tk.LEFT)
        ttk.Radiobutton(filter_frame, text="Videos", variable=self.file_type_filter,
                       value="video", command=self.apply_file_type_filter).pack(side=tk.LEFT)
        ttk.Radiobutton(filter_frame, text="Images", variable=self.file_type_filter,
                       value="image", command=self.apply_file_type_filter).pack(side=tk.LEFT)
        
        # File tree - removed Keywords column
        columns = ('Name', 'Size', 'Type')
        self.file_tree = ttk.Treeview(middle_frame, columns=columns, show='tree headings')
        
        # Configure columns
        self.file_tree.heading('#0', text='Name')
        self.file_tree.heading('Name', text='Filename')
        self.file_tree.heading('Size', text='Size')
        self.file_tree.heading('Type', text='Type')
        
        # Column widths - redistributed space
        self.file_tree.column('#0', width=250)
        self.file_tree.column('Name', width=250)
        self.file_tree.column('Size', width=100)
        self.file_tree.column('Type', width=100)
        
        # Bind selection event
        self.file_tree.bind('<<TreeviewSelect>>', self.on_file_select)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(middle_frame, orient=tk.VERTICAL, command=self.file_tree.yview)
        self.file_tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack tree and scrollbar
        self.file_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def setup_info_panel(self, parent):
        # Right panel for preview/info
        right_frame = ttk.Frame(parent)
        parent.add(right_frame, weight=1)
        
        # Info header
        ttk.Label(right_frame, text="File Info", font=("Arial", 12, "bold")).pack(pady=5)
        
        # Preview area - make it expandable
        preview_frame = ttk.LabelFrame(right_frame, text="Preview")
        preview_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Video controls
        controls_frame = ttk.Frame(preview_frame)
        controls_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.play_button = ttk.Button(controls_frame, text="▶ Play", command=self.play_video)
        self.play_button.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(controls_frame, text="📁 Show in Explorer", command=self.show_in_explorer).pack(side=tk.LEFT, padx=5)
        
        # Thumbnail label - larger and expandable
        self.thumbnail_label = tk.Label(preview_frame, text="Select a video\nto see thumbnail", 
                                       background="lightgray", width=25, height=15)
        self.thumbnail_label.pack(pady=10, fill=tk.BOTH, expand=True)
        
        # Current video path for playback
        self.current_video_path = None
        
        # Metadata area - smaller, fixed size
        info_frame = ttk.LabelFrame(right_frame, text="Metadata")
        info_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Metadata text widget - smaller height
        self.info_text = tk.Text(info_frame, wrap=tk.WORD, height=8)
        info_scrollbar = ttk.Scrollbar(info_frame, orient=tk.VERTICAL, command=self.info_text.yview)
        self.info_text.configure(yscrollcommand=info_scrollbar.set)
        
        self.info_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        info_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def setup_status_bar(self):
        self.status_bar = ttk.Label(self.root, text="Ready | No catalog loaded", 
                                   relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def new_catalog(self):
        # Dialog to create new catalog
        catalog_name = tk.simpledialog.askstring("New Catalog", "Enter catalog name:")
        if catalog_name:
            catalog_path = Path("catalogs") / f"{catalog_name}.db"
            catalog_path.parent.mkdir(exist_ok=True)
            
            self.current_catalog = CatalogDatabase(catalog_path)
            self.status_bar.config(text=f"Catalog created: {catalog_name}")
            self.save_session()  # Save the new catalog
            
            # Add to library tree
            self.catalog_tree.insert('', 'end', text=f"📊 {catalog_name}", values=[str(catalog_path)])

    def open_catalog(self):
        filename = filedialog.askopenfilename(
            title="Open Catalog",
            initialdir="catalogs",
            filetypes=[("Database files", "*.db"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                self.current_catalog = CatalogDatabase(Path(filename))
                catalog_name = Path(filename).stem
                self.status_bar.config(text=f"Opened catalog: {catalog_name}")
                self.load_catalog_files()
                self.load_catalog_structure()
                self.save_session()  # Save the opened catalog
            except Exception as e:
                messagebox.showerror("Error", f"Failed to open catalog: {str(e)}")

    def add_folder_to_catalog(self):
        if not self.current_catalog:
            messagebox.showwarning("Warning", "Please create or open a catalog first")
            return
            
        folder_path = filedialog.askdirectory(title="Select Folder to Add to Catalog")
        if folder_path:
            self.scan_and_add_folder(Path(folder_path))
    
    def scan_and_add_folder(self, folder_path):
        try:
            # Create progress window
            progress_window = tk.Toplevel(self.root)
            progress_window.title("Scanning Folder")
            progress_window.geometry("400x100")
            progress_window.transient(self.root)
            progress_window.grab_set()
            
            tk.Label(progress_window, text=f"Scanning: {folder_path.name}").pack(pady=10)
            progress_bar = ttk.Progressbar(progress_window, mode='indeterminate')
            progress_bar.pack(fill=tk.X, padx=20, pady=10)
            progress_bar.start()
            
            self.root.update()
            
            # Scan folder
            files = self.scanner.scan_directory(folder_path)
            print(f"Found {len(files)} files to add")
            
            # Stop progress and switch to determinate mode
            progress_bar.stop()
            progress_bar.config(mode='determinate', maximum=len(files))
            
            # Add to catalog
            added_count = 0
            for i, file_info in enumerate(files):
                try:
                    file_id = self.current_catalog.add_file(file_info)
                    
                    # Add keywords based on folder structure and filename
                    keywords = self.generate_keywords(file_info)
                    if keywords:
                        self.current_catalog.add_keywords_to_file(file_id, keywords, source='auto')
                    
                    added_count += 1
                    progress_bar['value'] = i + 1
                    self.root.update()
                except Exception as e:
                    print(f"Error adding file {file_info['filename']}: {e}")
            
            progress_window.destroy()
            self.status_bar.config(text=f"Added {added_count} files from {folder_path.name}")
            self.load_catalog_files()
            self.load_catalog_structure()  # Refresh folder structure
            
        except Exception as e:
            if 'progress_window' in locals():
                progress_window.destroy()
            print(f"Scan error: {e}")
            messagebox.showerror("Error", f"Failed to scan folder: {str(e)}")
            self.status_bar.config(text="Ready")

    def generate_keywords(self, file_info):
        """Generate keywords based on file path and name"""
        keywords = []
        
        # Add folder name as keyword
        filepath = Path(file_info['filepath'])
        folder_name = filepath.parent.name.lower()
        
        # Map folder names to keywords
        folder_keywords = {
            'soccer': ['soccer', 'sports', 'ball', 'field'],
            'basketball': ['basketball', 'sports', 'court', 'ball'],
            'stock': ['stock', 'footage', 'generic'],
            'fridaytest': ['test', 'friday', 'sample']
        }
        
        if folder_name in folder_keywords:
            keywords.extend(folder_keywords[folder_name])
        else:
            keywords.append(folder_name)
        
        # Add file type
        keywords.append(file_info.get('file_type', 'video'))
        
        # Add filename-based keywords
        filename_lower = file_info['filename'].lower()
        if 'clip' in filename_lower:
            keywords.append('clip')
        if any(num in filename_lower for num in ['1', '2', '3']):
            keywords.append('numbered')
        
        return list(set(keywords))  # Remove duplicates

    def apply_file_type_filter(self):
        """Apply file type filter to the displayed files"""
        self.load_catalog_files()

    def load_catalog_files(self):
        # Clear existing items
        for item in self.file_tree.get_children():
            self.file_tree.delete(item)

        if not self.current_catalog:
            return

        try:
            files = self.current_catalog.search_files("")

            if not files:
                print("No files found in catalog")
                self.status_bar.config(text="No files found in catalog")
                return

            print(f"Found {len(files)} files in catalog")

            # Apply file type filter
            filter_type = self.file_type_filter.get() if hasattr(self, 'file_type_filter') else "all"
            filtered_files = []

            for file_info in files:
                file_type = file_info.get('file_type', 'unknown')
                if filter_type == "all" or file_type == filter_type:
                    filtered_files.append(file_info)

            # Display filtered files
            for file_info in filtered_files:
                # Calculate size in MB
                filesize = file_info.get('filesize') or file_info.get('file_size', 0)
                size_mb = filesize / (1024 * 1024) if filesize else 0

                # Insert file into tree
                self.file_tree.insert('', 'end',
                                    text=file_info['filename'],
                                    values=(
                                        file_info['filename'],
                                        f"{size_mb:.1f} MB",
                                        file_info.get('file_type', 'unknown')
                                    ))

            # Update status with filter info
            if filter_type == "all":
                self.status_bar.config(text=f"Loaded {len(filtered_files)} files")
            else:
                self.status_bar.config(text=f"Showing {len(filtered_files)} {filter_type} files (of {len(files)} total)")
            
        except Exception as e:
            print(f"Error loading files: {e}")
            import traceback
            traceback.print_exc()
            self.status_bar.config(text=f"Error loading files: {str(e)}")

    def get_ai_tags_from_xml(self, video_path: Path) -> list:
        """Check for AI-generated tags XML file and extract tags"""
        try:
            # Look for XML file in the same directory or in a _stills folder
            video_stem = video_path.stem

            # Try multiple variations of the filename
            # 1. Original with spaces and apostrophes
            # 2. Spaces to underscores, keep apostrophes
            # 3. Spaces to underscores, remove apostrophes but keep the 's'
            # 4. Spaces to underscores, remove apostrophes completely
            variations = [
                video_stem,  # Original
                video_stem.replace(" ", "_"),  # Spaces to underscores
                video_stem.replace(" ", "_").replace("'s", "s"),  # 's -> s
                video_stem.replace(" ", "_").replace("'", ""),  # Remove apostrophes
            ]

            possible_xml_paths = []
            for variant in variations:
                possible_xml_paths.extend([
                    video_path.parent / f"{variant}_tags.xml",
                    video_path.parent / f"{variant}_stills" / f"{variant}_tags.xml",
                    video_path.parent / f"{variant}_Stills" / f"{variant}_tags.xml",
                ])

            # Remove duplicates while preserving order
            seen = set()
            unique_paths = []
            for path in possible_xml_paths:
                if path not in seen:
                    seen.add(path)
                    unique_paths.append(path)

            for xml_path in unique_paths:
                if xml_path.exists():
                    tree = ET.parse(xml_path)
                    root = tree.getroot()

                    # Handle new XML format (video_analysis with final_tags)
                    final_tags = root.find('final_tags')
                    if final_tags is not None:
                        all_tags = []

                        # Add regular tags (remove confidence scores from display)
                        for tag in final_tags.findall('tag'):
                            if tag.text:
                                all_tags.append(tag.text.strip())

                        # Add gallery matches (only high-confidence building matches)
                        gallery_matches = root.find('gallery_matches')
                        if gallery_matches is not None:
                            building_confidence_threshold = 0.65  # Only show buildings with >65% confidence
                            seen_buildings = set()  # Avoid duplicate building names

                            for match in gallery_matches.findall('match'):
                                category = match.get('category', '')
                                confidence = float(match.get('confidence', '0'))

                                if category and confidence >= building_confidence_threshold:
                                    if category not in seen_buildings:
                                        all_tags.append(f"🏛️ {category}")
                                        seen_buildings.add(category)

                        return all_tags

                    # Fallback: Handle old XML format
                    all_tags = set()
                    for frame in root.findall('Frame'):
                        labels = frame.find('Labels')
                        if labels is not None:
                            for label in labels.findall('Label'):
                                if label.text:
                                    all_tags.add(label.text.strip())

                    return sorted(list(all_tags))

            return []
        except Exception as e:
            print(f"Error reading AI tags: {e}")
            return []

    def on_file_select(self, event):
        """Handle file selection in the tree"""
        selection = self.file_tree.selection()
        if not selection:
            return

        item = self.file_tree.item(selection[0])
        filename = item['text']

        # Get full file info from database to show real embedded keywords
        keywords_text = "No embedded keywords"
        ai_tags_text = "No AI tags found"

        if self.current_catalog:
            files = self.current_catalog.search_files("")
            selected_file = None
            for file_info in files:
                if file_info['filename'] == filename:
                    selected_file = file_info
                    break

            if selected_file:
                # Get real embedded keywords from database
                keywords = selected_file.get('keywords', [])
                if keywords:
                    if isinstance(keywords, str) and keywords.strip():
                        keywords_text = keywords
                    elif isinstance(keywords, list) and keywords:
                        keywords_text = ', '.join(keywords)

                # Check for AI-generated tags from XML
                video_path = Path(selected_file['filepath'])
                ai_tags = self.get_ai_tags_from_xml(video_path)
                if ai_tags:
                    ai_tags_text = ', '.join(ai_tags[:20])  # Show first 20 tags
                    if len(ai_tags) > 20:
                        ai_tags_text += f" ... ({len(ai_tags)} total)"

                # Store current video path for playback
                self.current_video_path = selected_file['filepath']
                if selected_file.get('file_type') == 'video':
                    self.play_button.config(state='normal')
                    self.generate_and_show_thumbnail(selected_file['filepath'])
                else:
                    self.play_button.config(state='disabled')
                    self.thumbnail_label.config(text="Select a video\nto see thumbnail", image="")
            else:
                self.current_video_path = None
                self.play_button.config(state='disabled')

        # Update info panel with real embedded keywords and AI tags
        self.info_text.delete(1.0, tk.END)
        self.info_text.insert(tk.END, f"Selected: {filename}\n\n")
        self.info_text.insert(tk.END, "File Details:\n")
        self.info_text.insert(tk.END, f"Name: {item['values'][0]}\n")
        self.info_text.insert(tk.END, f"Size: {item['values'][1]}\n")
        self.info_text.insert(tk.END, f"Type: {item['values'][2]}\n\n")
        self.info_text.insert(tk.END, "Embedded Keywords:\n")
        self.info_text.insert(tk.END, f"{keywords_text}\n\n")
        self.info_text.insert(tk.END, "AI Generated Tags:\n")
        self.info_text.insert(tk.END, f"{ai_tags_text}\n")

    def generate_and_show_thumbnail(self, video_path):
        """Generate and display thumbnail for video"""
        try:
            self.thumbnail_label.config(text="Generating\nthumbnail...")
            self.root.update()
            
            thumb_path = self.thumbnail_generator.generate_thumbnail(video_path, size="320x240")
            
            if thumb_path and thumb_path.exists():
                # Load and display thumbnail
                from PIL import Image, ImageTk
                img = Image.open(thumb_path)
                
                # Scale to fit the label while maintaining aspect ratio
                label_width = self.thumbnail_label.winfo_width()
                label_height = self.thumbnail_label.winfo_height()
                
                if label_width > 1 and label_height > 1:  # Label has been rendered
                    img.thumbnail((label_width-20, label_height-20), Image.Resampling.LANCZOS)
                else:
                    img.thumbnail((300, 200), Image.Resampling.LANCZOS)  # Default size
                
                photo = ImageTk.PhotoImage(img)
                
                self.thumbnail_label.config(image=photo, text="")
                self.thumbnail_label.image = photo  # Keep reference
            else:
                self.thumbnail_label.config(text="Thumbnail\ngeneration failed", image="")
                
        except ImportError:
            # Fallback if PIL not available
            self.thumbnail_label.config(text=f"Thumbnail generated:\n{Path(video_path).name}", image="")
        except Exception as e:
            self.thumbnail_label.config(text=f"Error:\n{str(e)[:20]}...", image="")
            print(f"Thumbnail error: {e}")

    def on_search(self, event=None):
        """Handle search input"""
        if not self.current_catalog:
            return
        
        query = self.search_var.get()
        self.filter_files(query)

    def filter_files(self, query=""):
        """Filter displayed files based on search query"""
        # Clear existing items
        for item in self.file_tree.get_children():
            self.file_tree.delete(item)
        
        if not self.current_catalog:
            return
        
        try:
            files = self.current_catalog.search_files(query)
            
            for file_info in files:
                filesize = file_info.get('filesize') or file_info.get('file_size', 0)
                size_mb = filesize / (1024 * 1024) if filesize else 0
                
                # Insert file into tree - removed keywords
                self.file_tree.insert('', 'end', 
                                    text=file_info['filename'],
                                    values=(
                                        file_info['filename'],
                                        f"{size_mb:.1f} MB",
                                        file_info.get('file_type', 'unknown')
                                    ))
            
            self.status_bar.config(text=f"Found {len(files)} files")
            
        except Exception as e:
            print(f"Search error: {e}")

    def load_catalog_structure(self):
        """Load all available catalogs and current catalog structure"""
        # Clear existing items
        for item in self.catalog_tree.get_children():
            self.catalog_tree.delete(item)

        # Add root "My Catalogs" node
        root_item = self.catalog_tree.insert('', 'end', text='📁 My Catalogs', open=True)

        # Find all catalog files
        catalog_dir = Path('catalogs')
        if catalog_dir.exists():
            catalog_files = list(catalog_dir.glob('*.db'))
            catalog_files.sort(key=lambda f: f.stat().st_mtime, reverse=True)  # Most recent first

            for catalog_file in catalog_files:
                catalog_name = catalog_file.stem

                # Mark current catalog with special icon
                if self.current_catalog and catalog_file == self.current_catalog.catalog_path:
                    catalog_icon = '📊'  # Current catalog
                    catalog_text = f'{catalog_icon} {catalog_name} (current)'
                    catalog_item = self.catalog_tree.insert(root_item, 'end',
                                                          text=catalog_text,
                                                          values=('catalog', str(catalog_file)),
                                                          open=True)

                    # Add folders for current catalog
                    try:
                        files = self.current_catalog.search_files("")
                        folders = {}

                        for file_info in files:
                            filepath = Path(file_info['filepath'])
                            folder_path = filepath.parent
                            folder_name = folder_path.name

                            if folder_name not in folders:
                                folders[folder_name] = []
                            folders[folder_name].append(file_info)

                        # Add folders to current catalog
                        for folder_name, folder_files in folders.items():
                            folder_item = self.catalog_tree.insert(catalog_item, 'end',
                                                                 text=f'📁 {folder_name} ({len(folder_files)})',
                                                                 values=('folder', folder_name))

                    except Exception as e:
                        print(f"Error loading current catalog structure: {e}")
                else:
                    # Other catalogs (not currently open)
                    catalog_icon = '📄'  # Available catalog
                    catalog_text = f'{catalog_icon} {catalog_name}'
                    self.catalog_tree.insert(root_item, 'end',
                                           text=catalog_text,
                                           values=('catalog', str(catalog_file)))

        if not self.current_catalog:
            self.catalog_tree.insert(root_item, 'end',
                                   text='ℹ️ No catalog open - Create or open a catalog',
                                   values=('info', ''))

    def on_catalog_select(self, event):
        """Handle catalog/folder selection"""
        selection = self.catalog_tree.selection()
        if not selection:
            return

        item = self.catalog_tree.item(selection[0])
        text = item['text']
        values = item.get('values', [])

        if values and len(values) >= 2:
            item_type = values[0]
            item_value = values[1]

            if item_type == 'catalog':
                # Switch to a different catalog
                try:
                    catalog_path = Path(item_value)
                    if catalog_path.exists():
                        self.current_catalog = CatalogDatabase(catalog_path)
                        catalog_name = catalog_path.stem
                        self.status_bar.config(text=f"Switched to catalog: {catalog_name}")
                        self.load_catalog_files()
                        self.load_catalog_structure()  # Refresh to show current catalog
                        self.save_session()  # Save the switched catalog
                    else:
                        messagebox.showerror("Error", f"Catalog file not found: {catalog_path}")
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to open catalog: {str(e)}")

            elif item_type == 'folder':
                # Filter by folder
                folder_name = item_value
                self.filter_by_folder(folder_name)

        elif values and len(values) == 1:
            # Legacy format - folder selection
            folder_name = values[0]
            self.filter_by_folder(folder_name)
        else:
            # No values - catalog root selection
            self.load_catalog_files()

    def filter_by_folder(self, folder_name):
        """Filter files by folder"""
        # Clear existing items
        for item in self.file_tree.get_children():
            self.file_tree.delete(item)
        
        if not self.current_catalog:
            return
        
        try:
            files = self.current_catalog.search_files("")
            filtered_files = []
            
            for file_info in files:
                filepath = Path(file_info['filepath'])
                if filepath.parent.name == folder_name:
                    filtered_files.append(file_info)
            
            # Display filtered files
            for file_info in filtered_files:
                keywords = file_info.get('keywords', '')
                if isinstance(keywords, str):
                    keywords_display = keywords[:50] + "..." if len(keywords) > 50 else keywords
                else:
                    keywords_display = ', '.join(keywords[:3]) if keywords else ''
                
                filesize = file_info.get('filesize') or file_info.get('file_size', 0)
                size_mb = filesize / (1024 * 1024) if filesize else 0
                
                self.file_tree.insert('', 'end', 
                                    text=file_info['filename'],
                                    values=(
                                        file_info['filename'],
                                        f"{size_mb:.1f} MB",
                                        file_info.get('file_type', 'unknown'),
                                        keywords_display
                                    ))
            
            self.status_bar.config(text=f"Showing {len(filtered_files)} files from {folder_name}")
            
        except Exception as e:
            print(f"Error filtering by folder: {e}")

    def load_session(self):
        """Load previous session settings"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    
                last_catalog = config.get('last_catalog')
                if last_catalog and Path(last_catalog).exists():
                    self.current_catalog = CatalogDatabase(Path(last_catalog))
                    self.load_catalog_files()
                    self.load_catalog_structure()
                    catalog_name = Path(last_catalog).stem
                    self.status_bar.config(text=f"Restored catalog: {catalog_name}")
        except Exception as e:
            print(f"Error loading session: {e}")

    def save_session(self):
        """Save current session settings"""
        try:
            config = {}
            if self.current_catalog:
                config['last_catalog'] = str(self.current_catalog.catalog_path)
            
            with open(self.config_file, 'w') as f:
                json.dump(config, f)
        except Exception as e:
            print(f"Error saving session: {e}")

    def play_video(self):
        """Play the selected video in default player"""
        if not self.current_video_path:
            return
        
        video_path = Path(self.current_video_path)
        if not video_path.exists():
            messagebox.showerror("Error", f"Video file not found: {video_path}")
            return
        
        try:
            # Cross-platform video playback
            if sys.platform == "win32":
                subprocess.run(['start', str(video_path)], shell=True, check=True)
            elif sys.platform == "darwin":  # macOS
                subprocess.run(['open', str(video_path)], check=True)
            else:  # Linux
                subprocess.run(['xdg-open', str(video_path)], check=True)
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to play video: {str(e)}")

    def show_in_explorer(self):
        """Show the selected file in file explorer"""
        if not self.current_video_path:
            return
        
        video_path = Path(self.current_video_path)
        if not video_path.exists():
            messagebox.showerror("Error", f"File not found: {video_path}")
            return
        
        try:
            if sys.platform == "win32":
                # Try explorer /select first, fallback to folder open
                try:
                    subprocess.run(['explorer', '/select,', str(video_path)], check=True)
                except subprocess.CalledProcessError:
                    # Fallback: just open the folder
                    import os
                    os.startfile(str(video_path.parent))
            elif sys.platform == "darwin":  # macOS
                subprocess.run(['open', '-R', str(video_path)], check=True)
            else:  # Linux
                subprocess.run(['xdg-open', str(video_path.parent)], check=True)
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to show in explorer: {str(e)}")

    def open_stills_exporter(self):
        """Open the AI Stills Exporter in a new window"""
        try:
            # Create a new top-level window
            exporter_window = tk.Toplevel(self.root)
            exporter_window.title("AI Stills Exporter")
            exporter_window.geometry("600x500")

            # Import and initialize the Stills Exporter GUI
            try:
                from stills_exporter_gui import StillsExporterGUI
            except ImportError:
                from src.stills_exporter_gui import StillsExporterGUI

            # Create the exporter GUI in the new window
            StillsExporterGUI(exporter_window)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to open Stills Exporter: {str(e)}")

    def refresh_catalog(self):
        """Refresh catalog by re-scanning all files and updating metadata"""
        if not self.current_catalog:
            messagebox.showwarning("No Catalog", "Please open a catalog first.")
            return
        
        # Confirm with user
        result = messagebox.askyesno(
            "Refresh Catalog", 
            "This will re-scan all files and update metadata.\nThis may take a while. Continue?"
        )
        
        if not result:
            return
        
        self.status_bar.config(text="Refreshing catalog...")
        self.root.update()
        
        try:
            # Get all files from database
            all_files = self.current_catalog.search_files("")
            total_files = len(all_files)
            
            updated_count = 0
            for i, file_info in enumerate(all_files):
                filepath = Path(file_info['filepath'])
                
                # Update status
                self.status_bar.config(text=f"Refreshing {i+1}/{total_files}: {filepath.name}")
                self.root.update()
                
                if filepath.exists():
                    # Get fresh file info with real embedded metadata
                    if file_info.get('file_type') == 'video':
                        fresh_info = self.scanner.get_video_info(filepath)
                    else:
                        fresh_info = self.scanner._extract_file_info(filepath)
                    
                    if fresh_info:
                        # Update database with fresh info
                        self.current_catalog.add_file(fresh_info)
                        
                        # Update keywords if they exist
                        if fresh_info.get('keywords'):
                            file_id = self.current_catalog.get_file_id(fresh_info['filepath'])
                            if file_id:
                                # Clear old keywords and add new ones
                                self.current_catalog.clear_file_keywords(file_id)
                                self.current_catalog.add_keywords_to_file(
                                    file_id, fresh_info['keywords'], source='embedded'
                                )
                        
                        updated_count += 1
            
            # Refresh the display
            self.load_catalog_files()
            
            self.status_bar.config(text=f"Catalog refreshed! Updated {updated_count} files.")
            messagebox.showinfo("Refresh Complete", f"Successfully refreshed {updated_count} files.")
            
        except Exception as e:
            self.status_bar.config(text="Refresh failed")
            messagebox.showerror("Refresh Error", f"Error refreshing catalog: {str(e)}")

def main():
    root = tk.Tk()
    app = MediaCatalogGUI(root)
    
    # Save session on close
    def on_closing():
        app.save_session()
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()







