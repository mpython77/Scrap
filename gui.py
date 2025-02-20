import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from datetime import datetime
import threading
import os
from scraper import RealEstateScraper
from logger import Logger

class RealEstateScraperGUI:
    """A GUI class for the Real Estate Data Scraper."""
    
    def __init__(self):
        """Initialize the GUI."""
        self.root = tk.Tk()
        self.root.title("Real Estate Data Scraper")
        self.root.geometry("1000x800")
        
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.view_type = tk.StringVar(value="monthly")
        self.current_year = datetime.now().year
        self.scraping_thread = None
        self.is_scraping = False
        
        self.setup_gui()
        
    def setup_gui(self):
        """Set up the GUI components."""
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        controls_frame = ttk.Frame(main_frame)
        controls_frame.pack(fill=tk.X, pady=5)
        
        log_frame = ttk.LabelFrame(main_frame, text="Scraping Log", padding="10")
        log_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=15)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        self.logger = Logger(self.log_text)
        
        headless_frame = ttk.LabelFrame(controls_frame, text="Browser Mode", padding="10")
        headless_frame.pack(fill=tk.X, pady=5)
        self.headless_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(headless_frame, text="Run in background", variable=self.headless_var).pack(side=tk.LEFT, padx=10)
        
        view_frame = ttk.LabelFrame(controls_frame, text="View Type", padding="10")
        view_frame.pack(fill=tk.X, pady=5)
        ttk.Radiobutton(view_frame, text="Monthly", variable=self.view_type, value="monthly", command=self.update_period_options).pack(side=tk.LEFT, padx=10)
        ttk.Radiobutton(view_frame, text="Quarterly", variable=self.view_type, value="quarterly", command=self.update_period_options).pack(side=tk.LEFT, padx=10)
        
        period_frame = ttk.LabelFrame(controls_frame, text="Period", padding="10")
        period_frame.pack(fill=tk.X, pady=5)
        self.period_combo = ttk.Combobox(period_frame, state="readonly", width=30)
        self.period_combo.pack(side=tk.LEFT, padx=5)
        self.update_period_options()
        
        year_frame = ttk.LabelFrame(controls_frame, text="Year", padding="10")
        year_frame.pack(fill=tk.X, pady=5)
        self.year_combo = ttk.Combobox(year_frame, values=list(range(2014, self.current_year + 1)), state="readonly", width=30)
        self.year_combo.set(self.current_year)
        self.year_combo.pack(side=tk.LEFT, padx=5)
        
        region_frame = ttk.LabelFrame(controls_frame, text="Region", padding="10")
        region_frame.pack(fill=tk.X, pady=5)
        self.regions = ["Beograd", "Čukarica", "Novi Beograd", "Palilula", "Rakovica", 
                        "Savski venac", "Stari grad", "Voždovac", "Vračar", "Zemun", 
                        "Zvezdara", "Novi Sad", "Niš", "Kragujevac"]
        self.region_combo = ttk.Combobox(region_frame, values=self.regions, state="readonly", width=30)
        self.region_combo.set("Beograd")
        self.region_combo.pack(side=tk.LEFT, padx=5)
        
        subregion_frame = ttk.LabelFrame(controls_frame, text="Sub-region", padding="10")
        subregion_frame.pack(fill=tk.X, pady=5)
        self.subregion_combo = ttk.Combobox(subregion_frame, values=["Sve"], state="readonly", width=30)
        self.subregion_combo.set("Sve")
        self.subregion_combo.pack(side=tk.LEFT, padx=5)
        
        button_frame = ttk.Frame(controls_frame)
        button_frame.pack(fill=tk.X, pady=10)
        self.start_button = ttk.Button(button_frame, text="Start Scraping", command=self.start_scraping)
        self.start_button.pack(side=tk.LEFT, padx=5)
        self.stop_button = ttk.Button(button_frame, text="Stop", command=self.stop_scraping, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Exit", command=self.on_closing).pack(side=tk.RIGHT, padx=5)

    def update_period_options(self):
        """Update period options based on view type."""
        periods = ["Januar", "Februar", "Mart", "April", "Maj", "Jun", "Jul", "Avgust", "Septembar", "Oktobar", "Novembar", "Decembar"] \
                 if self.view_type.get() == "monthly" else ["Q1", "Q2", "Q3", "Q4"]
        self.period_combo['values'] = periods
        self.period_combo.set(periods[0])

    def scraping_task(self):
        """Perform the scraping task in a separate thread."""
        scraper = None
        try:
            if not os.path.exists("output"):
                os.makedirs("output")
            
            scraper = RealEstateScraper(self.logger, headless=self.headless_var.get())
            scraper.initialize_driver()
            
            view_type = self.view_type.get()
            period = self.period_combo.get()
            year = self.year_combo.get()
            region = self.region_combo.get()
            sub_region = self.subregion_combo.get()
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"output/real_estate_data_{region}_{period}_{year}_{timestamp}.xlsx"
            
            scraper.set_filters(view_type, period, year, region, sub_region)
            data = scraper.scrape_data()
            
            if not self.is_scraping:
                return
                
            scraper.save_to_excel(data, filename)
            self.logger.log(f"Data successfully saved to {filename}")
            messagebox.showinfo("Success", f"Data has been saved to {filename}")
            
        except Exception as error:
            self.logger.log(f"Error: {str(error)}", "error")
            messagebox.showerror("Error", str(error))
        finally:
            if scraper:
                scraper.close()
            self.is_scraping = False
            self.root.after(0, self.update_buttons)

    def start_scraping(self):
        """Start the scraping process."""
        if not self.is_scraping:
            self.is_scraping = True
            self.update_buttons()
            self.logger.start_timer()
            self.scraping_thread = threading.Thread(target=self.scraping_task)
            self.scraping_thread.daemon = True
            self.scraping_thread.start()

    def stop_scraping(self):
        """Stop the scraping process."""
        if self.is_scraping:
            self.is_scraping = False
            self.logger.log("Stopping scraper...")
            self.update_buttons()

    def update_buttons(self):
        """Update button states based on scraping status."""
        states = {True: (tk.DISABLED, tk.NORMAL), False: (tk.NORMAL, tk.DISABLED)}
        self.start_button.config(state=states[self.is_scraping][0])
        self.stop_button.config(state=states[self.is_scraping][1])
        combo_state = tk.DISABLED if self.is_scraping else "readonly"
        self.period_combo.config(state=combo_state)
        self.year_combo.config(state=combo_state)
        self.region_combo.config(state=combo_state)
        self.subregion_combo.config(state=combo_state)

    def on_closing(self):
        """Handle window closing."""
        if self.is_scraping and messagebox.askokcancel("Quit", "Scraping is in progress. Do you want to stop and exit?"):
            self.stop_scraping()
            if self.scraping_thread:
                self.scraping_thread.join(timeout=2)
        self.root.destroy()

    def run(self):
        """Run the GUI application."""
        self.root.mainloop()
