import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import warnings
warnings.filterwarnings('ignore')

def scrape_jamabandi_table(district, tehsil, village, khewat=None, name=None):
    """
    Scrape land records table from Jamabandi website
    
    Parameters:
    district (str): District name
    tehsil (str): Tehsil name
    village (str): Village name
    khewat (str, optional): Khewat number
    name (str, optional): Owner name for filtering
    
    Returns:
    pandas.DataFrame: Extracted table data
    """
    
    # Base URL
    base_url = "https://jamabandi.nic.in/DSNakal/CheckMutDetail1"
    
    # Session to maintain cookies
    session = requests.Session()
    
    try:
        # First, get the initial page to set cookies
        print("Initializing connection...")
        session.get(base_url)
        
        # Prepare form data
        form_data = {
            'District': district,
            'Tehsil': tehsil,
            'Village': village,
            'Khewat': khewat if khewat else '',
            'Name': name if name else '',
            'B1': 'Submit'
        }
        
        # Set headers to mimic a browser
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Referer': base_url,
            'Origin': 'https://jamabandi.nic.in',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        print("Submitting form...")
        # Submit the form
        response = session.post(base_url, data=form_data, headers=headers)
        
        # Check if response is successful
        if response.status_code != 200:
            print(f"Error: Received status code {response.status_code}")
            return None
        
        # Parse the HTML content
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find the table
        table = soup.find('table', {'border': '1'})
        
        if not table:
            print("No table found on the page.")
            return None
        
        # Extract table headers
        headers = []
        header_row = table.find('tr')
        for th in header_row.find_all('th'):
            headers.append(th.text.strip())
        
        # Extract table rows
        rows = []
        for tr in table.find_all('tr')[1:]:  # Skip header row
            cells = tr.find_all('td')
            row = [cell.text.strip() for cell in cells]
            if row:  # Only add non-empty rows
                rows.append(row)
        
        # Create DataFrame
        if headers and rows:
            df = pd.DataFrame(rows, columns=headers)
            print(f"Successfully extracted {len(df)} records")
            return df
        else:
            print("No data found in the table")
            return None
            
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return None

def save_to_excel(df, filename):
    """Save DataFrame to Excel file"""
    if df is not None:
        df.to_excel(filename, index=False)
        print(f"Data saved to {filename}")
    else:
        print("No data to save")

def save_to_csv(df, filename):
    """Save DataFrame to CSV file"""
    if df is not None:
        df.to_csv(filename, index=False)
        print(f"Data saved to {filename}")
    else:
        print("No data to save")

# Example usage
if __name__ == "__main__":
    # Example parameters (you'll need to replace these with actual values)
    district = "Ambala"
    tehsil = "Ambala"
    village = "Baria"
    
    # Scrape the table
    df = scrape_jamabandi_table(district, tehsil, village)
    
    # Save results
    if df is not None:
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        excel_filename = f"jamabandi_data_{timestamp}.xlsx"
        csv_filename = f"jamabandi_data_{timestamp}.csv"
        
        save_to_excel(df, excel_filename)
        save_to_csv(df, csv_filename)
        
        # Display first few rows
        print("\nFirst 5 rows of extracted data:")
        print(df.head())
    else:
        print("Failed to extract data")
