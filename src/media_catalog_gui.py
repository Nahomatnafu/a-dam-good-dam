import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
from pathlib import Path
import sys
sys.path.append('.')
from src.database import CatalogDatabase
from src.file_scanner import FileScanner

class MediaCatalogGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Media Catalog - NeoFinder Alternative")
        self.root.geometry("1200x800")
        
        # Initialize backend components
        self.current_catalog = None
        self.scanner = FileScanner()
        
        self.setup_menu_bar()
        self.setup_toolbar()
        self.setup_three_panel_layout()
        self.setup_status_bar()

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
        
        # Create three-panel layout
        main_paned = ttk.PanedWindow(main_frame, orient=tk.HORIZONTAL)
        main_paned.pack(fill=tk.BOTH, expand=True)
        
        # LEFT PANEL: Library/Catalogs
        self.setup_library_panel(main_paned)
        
        # MIDDLE PANEL: File list
        self.setup_file_list_panel(main_paned)
        
        # RIGHT PANEL: Preview/Info
        self.setup_info_panel(main_paned)

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
        
    def setup_file_list_panel(self, parent):
        # Middle panel for file list
        middle_frame = ttk.Frame(parent)
        parent.add(middle_frame, weight=3)
        
        # File list header with view options
        header_frame = ttk.Frame(middle_frame)
        header_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(header_frame, text="Files", font=("Arial", 12, "bold")).pack(side=tk.LEFT)
        
        # View mode buttons
        view_frame = ttk.Frame(header_frame)
        view_frame.pack(side=tk.RIGHT)
        ttk.Button(view_frame, text="List", width=6).pack(side=tk.LEFT, padx=2)
        ttk.Button(view_frame, text="Grid", width=6).pack(side=tk.LEFT, padx=2)
        
        # File list
        columns = ('filename', 'size', 'type', 'keywords')
        self.file_tree = ttk.Treeview(middle_frame, columns=columns, show='tree headings')
        
        # Configure columns
        self.file_tree.heading('#0', text='Name')
        self.file_tree.heading('filename', text='Filename')
        self.file_tree.heading('size', text='Size')
        self.file_tree.heading('type', text='Type')
        self.file_tree.heading('keywords', text='Keywords')
        
        # Column widths
        self.file_tree.column('#0', width=200)
        self.file_tree.column('filename', width=150)
        self.file_tree.column('size', width=80)
        self.file_tree.column('type', width=80)
        self.file_tree.column('keywords', width=200)
        
        # Scrollbar for file list
        file_scrollbar = ttk.Scrollbar(middle_frame, orient=tk.VERTICAL, command=self.file_tree.yview)
        self.file_tree.configure(yscrollcommand=file_scrollbar.set)
        
        # Pack file list
        self.file_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        file_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def setup_info_panel(self, parent):
        # Right panel for preview/info
        right_frame = ttk.Frame(parent)
        parent.add(right_frame, weight=1)
        
        # Info header
        ttk.Label(right_frame, text="File Info", font=("Arial", 12, "bold")).pack(pady=5)
        
        # Preview area (placeholder)
        preview_frame = ttk.LabelFrame(right_frame, text="Preview")
        preview_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Use regular tk.Label for background and height options
        tk.Label(preview_frame, text="Thumbnail\n(Coming Soon)", 
                 background="lightgray", width=20, height=8).pack(pady=10)
        
        # Metadata area
        info_frame = ttk.LabelFrame(right_frame, text="Metadata")
        info_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Metadata text widget
        self.info_text = tk.Text(info_frame, wrap=tk.WORD, height=10)
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
            
            # Add to library tree
            self.catalog_tree.insert('', 'end', text=f"📊 {catalog_name}", values=[str(catalog_path)])
        
    def open_catalog(self):
        file_path = filedialog.askopenfilename(
            title="Open Catalog",
            filetypes=[("Database files", "*.db"), ("All files", "*.*")]
        )
        if file_path:
            self.current_catalog = CatalogDatabase(Path(file_path))
            catalog_name = Path(file_path).stem
            self.status_bar.config(text=f"Catalog opened: {catalog_name}")
            
            # Load files into file list
            self.load_catalog_files()
        
    def add_folder_to_catalog(self):
        if not self.current_catalog:
            messagebox.showwarning("Warning", "Please create or open a catalog first")
            return
            
        folder_path = filedialog.askdirectory(title="Select Folder to Add to Catalog")
        if folder_path:
            self.scan_and_add_folder(Path(folder_path))
    
    def scan_and_add_folder(self, folder_path):
        try:
            self.status_bar.config(text=f"Scanning {folder_path}...")
            self.root.update()
            
            # Scan folder
            files = self.scanner.scan_directory(folder_path)
            
            # Add to catalog
            for file_info in files:
                file_id = self.current_catalog.add_file(file_info)
                
            self.status_bar.config(text=f"Added {len(files)} files from {folder_path.name}")
            
            # Refresh file list
            self.load_catalog_files()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to scan folder: {str(e)}")
            self.status_bar.config(text="Ready")
    
    def load_catalog_files(self):
        # Clear existing items
        for item in self.file_tree.get_children():
            self.file_tree.delete(item)
        
        if not self.current_catalog:
            return
            
        # Load files from catalog
        files = self.current_catalog.get_all_files()
        
        for file_info in files:
            # Insert file into tree
            self.file_tree.insert('', 'end', 
                                text=file_info['filename'],
                                values=(
                                    file_info['filename'],
                                    f"{file_info.get('size_mb', 0):.1f} MB",
                                    file_info.get('file_type', 'unknown'),
                                    ', '.join(file_info.get('keywords', [])[:3])  # First 3 keywords
                                ))

def main():
    root = tk.Tk()
    app = MediaCatalogGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()





