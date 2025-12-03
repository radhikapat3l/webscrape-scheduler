# Web Scraping Assignment: Apple Products Prices and Ratings
# Category: Consumer Electronics (Apple Devices)
# 5 Products × 5 Retailers = 25 Data Points
# All prices converted to USD
# Student: [Your Name]
# Date: November 2024

# Install required packages
# pip install beautifulsoup4 requests lxml pandas openpyxl

import os
import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
from datetime import datetime
import time

LOG_PATH = "data/scrape_log.csv"
os.makedirs("data", exist_ok=True)

# Current exchange rates (as of November 2024)
EXCHANGE_RATES = {
    'AED': 0.27,  # 1 AED = 0.27 USD
    'GBP': 1.26,  # 1 GBP = 1.26 USD
    'USD': 1.0
}

# Headers to mimic browser
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive'
}

# Define all 25 URLs organized by product and retailer
products_urls = {
    'iPhone 17 Pro': {
        'Apple': 'https://www.apple.com/shop/buy-iphone/iphone-17-pro',
        'Sharaf DG': 'https://uae.sharafdg.com/product/apple-iphone-17-pro-256gb-cosmic-orange-middle-east-version-with-facetime/',
        'Argos': 'https://www.argos.co.uk/product/7790069',
        'Verizon': 'https://www.verizon.com/smartphones/apple-iphone-17-pro/?sku=sku6037286',
        'AT&T': 'https://www.att.com/buy/phones/apple-iphone-17-pro.html?q=iphone%2017%20pro'
    },
    'iPhone 17': {
        'Apple': 'https://www.apple.com/shop/buy-iphone/iphone-17',
        'Sharaf DG': 'https://uae.sharafdg.com/product/apple-iphone-17-256gb-white-middle-east-version-with-facetime/?promo=3647723&dg=false',
        'Argos': 'https://www.argos.co.uk/product/7790605',
        'Verizon': 'https://www.verizon.com/smartphones/apple-iphone-17/?sku=sku6037399',
        'AT&T': 'https://www.att.com/buy/phones/apple-iphone-17.html?q=iphone%2017'
    },
    'iPhone 16': {
        'Apple': 'https://www.apple.com/shop/buy-iphone/iphone-16',
        'Sharaf DG': 'https://uae.sharafdg.com/product/apple-iphone-16-128gb-white/?promo=3688886&dg=false',
        'Argos': 'https://www.argos.co.uk/product/4334222',
        'Verizon': 'https://www.verizon.com/smartphones/apple-iphone-16/?sku=sku6016049',
        'AT&T': 'https://www.att.com/buy/phones/apple-iphone-16.html'
    },
    'iPhone Air': {
        'Apple': 'https://www.apple.com/shop/buy-iphone/iphone-air',
        'Sharaf DG': 'https://uae.sharafdg.com/product/apple-iphone-air-256gb-sky-blue-middle-east-version-with-facetime/',
        'Argos': 'https://www.argos.co.uk/product/7784745',
        'Verizon': 'https://www.verizon.com/smartphones/apple-iphone-air/?sku=sku6037324',
        'AT&T': 'https://www.att.com/buy/phones/apple-iphone-air.html?q=iphone%20air'
    },
    'iPad Air': {
        'Apple': 'https://www.apple.com/shop/buy-ipad/ipad-air',
        'Sharaf DG': 'https://uae.sharafdg.com/product/11-inch-ipad-air-m3-2025-wi-fi-256gb-space-grey-middle-east-version-with-facetime/?promo=3681733&dg=false',
        'Argos': 'https://www.argos.co.uk/product/4529240',
        'Verizon': 'https://www.verizon.com/tablets/apple-ipad-air-11-inch-m3/?sku=sku6023463',
        'AT&T': 'https://www.att.com/buy/tablets/apple-ipad-air-11-inch-m3-2025.html'
    }
}

# Storage for all scraped data
all_data = []

# ==================== CURRENCY CONVERSION FUNCTIONS ====================

def convert_to_usd(price_str, original_currency):
    """Convert price from any currency to USD"""
    if not price_str or 'Error' in price_str or 'Check' in price_str:
        return price_str, None

    try:
        # Extract numeric value
        numbers = re.findall(r'[\d,]+\.?\d*', price_str)
        if not numbers:
            return price_str, None

        # Get the first number and remove commas
        amount = float(numbers[0].replace(',', ''))

        # Convert to USD
        if original_currency in EXCHANGE_RATES:
            usd_amount = amount * EXCHANGE_RATES[original_currency]

            # Check if it's a monthly payment
            if '/mo' in price_str:
                return f"${usd_amount:.2f}/mo", usd_amount
            else:
                return f"${usd_amount:.2f}", usd_amount

        return price_str, None
    except:
        return price_str, None

# ==================== SCRAPING FUNCTIONS ====================

def scrape_apple(url, product_name):
    """Scrape Apple Store"""
    try:
        print(f"  Scraping Apple for {product_name}...")
        response = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.content, 'lxml')

        # Extract price (usually "From $XXX")
        price = None
        price_elem = soup.find(text=re.compile(r'From\s*\$\d+'))
        if price_elem:
            price_match = re.search(r'From\s*\$(\d+)', price_elem)
            if price_match:
                price = f"${price_match.group(1)}"

        # Convert to USD (already in USD)
        price_usd, price_numeric = convert_to_usd(price if price else 'See website', 'USD')

        # Apple doesn't show ratings on product pages
        rating = 'Not displayed'

        return {
            'Product': product_name,
            'Retailer': 'Apple',
            'Original Price': price if price else 'See website',
            'Price (USD)': price_usd,
            'Price Numeric': price_numeric,
            'Rating': rating,
            'URL': url
        }
    except Exception as e:
        return {
            'Product': product_name,
            'Retailer': 'Apple',
            'Original Price': f'Error: {str(e)[:30]}',
            'Price (USD)': 'N/A',
            'Price Numeric': None,
            'Rating': 'N/A',
            'URL': url
        }

def scrape_sharafdg(url, product_name):
    """Scrape Sharaf DG (UAE)"""
    try:
        print(f"  Scraping Sharaf DG for {product_name}...")
        response = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.content, 'lxml')

        # Extract price (AED)
        price = None
        price_patterns = [
            soup.find('span', {'class': re.compile('price', re.I)}),
            soup.find(text=re.compile(r'AED\s*[\d,]+'))
        ]

        for price_elem in price_patterns:
            if price_elem:
                price_text = price_elem if isinstance(price_elem, str) else price_elem.get_text()
                price_match = re.search(r'AED\s*([\d,]+)', price_text)
                if price_match:
                    price = f"AED {price_match.group(1)}"
                    break

        # Convert to USD
        price_usd, price_numeric = convert_to_usd(price if price else 'Check website', 'AED')

        # Extract rating
        rating = 'No rating displayed'
        rating_elem = soup.find('div', {'class': re.compile('rating|star', re.I)})
        if rating_elem:
            rating = rating_elem.get_text().strip()

        return {
            'Product': product_name,
            'Retailer': 'Sharaf DG (UAE)',
            'Original Price': price if price else 'Check website',
            'Price (USD)': price_usd,
            'Price Numeric': price_numeric,
            'Rating': rating,
            'URL': url
        }
    except Exception as e:
        return {
            'Product': product_name,
            'Retailer': 'Sharaf DG (UAE)',
            'Original Price': f'Error: {str(e)[:30]}',
            'Price (USD)': 'N/A',
            'Price Numeric': None,
            'Rating': 'N/A',
            'URL': url
        }

def scrape_argos(url, product_name):
    """Scrape Argos (UK)"""
    try:
        print(f"  Scraping Argos for {product_name}...")
        response = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.content, 'lxml')

        # Extract price (GBP)
        price = None
        price_patterns = [
            soup.find('span', {'data-test': 'product-price'}),
            soup.find('div', {'class': re.compile('price', re.I)}),
            soup.find(text=re.compile(r'£[\d,]+\.?\d*'))
        ]

        for price_elem in price_patterns:
            if price_elem:
                price_text = price_elem if isinstance(price_elem, str) else price_elem.get_text()
                price_match = re.search(r'£([\d,]+\.?\d*)', price_text)
                if price_match:
                    price = f"£{price_match.group(1)}"
                    break

        # Convert to USD
        price_usd, price_numeric = convert_to_usd(price if price else 'Check website', 'GBP')

        # Extract rating
        rating = 'No rating displayed'
        rating_patterns = [
            soup.find('span', {'class': re.compile('rating|star', re.I)}),
            soup.find(text=re.compile(r'\d+\.?\d*\s*out of\s*5|\d+\.?\d*/5'))
        ]

        for rating_elem in rating_patterns:
            if rating_elem:
                rating = rating_elem if isinstance(rating_elem, str) else rating_elem.get_text().strip()
                break

        return {
            'Product': product_name,
            'Retailer': 'Argos (UK)',
            'Original Price': price if price else 'Check website',
            'Price (USD)': price_usd,
            'Price Numeric': price_numeric,
            'Rating': rating,
            'URL': url
        }
    except Exception as e:
        return {
            'Product': product_name,
            'Retailer': 'Argos (UK)',
            'Original Price': f'Error: {str(e)[:30]}',
            'Price (USD)': 'N/A',
            'Price Numeric': None,
            'Rating': 'N/A',
            'URL': url
        }

def scrape_verizon(url, product_name):
    """Scrape Verizon (US)"""
    try:
        print(f"  Scraping Verizon for {product_name}...")
        response = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.content, 'lxml')

        # Extract price (monthly payment)
        price = None
        price_patterns = [
            soup.find(text=re.compile(r'\$[\d.]+/mo')),
            soup.find('span', {'class': re.compile('price', re.I)})
        ]

        for price_elem in price_patterns:
            if price_elem:
                price_text = price_elem if isinstance(price_elem, str) else price_elem.get_text()
                price_match = re.search(r'\$([\d.]+)/mo', price_text)
                if price_match:
                    price = f"${price_match.group(1)}/mo"
                    break

        # Convert to USD (already in USD)
        price_usd, price_numeric = convert_to_usd(price if price else 'Check website', 'USD')

        # Extract rating
        rating = 'No rating'
        rating_patterns = [
            soup.find(text=re.compile(r'\d+\.?\d*\s*out of\s*5')),
            soup.find(text=re.compile(r'\d+\.?\d*\s*\(\d+K?\s*reviews?\)'))
        ]

        for rating_elem in rating_patterns:
            if rating_elem:
                rating = rating_elem.strip() if isinstance(rating_elem, str) else rating_elem.get_text().strip()
                # Clean up the rating
                rating_match = re.search(r'(\d+\.?\d*)\s*(?:out of 5|\([\d.KM]+\s*reviews?\))', rating)
                if rating_match:
                    rating = rating_match.group(0)
                break

        return {
            'Product': product_name,
            'Retailer': 'Verizon (US)',
            'Original Price': price if price else 'Check website',
            'Price (USD)': price_usd,
            'Price Numeric': price_numeric,
            'Rating': rating,
            'URL': url
        }
    except Exception as e:
        return {
            'Product': product_name,
            'Retailer': 'Verizon (US)',
            'Original Price': f'Error: {str(e)[:30]}',
            'Price (USD)': 'N/A',
            'Price Numeric': None,
            'Rating': 'N/A',
            'URL': url
        }

def scrape_att(url, product_name):
    """Scrape AT&T (US)"""
    try:
        print(f"  Scraping AT&T for {product_name}...")
        response = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.content, 'lxml')

        # Extract price
        price = None
        price_patterns = [
            soup.find(text=re.compile(r'\$[\d.]+/mo')),
            soup.find('span', {'class': re.compile('price', re.I)}),
            soup.find(text=re.compile(r'\$[\d,]+'))
        ]

        for price_elem in price_patterns:
            if price_elem:
                price_text = price_elem if isinstance(price_elem, str) else price_elem.get_text()
                price_match = re.search(r'\$([\d.,]+)(?:/mo)?', price_text)
                if price_match:
                    price = f"${price_match.group(1)}"
                    if '/mo' in price_text:
                        price += '/mo'
                    break

        # Convert to USD (already in USD)
        price_usd, price_numeric = convert_to_usd(price if price else 'Check website', 'USD')

        # Extract rating
        rating = 'No rating displayed'
        rating_patterns = [
            soup.find(text=re.compile(r'\d+\.?\d*\s*out of\s*5')),
            soup.find('span', {'class': re.compile('rating|star', re.I)})
        ]

        for rating_elem in rating_patterns:
            if rating_elem:
                rating = rating_elem if isinstance(rating_elem, str) else rating_elem.get_text().strip()
                break

        return {
            'Product': product_name,
            'Retailer': 'AT&T (US)',
            'Original Price': price if price else 'Check website',
            'Price (USD)': price_usd,
            'Price Numeric': price_numeric,
            'Rating': rating,
            'URL': url
        }
    except Exception as e:
        return {
            'Product': product_name,
            'Retailer': 'AT&T (US)',
            'Original Price': f'Error: {str(e)[:30]}',
            'Price (USD)': 'N/A',
            'Price Numeric': None,
            'Rating': 'N/A',
            'URL': url
        }

# ==================== MAIN SCRAPING LOOP ====================

print("=" * 90)
print("APPLE PRODUCTS WEB SCRAPING ASSIGNMENT")
print("=" * 90)
print("\nProduct Category: Consumer Electronics (Apple Devices)")
print(f"Number of Products: {len(products_urls)}")
print("Number of Retailers: 5 (Apple, Sharaf DG, Argos, Verizon, AT&T)")
print(f"Total Data Points: {len(products_urls) * 5} (25)")
print("\nCurrency Conversion Rates:")
print(f"  1 AED = ${EXCHANGE_RATES['AED']} USD")
print(f"  1 GBP = ${EXCHANGE_RATES['GBP']} USD")
print("\n" + "=" * 90)

scraper_functions = {
    'Apple': scrape_apple,
    'Sharaf DG': scrape_sharafdg,
    'Argos': scrape_argos,
    'Verizon': scrape_verizon,
    'AT&T': scrape_att
}

# Scrape all products
for product_name, retailers in products_urls.items():
    print(f"\n{product_name}")
    print("-" * 70)

    for retailer, url in retailers.items():
        scraper = scraper_functions[retailer]
        data = scraper(url, product_name)
        all_data.append(data)
        time.sleep(2)  # Be polite to servers

# ==================== DATA ANALYSIS & EXPORT ====================

print("\n" + "=" * 90)
print("SCRAPING COMPLETED - GENERATING REPORTS")
print("=" * 90)

# Create DataFrame
df = pd.DataFrame(all_data)

# Display complete results
print("\nCOMPLETE SCRAPED DATA (All Prices in USD):")
print("=" * 90)
display_df = df[['Product', 'Retailer', 'Original Price', 'Price (USD)', 'Rating']]
print(display_df.to_string(index=False))

# Create pivot table for USD prices
print("\n\nPRICES IN USD BY PRODUCT AND RETAILER:")
print("=" * 90)
price_pivot = df.pivot_table(
    index='Product',
    columns='Retailer',
    values='Price (USD)',
    aggfunc='first'
)
print(price_pivot.to_string())

# Create pivot table for ratings
print("\n\nRATINGS BY PRODUCT AND RETAILER:")
print("=" * 90)
rating_pivot = df.pivot_table(
    index='Product',
    columns='Retailer',
    values='Rating',
    aggfunc='first'
)
print(rating_pivot.to_string())

# Price comparison analysis
print("\n\nPRICE COMPARISON ANALYSIS:")
print("=" * 90)
# Filter out non-numeric prices for analysis
numeric_df = df[df['Price Numeric'].notna()].copy()

if len(numeric_df) > 0:
    price_analysis = numeric_df.groupby('Product').agg({
        'Price Numeric': ['min', 'max', 'mean', 'count']
    }).round(2)
    price_analysis.columns = ['Min Price (USD)', 'Max Price (USD)', 'Avg Price (USD)', 'Retailers with Price']
    print(price_analysis.to_string())

    # Find best and worst deals
    print("\n\nBEST DEALS (Lowest Prices):")
    print("-" * 70)
    for product in numeric_df['Product'].unique():
        product_data = numeric_df[numeric_df['Product'] == product]
        if len(product_data) > 0:
            best_deal = product_data.loc[product_data['Price Numeric'].idxmin()]
            print(f"{product}: ${best_deal['Price Numeric']:.2f} at {best_deal['Retailer']}")

# Statistics
print("\n\nSTATISTICS:")
print("=" * 90)
print(f"Total products scraped: {df['Product'].nunique()}")
print(f"Total retailers checked: {df['Retailer'].nunique()}")
print(f"Total data points collected: {len(df)}")

# Count successful scrapes
successful_prices = len(df[~df['Price (USD)'].str.contains('Error|Check|N/A', case=False, na=False)])
successful_ratings = len(df[~df['Rating'].str.contains('N/A|Error', case=False, na=False)])
print(f"Successfully scraped prices: {successful_prices}/{len(df)}")
print(f"Successfully scraped ratings: {successful_ratings}/{len(df)}")

# Export to CSV
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
csv_filename = f'apple_products_USD_{timestamp}.csv'
df.to_csv(csv_filename, index=False)
print(f"\nData exported to CSV: {csv_filename}")

# Export to Excel with multiple sheets
excel_filename = f'apple_products_USD_{timestamp}.xlsx'
with pd.ExcelWriter(excel_filename, engine='openpyxl') as writer:
    df.to_excel(writer, sheet_name='Raw Data', index=False)
    price_pivot.to_excel(writer, sheet_name='Prices USD Comparison')
    rating_pivot.to_excel(writer, sheet_name='Ratings Comparison')
    if len(numeric_df) > 0:
        price_analysis.to_excel(writer, sheet_name='Price Analysis')
print(f"Data exported to Excel: {excel_filename}")

# Create summary by retailer
print("\n\nSUMMARY BY RETAILER:")
print("=" * 90)
retailer_summary = df.groupby('Retailer').agg({
    'Product': 'count',
    'Price (USD)': lambda x: sum(~x.str.contains('Error|Check|N/A', case=False, na=False)),
    'Rating': lambda x: sum(~x.str.contains('N/A|Error|No rating', case=False, na=False))
})
retailer_summary.columns = ['Total Products', 'Prices Found', 'Ratings Found']
print(retailer_summary.to_string())


print("\n\nNOTES:")
print("-" * 90)
print(f"1. Exchange rates used: 1 AED = ${EXCHANGE_RATES['AED']} USD, 1 GBP = ${EXCHANGE_RATES['GBP']} USD")
print("2. Some retailers use dynamic JavaScript loading, which may require Selenium")
print("3. Monthly payment prices are marked with '/mo' suffix")
print("4. Not all retailers display customer ratings on product pages")
print("5. All prices have been converted to USD for easy comparison")
print("=" * 90)

def run_scrape():
    run_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    all_data = []

    for product_name, retailers in products_urls.items():
        for retailer, url in retailers.items():
            scraper = scraper_functions[retailer]
            data = scraper(url, product_name)
            data["Run Datetime"] = run_datetime
            all_data.append(data)
            time.sleep(2)

    df_run = pd.DataFrame(all_data)

    if not os.path.exists(LOG_PATH):
        df_run.to_csv(LOG_PATH, index=False)
    else:
        df_run.to_csv(LOG_PATH, mode="a", header=False, index=False)

    print(f"Saved {len(df_run)} rows to {LOG_PATH} at {run_datetime}")


if __name__ == "__main__":
    run_scrape()
