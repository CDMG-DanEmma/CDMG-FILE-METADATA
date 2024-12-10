import os
import sys

# Add the src directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import tkinter as tk
from gui.main_window import MainWindow
from database.models import init_db

def main():
    # Initialize database
    init_db()
    
    # Create and run application
    root = tk.Tk()
    app = MainWindow(root)
    root.mainloop()

if __name__ == "__main__":
    main()