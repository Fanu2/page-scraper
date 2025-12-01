
# **SimpleScraper – GUI Web Scraper (Python + Tkinter)**

SimpleScraper is a lightweight, beginner-friendly Python application that lets you scrape website content using **CSS selectors**, preview results, follow pagination, and export data to **CSV or JSON**.
It includes a full **Tkinter GUI**, so no coding is required to run it.

---

## 🚀 **Features**

### 🔍 Scrape any web page

* Enter a **URL**
* Enter a **CSS selector** (like `.title`, `a`, `article h2`, etc.)
* Extract **text**, `href`, `src`, or any HTML attribute

### 📄 Pagination support

* Provide a selector for the “next page” link
* Scraper will follow pages automatically
* Limit how many pages to scrape

### 🕹️ GUI features

* One-click scraping
* Preview results from a single page
* Start/Stop scraping
* Live logs and status updates
* Multithreaded (UI never freezes)

### 💾 Export Options

* Export full results to **CSV**
* Export to **JSON**

### ⚙️ Technical

* Uses `requests` + `BeautifulSoup4`
* Custom User-Agent
* Adjustable delay between requests
* Handles relative URLs
* Built-in error reporting

---

## 📦 **Installation**

### 1. Clone the repository:

```bash
git clone https://github.com/YOURNAME/REPO_NAME.git
cd REPO_NAME
```

### 2. Create a virtual environment (recommended):

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies:

```bash
pip install requests beautifulsoup4
```

---

## ▶️ **Running the App**

```bash
python3 simple_scraper.py
```

The GUI will appear.

---

## 🧑‍💻 **How to Use**

### 1. **Start URL**

Example:

```
https://news.ycombinator.com/
```

### 2. **CSS Selector**

Examples:

* `.titlelink`
* `a`
* `article h2`
* `.product-item .name`

### 3. **Attribute**

* `text` → get text content
* `href` → extract links
* `src` → extract images
* Any valid HTML attribute

### 4. **Pagination (optional)**

Enter a selector that points to the *Next Page* button/link.
Examples:

* `.morelink`
* `a.next`
* `.pagination .next a`

### 5. **Click “Start Scrape”**

Results appear in the results window.

### 6. **Export**

Use:

* **Export CSV**
* **Export JSON**

---

## 📁 **Project Structure**

```
SimpleScraper/
│
├── simple_scraper.py      # Main application (GUI + scraper logic)
├── README.md              # Documentation
└── requirements.txt       # Optional: dependency list
```

---

## ⚠️ **Ethics & Website Rules**

Always check the target site's:

* `robots.txt`
* Terms of Service
* Rate-limit expectations

This app is **not** designed to bypass protections.

---

## 🧱 **Limitations**

* Does **not** execute JavaScript (not a browser)
* Some dynamic sites may require Selenium or Playwright
* Pagination only works with link-based navigation

---

## 🛠️ **Planned Improvements**

* [ ] Headless browser mode (Selenium/Playwright)
* [ ] Regex extraction tools
* [ ] Save HTML snapshots
* [ ] Scrape multiple URLs simultaneously
* [ ] Dark mode UI

If you want any of these added, just ask!

---

## 🤝 **Contributing**

Pull requests and suggestions are welcome!
Feel free to open Issues for bugs or feature requests.

---

## 📜 **License**

MIT License.
Free to use, modify, and distribute.

---
