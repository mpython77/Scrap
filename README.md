# Real Estate Data Scraper

A modular Python tool for scraping real estate data from [cenenekretnina.rs](https://www.cenenekretnina.rs/). It features a `tkinter`-based GUI, `selenium` for web scraping, and `pandas` for exporting data to Excel.

## Features

- **GUI**: Configure filters like view type, period, year, region, and sub-region.
- **Scraping**: Extracts data such as type, date, price, area, and location.
- **Export**: Saves data to `.xlsx` files in `output/`.
- **Logging**: Real-time logs in the GUI and `logs/` directory.
- **Headless Mode**: Optional background execution.

## Prerequisites

- Python 3.6+ ([download](https://www.python.org/))
- Google Chrome browser
- Stable internet connection

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/real-estate-scraper.git
   cd real-estate-scraper
