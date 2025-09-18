import tkinter as tk
from tkinter import ttk, filedialog, messagebox

class MediaCatalogGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Media Catalog - NeoFinder Alternative")
        self.root.geometry("1000x700")
        
        self.setup_menu_bar()
        self.setup_toolbar()
        self.setup_main_layout()
        self.setup_status_bar()

    def setup_menu_bar(self):
        # File, Edit, View, Tools, Help menus
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New Catalog...", command=self.new_catalog)
        file_menu.add_command(label="Open Catalog...", command=self.open_catalog)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
    def setup_toolbar(self):
        # Quick action buttons
        toolbar = ttk.Frame(self.root)
        toolbar.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        
        ttk.Button(toolbar, text="New Catalog", command=self.new_catalog).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar, text="Open Catalog", command=self.open_catalog).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar, text="Scan Folder", command=self.scan_folder).pack(side=tk.LEFT, padx=5)
        
    def setup_main_layout(self):
        # Split panes for file list and preview
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # For now, just a simple label
        ttk.Label(main_frame, text="Media Catalog GUI - Ready to build!", 
                 font=("Arial", 16)).pack(expand=True)
        
    def setup_status_bar(self):
        self.status_bar = ttk.Label(self.root, text="Ready | No catalog loaded", 
                                   relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def new_catalog(self):
        messagebox.showinfo("New Catalog", "New catalog functionality coming soon!")
        
    def open_catalog(self):
        messagebox.showinfo("Open Catalog", "Open catalog functionality coming soon!")
        
    def scan_folder(self):
        messagebox.showinfo("Scan Folder", "Scan folder functionality coming soon!")

def main():
    root = tk.Tk()
    app = MediaCatalogGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
