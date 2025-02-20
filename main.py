import logging
from gui import RealEstateScraperGUI
from tkinter import messagebox

if __name__ == "__main__":
    try:
        app = RealEstateScraperGUI()
        app.run()
    except Exception as e:
        logging.error(f"Application error: {str(e)}")
        messagebox.showerror("Error", f"Application error: {str(e)}")
