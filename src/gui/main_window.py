import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from database.operations import DatabaseManager

class MainWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Project Metadata Manager")
        self.root.geometry("1024x600")
        self.db_manager = DatabaseManager()

        # Initialize status bar first
        self.status_var = tk.StringVar()
        self.status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        # Then initialize the rest of the UI
        self._init_ui()

    def _init_ui(self):
        # Create main container
        self.main_container = ttk.PanedWindow(self.root, orient='horizontal')
        self.main_container.pack(fill='both', expand=True)

        self._init_file_browser()
        self._init_metadata_panel()

        # Initialize with current directory
        self.current_path = os.getcwd()
        self.populate_tree(self.current_path)

    def _init_file_browser(self):
        # Left side - File Browser
        self.left_frame = ttk.Frame(self.main_container)
        self.main_container.add(self.left_frame)

        # Button to select directory
        self.select_btn = ttk.Button(self.left_frame, text="Select Folder", 
                                   command=self.select_directory)
        self.select_btn.pack(fill='x', padx=5, pady=5)

        # Create tree view frame
        tree_frame = ttk.Frame(self.left_frame)
        tree_frame.pack(fill='both', expand=True, padx=5)

        # Create tree view with scrollbars
        self.tree = ttk.Treeview(tree_frame, columns=('Type',), height=25)
        self.tree.heading('#0', text='Name')
        self.tree.heading('Type', text='Type')
        
        # Add scrollbars
        y_scrollbar = ttk.Scrollbar(tree_frame, orient='vertical', 
                                  command=self.tree.yview)
        x_scrollbar = ttk.Scrollbar(tree_frame, orient='horizontal', 
                                  command=self.tree.xview)
        
        self.tree.configure(yscrollcommand=y_scrollbar.set, 
                          xscrollcommand=x_scrollbar.set)
        
        # Grid layout for tree and scrollbars
        self.tree.grid(row=0, column=0, sticky='nsew')
        y_scrollbar.grid(row=0, column=1, sticky='ns')
        x_scrollbar.grid(row=1, column=0, sticky='ew')
        
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)

        # Bind events
        self.tree.bind('<Double-1>', self.on_double_click)
        self.tree.bind('<<TreeviewSelect>>', self.on_select)

        # Current path label
        self.path_label = ttk.Label(self.left_frame, text="", wraplength=300)
        self.path_label.pack(fill='x', padx=5, pady=5)

    def _init_metadata_panel(self):
        # Right side - Metadata Panel
        self.right_frame = ttk.Frame(self.main_container)
        self.main_container.add(self.right_frame)

        # Metadata fields
        ttk.Label(self.right_frame, text="Metadata", 
                 font=('Arial', 12, 'bold')).pack(pady=10)
        
        # Create metadata fields
        self.metadata_fields = {}
        fields = ['Project #', 'Department', 'Revision', 'Type', 'Area', 'Progress']
        
        for field in fields:
            frame = ttk.Frame(self.right_frame)
            frame.pack(fill='x', padx=5, pady=2)
            ttk.Label(frame, text=field + ":").pack(side='left')
            entry = ttk.Entry(frame)
            entry.pack(side='right', expand=True, fill='x', padx=5)
            self.metadata_fields[field] = entry

        # Notes field
        ttk.Label(self.right_frame, text="Notes:").pack(anchor='w', padx=5)
        self.notes_text = tk.Text(self.right_frame, height=5)
        self.notes_text.pack(fill='x', padx=5, pady=5)

        # Buttons frame
        button_frame = ttk.Frame(self.right_frame)
        button_frame.pack(fill='x', padx=5, pady=5)

        # Save button
        self.save_btn = ttk.Button(button_frame, text="Save Metadata", 
                                 command=self.save_metadata)
        self.save_btn.pack(side='left', padx=5)

        # Clear button
        self.clear_btn = ttk.Button(button_frame, text="Clear Fields", 
                                  command=self.clear_fields)
        self.clear_btn.pack(side='left', padx=5)

    def select_directory(self):
        """Open directory selection dialog"""
        directory = filedialog.askdirectory()
        if directory:
            self.current_path = directory
            self.populate_tree(directory)
            self.status_var.set(f"Changed directory to: {directory}")

    def populate_tree(self, path):
        """Populate the tree with contents of the given path"""
        self.path_label.config(text=path)
        
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        try:
            for item in sorted(os.listdir(path)):
                item_path = os.path.join(path, item)
                item_type = 'Folder' if os.path.isdir(item_path) else 'File'
                self.tree.insert('', 'end', text=item, values=(item_type,))
            self.status_var.set(f"Loaded directory: {path}")
        except PermissionError:
            self.status_var.set("Error: Permission denied")
            messagebox.showerror("Error", "Permission denied to access this directory")
        except Exception as e:
            self.status_var.set(f"Error: {str(e)}")
            messagebox.showerror("Error", f"Error accessing directory: {str(e)}")

    def on_double_click(self, event):
        """Handle double-click on tree item"""
        selected_items = self.tree.selection()
        if not selected_items:
            return

        item = selected_items[0]
        item_text = self.tree.item(item, "text")
        item_type = self.tree.item(item, "values")[0]
        
        if item_type == 'Folder':
            new_path = os.path.join(self.current_path, item_text)
            self.current_path = new_path
            self.populate_tree(new_path)

    def on_select(self, event):
        """Handle selection of tree item"""
        selected_items = self.tree.selection()
        if selected_items:
            item = selected_items[0]
            item_text = self.tree.item(item, "text")
            item_path = os.path.join(self.current_path, item_text)
            
            # Get metadata from database
            metadata = self.db_manager.get_metadata(item_path)
            
            # Clear current fields
            self.clear_fields()
            
            # Fill in metadata if it exists
            if metadata:
                for field, value in metadata.items():
                    if field == 'notes':
                        self.notes_text.insert('1.0', value or '')
                    else:
                        field_name = field.replace('_', ' ').title()
                        if field_name in self.metadata_fields and value:
                            self.metadata_fields[field_name].insert(0, value)
                self.status_var.set(f"Loaded metadata for: {item_text}")
            else:
                self.status_var.set(f"No existing metadata for: {item_text}")

    def save_metadata(self):
        """Save metadata for selected file"""
        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showwarning("Warning", "Please select a file first")
            return

        item = selected_items[0]
        item_text = self.tree.item(item, "text")
        item_path = os.path.join(self.current_path, item_text)
        
        # Gather metadata from fields
        metadata = {
            'project_number': self.metadata_fields['Project #'].get(),
            'department': self.metadata_fields['Department'].get(),
            'revision': self.metadata_fields['Revision'].get(),
            'type': self.metadata_fields['Type'].get(),
            'area': self.metadata_fields['Area'].get(),
            'progress': self.metadata_fields['Progress'].get(),
            'notes': self.notes_text.get('1.0', tk.END).strip()
        }
        
        # Save to database
        if self.db_manager.add_or_update_metadata(item_path, metadata):
            self.status_var.set(f"Successfully saved metadata for: {item_text}")
            messagebox.showinfo("Success", f"Metadata saved for {item_text}")
        else:
            self.status_var.set(f"Error saving metadata for: {item_text}")
            messagebox.showerror("Error", f"Failed to save metadata for {item_text}")

    def clear_fields(self):
        """Clear all metadata fields"""
        for entry in self.metadata_fields.values():
            entry.delete(0, tk.END)
        self.notes_text.delete('1.0', tk.END)
        self.status_var.set("Cleared all fields")

    def __del__(self):
        """Cleanup when the window is destroyed"""
        if hasattr(self, 'db_manager'):
            del self.db_manager