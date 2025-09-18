import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
from pathlib import Path
import sys
import json
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
        self.setup_three_panel_layout()
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
        file_menu.add_command(label="Exit", command=self.root.quit)
        
    def setup_toolbar(self):
        toolbar = ttk.Frame(self.root)
        toolbar.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        
        ttk.Button(toolbar, text="New Catalog", command=self.new_catalog).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar, text="Open Catalog", command=self.open_catalog).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar, text="Add Folder", command=self.add_folder_to_catalog).pack(side=tk.LEFT, padx=5)
        
    def setup_three_panel_layout(self):
        # Main container
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create three-panel layout with resizable panes
        main_paned = ttk.PanedWindow(main_frame, orient=tk.HORIZONTAL)
        main_paned.pack(fill=tk.BOTH, expand=True)
        
        # LEFT PANEL: Library/Catalogs (weight=1, min width)
        self.setup_library_panel(main_paned)
        
        # MIDDLE PANEL: File list (weight=2, larger default)
        self.setup_files_panel(main_paned)
        
        # RIGHT PANEL: Preview/Info (weight=1, resizable)
        self.setup_info_panel(main_paned)
        
        # Set initial pane sizes (optional - user can resize)
        self.root.after(100, lambda: main_paned.sashpos(0, 250))  # Left panel width
        self.root.after(100, lambda: main_paned.sashpos(1, 700))  # Middle panel width

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
        
        # View toggle buttons
        view_frame = ttk.Frame(files_header)
        view_frame.pack(side=tk.RIGHT)
        ttk.Button(view_frame, text="List", width=8).pack(side=tk.LEFT, padx=2)
        ttk.Button(view_frame, text="Grid", width=8).pack(side=tk.LEFT)
        
        # File tree
        columns = ('Name', 'Size', 'Type', 'Keywords')
        self.file_tree = ttk.Treeview(middle_frame, columns=columns, show='tree headings')
        
        # Configure columns
        self.file_tree.heading('#0', text='Name')
        self.file_tree.heading('Name', text='Filename')
        self.file_tree.heading('Size', text='Size')
        self.file_tree.heading('Type', text='Type')
        self.file_tree.heading('Keywords', text='Keywords')
        
        # Column widths
        self.file_tree.column('#0', width=200)
        self.file_tree.column('Name', width=200)
        self.file_tree.column('Size', width=80)
        self.file_tree.column('Type', width=80)
        self.file_tree.column('Keywords', width=200)
        
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
        
        # Thumbnail label - larger and expandable
        self.thumbnail_label = tk.Label(preview_frame, text="Select a video\nto see thumbnail", 
                                       background="lightgray", width=25, height=15)
        self.thumbnail_label.pack(pady=10, fill=tk.BOTH, expand=True)
        
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

    def load_catalog_files(self):
        # Clear existing items
        for item in self.file_tree.get_children():
            self.file_tree.delete(item)
        
        if not self.current_catalog:
            return
        
        try:
            # Use search_files with empty query to get all files
            files = self.current_catalog.search_files("")
            
            if not files:  # Handle empty list, not None
                print("No files found in catalog")
                self.status_bar.config(text="No files found in catalog")
                return
            
            print(f"Found {len(files)} files in catalog")
            
            for file_info in files:
                # Handle the case where keywords might be a string, not a list
                keywords = file_info.get('keywords', '')
                if isinstance(keywords, str):
                    keywords_display = keywords[:50] + "..." if len(keywords) > 50 else keywords
                else:
                    keywords_display = ', '.join(keywords[:3]) if keywords else ''
                
                # Calculate size in MB
                filesize = file_info.get('filesize') or file_info.get('file_size', 0)
                size_mb = filesize / (1024 * 1024) if filesize else 0
                
                # Insert file into tree
                self.file_tree.insert('', 'end', 
                                    text=file_info['filename'],
                                    values=(
                                        file_info['filename'],
                                        f"{size_mb:.1f} MB",
                                        file_info.get('file_type', 'unknown'),
                                        keywords_display
                                    ))
                                    
            self.status_bar.config(text=f"Loaded {len(files)} files")
            
        except Exception as e:
            print(f"Error loading files: {e}")
            import traceback
            traceback.print_exc()
            self.status_bar.config(text=f"Error loading files: {str(e)}")

    def on_file_select(self, event):
        """Handle file selection in the tree"""
        selection = self.file_tree.selection()
        if not selection:
            return
        
        item = self.file_tree.item(selection[0])
        filename = item['text']
        
        # Update info panel
        self.info_text.delete(1.0, tk.END)
        self.info_text.insert(tk.END, f"Selected: {filename}\n\n")
        self.info_text.insert(tk.END, "File Details:\n")
        self.info_text.insert(tk.END, f"Name: {item['values'][0]}\n")
        self.info_text.insert(tk.END, f"Size: {item['values'][1]}\n")
        self.info_text.insert(tk.END, f"Type: {item['values'][2]}\n")
        self.info_text.insert(tk.END, f"Keywords: {item['values'][3]}\n")
        
        # Generate thumbnail for video files
        if self.current_catalog and item['values'][2] == 'video':
            files = self.current_catalog.search_files("")
            selected_file = None
            for file_info in files:
                if file_info['filename'] == filename:
                    selected_file = file_info
                    break
            
            if selected_file:
                self.generate_and_show_thumbnail(selected_file['filepath'])
        else:
            self.thumbnail_label.config(text="Select a video\nto see thumbnail", image="")

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
            
            self.status_bar.config(text=f"Found {len(files)} files")
            
        except Exception as e:
            print(f"Search error: {e}")

    def load_catalog_structure(self):
        """Load catalog structure with folders"""
        # Clear existing items
        for item in self.catalog_tree.get_children():
            self.catalog_tree.delete(item)
        
        if not self.current_catalog:
            root_item = self.catalog_tree.insert('', 'end', text='📁 My Catalogs', open=True)
            return
        
        # Add current catalog
        catalog_name = self.current_catalog.catalog_path.stem
        catalog_item = self.catalog_tree.insert('', 'end', text=f'📊 {catalog_name}', open=True)
        
        # Get all files and organize by folder
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
            
            # Add folders to tree
            for folder_name, folder_files in folders.items():
                folder_item = self.catalog_tree.insert(catalog_item, 'end', 
                                                     text=f'📁 {folder_name} ({len(folder_files)})',
                                                     values=(folder_name,))
            
        except Exception as e:
            print(f"Error loading catalog structure: {e}")

    def on_catalog_select(self, event):
        """Handle catalog/folder selection"""
        selection = self.catalog_tree.selection()
        if not selection:
            return
        
        item = self.catalog_tree.item(selection[0])
        text = item['text']
        values = item.get('values', [])
        
        if values and len(values) > 0:
            # This is a folder selection
            folder_name = values[0]
            self.filter_by_folder(folder_name)
        else:
            # This is catalog selection
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





