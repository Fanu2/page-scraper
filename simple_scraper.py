#!/usr/bin/env python3
"""
simple_scraper.py

Small GUI + library for scraping HTML pages using CSS selectors.

Dependencies:
    pip install requests beautifulsoup4

Run:
    python3 simple_scraper.py
"""

import requests
from bs4 import BeautifulSoup
import csv
import json
import time
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext

# ---------- Scraper library ----------
class Scraper:
    def __init__(self, user_agent=None, timeout=10, delay=1.0, max_pages=1):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": user_agent or "SimpleScraper/1.0 (+https://github.com/yourname)"
        })
        self.timeout = timeout
        self.delay = float(delay)
        self.max_pages = int(max_pages)

    def fetch(self, url):
        """Fetch HTML content for a URL (returns text); raises requests exceptions on error."""
        resp = self.session.get(url, timeout=self.timeout)
        resp.raise_for_status()
        return resp.text

    def parse_items(self, html, selector, attribute=None):
        """
        Parse HTML using BeautifulSoup and a CSS selector.
        If attribute is None or "text", returns element text stripped.
        Otherwise returns element.get(attribute, '').
        """
        soup = BeautifulSoup(html, "html.parser")
        nodes = soup.select(selector)
        results = []
        for el in nodes:
            if attribute is None or attribute.lower() == "text":
                results.append(el.get_text(strip=True))
            else:
                results.append(el.get(attribute, ""))
        return results

    def find_next(self, html, next_selector):
        """
        Find next page URL using a selector. The selector should match a link element (a).
        Returns absolute/relative href string or None if not found.
        """
        soup = BeautifulSoup(html, "html.parser")
        el = soup.select_one(next_selector)
        if el and el.name == "a":
            return el.get("href")
        # If selector matches something else, try find first <a> inside it
        if el:
            a = el.find("a")
            if a:
                return a.get("href")
        return None

    def absolute_url(self, base, href):
        """Make absolute URL using requests' util."""
        return requests.compat.urljoin(base, href)

    def scrape(self, start_url, selector, attribute=None, next_selector=None):
        """
        Scrape pages starting from start_url.
        Yields (url, item) pairs for each item found by selector.
        Follows "next_selector" up to max_pages.
        """
        results = []
        url = start_url
        pages = 0
        visited = set()
        while url and pages < self.max_pages and url not in visited:
            try:
                html = self.fetch(url)
            except Exception as e:
                raise RuntimeError(f"Failed to fetch {url}: {e}")
            visited.add(url)
            items = self.parse_items(html, selector, attribute)
            for it in items:
                results.append({"page": url, "value": it})
            pages += 1
            # find next
            if next_selector:
                href = self.find_next(html, next_selector)
                if not href:
                    break
                url = self.absolute_url(url, href)
            else:
                break
            time.sleep(self.delay)
        return results

# ---------- GUI ----------
class ScraperGUI:
    def __init__(self, root):
        self.root = root
        root.title("Simple Scraper")
        root.geometry("900x600")

        frame = ttk.Frame(root, padding=10)
        frame.pack(fill="both", expand=True)

        # Input rows
        row = 0
        ttk.Label(frame, text="Start URL:").grid(column=0, row=row, sticky="w")
        self.url_entry = ttk.Entry(frame, width=80)
        self.url_entry.grid(column=1, row=row, columnspan=4, sticky="we", padx=6, pady=4)

        row += 1
        ttk.Label(frame, text="CSS Selector:").grid(column=0, row=row, sticky="w")
        self.sel_entry = ttk.Entry(frame, width=40)
        self.sel_entry.grid(column=1, row=row, sticky="we", padx=6)

        ttk.Label(frame, text="Attribute (href/text/src):").grid(column=2, row=row, sticky="w")
        self.attr_entry = ttk.Entry(frame, width=20)
        self.attr_entry.insert(0, "text")
        self.attr_entry.grid(column=3, row=row, sticky="we", padx=6)

        row += 1
        ttk.Label(frame, text="Next page selector (optional):").grid(column=0, row=row, sticky="w")
        self.next_entry = ttk.Entry(frame, width=40)
        self.next_entry.grid(column=1, row=row, sticky="we", padx=6)

        ttk.Label(frame, text="Max pages:").grid(column=2, row=row, sticky="w")
        self.max_pages_spin = ttk.Spinbox(frame, from_=1, to=100, width=6)
        self.max_pages_spin.set("1")
        self.max_pages_spin.grid(column=3, row=row, sticky="w")

        ttk.Label(frame, text="Delay (sec):").grid(column=4, row=row, sticky="w")
        self.delay_entry = ttk.Entry(frame, width=6)
        self.delay_entry.insert(0, "1.0")
        self.delay_entry.grid(column=5, row=row, sticky="w")

        row += 1
        ttk.Label(frame, text="User-Agent (optional):").grid(column=0, row=row, sticky="w")
        self.ua_entry = ttk.Entry(frame, width=60)
        self.ua_entry.grid(column=1, row=row, columnspan=4, sticky="we", padx=6)
        self.ua_entry.insert(0, "SimpleScraper/1.0 (https://github.com/yourname)")

        # Buttons
        row += 1
        self.start_button = ttk.Button(frame, text="Start Scrape", command=self.start_scrape)
        self.start_button.grid(column=1, row=row, sticky="we", padx=6, pady=8)

        self.preview_button = ttk.Button(frame, text="Preview (single page)", command=self.preview_once)
        self.preview_button.grid(column=2, row=row, sticky="we", padx=6, pady=8)

        self.export_csv_button = ttk.Button(frame, text="Export CSV", command=self.export_csv, state="disabled")
        self.export_csv_button.grid(column=3, row=row, sticky="we", padx=6, pady=8)

        self.export_json_button = ttk.Button(frame, text="Export JSON", command=self.export_json, state="disabled")
        self.export_json_button.grid(column=4, row=row, sticky="we", padx=6, pady=8)

        # Results area
        row += 1
        ttk.Label(frame, text="Results (value | source page) :").grid(column=0, row=row, sticky="w")
        row += 1
        self.results_box = scrolledtext.ScrolledText(frame, wrap="none", height=18)
        self.results_box.grid(column=0, row=row, columnspan=6, sticky="nsew", padx=4, pady=4)
        frame.rowconfigure(row, weight=1)
        frame.columnconfigure(1, weight=1)

        # status
        row += 1
        self.status_var = tk.StringVar(value="Idle")
        ttk.Label(frame, textvariable=self.status_var).grid(column=0, row=row, columnspan=6, sticky="we")

        # internal
        self.results = []
        self.thread = None

    def set_status(self, text):
        self.status_var.set(text)

    def preview_once(self):
        url = self.url_entry.get().strip()
        selector = self.sel_entry.get().strip()
        if not url or not selector:
            messagebox.showwarning("Missing input", "Please enter a URL and CSS selector for preview.")
            return
        ua = self.ua_entry.get().strip() or None
        s = Scraper(user_agent=ua, timeout=10, delay=0, max_pages=1)
        try:
            html = s.fetch(url)
            items = s.parse_items(html, selector, self.attr_entry.get().strip() or None)
            self.results_box.delete("1.0", tk.END)
            for it in items[:200]:
                self.results_box.insert(tk.END, f"{it}\n")
            self.set_status(f"Preview: {len(items)} items found on single page")
        except Exception as e:
            messagebox.showerror("Error", str(e))
            self.set_status("Error in preview")

    def start_scrape(self):
        if self.thread and self.thread.is_alive():
            messagebox.showinfo("Busy", "Scraping is already in progress.")
            return
        url = self.url_entry.get().strip()
        selector = self.sel_entry.get().strip()
        if not url or not selector:
            messagebox.showwarning("Missing input", "Enter start URL and CSS selector.")
            return
        try:
            max_pages = int(self.max_pages_spin.get())
        except Exception:
            max_pages = 1
        try:
            delay = float(self.delay_entry.get())
        except Exception:
            delay = 1.0

        ua = self.ua_entry.get().strip() or None
        next_sel = self.next_entry.get().strip() or None

        self.results = []
        self.results_box.delete("1.0", tk.END)
        self.export_csv_button.config(state="disabled")
        self.export_json_button.config(state="disabled")
        self.set_status("Starting scrape...")
        self.thread = threading.Thread(target=self._scrape_bg, args=(url, selector, self.attr_entry.get().strip() or None, next_sel, ua, delay, max_pages), daemon=True)
        self.thread.start()

    def _scrape_bg(self, start_url, selector, attribute, next_selector, user_agent, delay, max_pages):
        try:
            scraper = Scraper(user_agent=user_agent, timeout=15, delay=delay, max_pages=max_pages)
            self.set_status("Fetching...")
            items = scraper.scrape(start_url, selector, attribute, next_selector)
            self.results = items
            # update UI
            self.root.after(0, lambda: self._show_results(items))
            self.set_status(f"Finished: {len(items)} items from up to {max_pages} page(s).")
            self.root.after(0, lambda: self.export_csv_button.config(state="normal"))
            self.root.after(0, lambda: self.export_json_button.config(state="normal"))
        except Exception as e:
            self.set_status("Error occurred.")
            messagebox.showerror("Scrape error", str(e))

    def _show_results(self, items):
        self.results_box.delete("1.0", tk.END)
        for it in items:
            # very simple tab-separated display
            page = it.get("page", "")
            val = it.get("value", "")
            self.results_box.insert(tk.END, f"{val} \t| {page}\n")

    def export_csv(self):
        if not self.results:
            messagebox.showinfo("No data", "No results to export.")
            return
        path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV", "*.csv"), ("All files", "*.*")])
        if not path:
            return
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["page", "value"])
            writer.writeheader()
            for it in self.results:
                writer.writerow({"page": it.get("page", ""), "value": it.get("value", "")})
        messagebox.showinfo("Saved", f"Saved CSV to {path}")

    def export_json(self):
        if not self.results:
            messagebox.showinfo("No data", "No results to export.")
            return
        path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON", "*.json"), ("All files", "*.*")])
        if not path:
            return
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.results, f, ensure_ascii=False, indent=2)
        messagebox.showinfo("Saved", f"Saved JSON to {path}")

def main():
    root = tk.Tk()
    app = ScraperGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()

