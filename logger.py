import logging
from datetime import datetime
from pathlib import Path
import time
import tkinter as tk

class Logger:
    """A class to handle logging to both a file and a GUI widget."""
    
    def __init__(self, log_widget=None):
        """Initialize the logger with an optional GUI log widget."""
        self.log_widget = log_widget
        self.start_time = None
        self.log_file = None
        self.setup_logging()
        
        # Messages that should appear in blue in the GUI
        self.blue_messages = [
            "Scraping completed. Total rows scraped:",
            "Saving",
            "Data saved successfully",
            "Data successfully saved to",
            "Closing browser",
            "Browser closed successfully"
        ]

    def setup_logging(self):
        """Configure logging to file and console."""
        Path("logs").mkdir(exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file = f"logs/scraping_log_{timestamp}.txt"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.log_file),
                logging.StreamHandler()
            ]
        )

    def should_be_blue(self, message):
        """Check if the message should be displayed in blue."""
        return any(blue_msg in message for blue_msg in self.blue_messages)

    def log(self, message, level="info"):
        """Log a message to file, console, and GUI if available."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        if level == "info":
            logging.info(message)
        elif level == "error":
            logging.error(message)
        elif level == "warning":
            logging.warning(message)
        
        if self.log_widget:
            log_entry = f"{timestamp} - {message}\n"
            self.log_widget.insert(tk.END, log_entry)
            
            if self.should_be_blue(message):
                end_pos = self.log_widget.index("end-1c")
                start_pos = f"{float(end_pos) - 1:.1f}"
                self.log_widget.tag_add("blue", start_pos, end_pos)
                self.log_widget.tag_config("blue", foreground="blue")
            
            self.log_widget.see(tk.END)

    def start_timer(self):
        """Start the timer for scraping duration."""
        self.start_time = time.time()
        self.log("Starting scraping process...")

    def end_timer(self):
        """End the timer and log the duration."""
        if self.start_time:
            elapsed_time = time.time() - self.start_time
            self.log(f"Scraping completed in {elapsed_time:.2f} seconds")
            return elapsed_time
        return 0
