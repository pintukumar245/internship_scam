import requests
from bs4 import BeautifulSoup
import csv
import time
import random

def scrape_internshala(keyword='data-science', pages=1):
    base_url = "https://internshala.com"
    scraped_data = []

    # Using headers to mimic a real browser visit
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'
    }

    for page in range(1, pages + 1):
        url = f"{base_url}/internships/{keyword}-internship/page-{page}/"
        print(f"Scraping {url}...")
        
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find all internship listings on Internshala
            # Note: class names might change over time, so you may need to inspect the webpage and update them
            internships = soup.find_all('div', class_='internship_meta')
            
            for internship in internships:
                title_elem = internship.find('h3', class_='heading_4_5 profile')
                company_elem = internship.find('div', class_='company_name')
                location_elem = internship.find('a', class_='location_link')
                stipend_elem = internship.find('span', class_='stipend')
                
                title = title_elem.text.strip() if title_elem else "N/A"
                company = company_elem.text.strip() if company_elem else "N/A"
                location = location_elem.text.strip() if location_elem else "N/A"
                stipend = stipend_elem.text.strip() if stipend_elem else "N/A"
                
                # Potential scam indicators to look out for in future analysis:
                # 1. Very high stipend for unknown company
                # 2. Vague job descriptions
                # 3. Asking for registration fees
                scam_indicator = "Needs Review" 

                scraped_data.append({
                    'Title': title,
                    'Company': company,
                    'Location': location,
                    'Stipend': stipend,
                    'Source': 'Internshala',
                    'Scam_Indicator_Flag': scam_indicator
                })
            
            print(f"Scraped {len(internships)} internships from page {page}")
            # Be polite and add a delay so we don't overwhelm the server
            time.sleep(random.uniform(2, 5))
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching URL {url}: {e}")

    return scraped_data

def save_to_csv(data, filename="internship_data.csv"):
    if not data:
        print("No data to save.")
        return
        
    keys = data[0].keys()
    with open(filename, 'w', newline='', encoding='utf-8') as output_file:
        dict_writer = csv.DictWriter(output_file, fieldnames=keys)
        dict_writer.writeheader()
        dict_writer.writerows(data)
    print(f"Data saved successfully to {filename}")

if __name__ == "__main__":
    print("Starting Internship Data Scraper...")
    
    # You can change the keyword to 'marketing', 'hr', etc.
    # Be careful not to scrape too many pages at once!
    internshala_data = scrape_internshala(keyword='data-science', pages=2)
    
    save_to_csv(internshala_data, "internship_scam_analysis_data.csv")
    print("Scraping finished!")
