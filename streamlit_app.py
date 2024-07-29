import streamlit as st
import requests
import re
import csv
from io import StringIO
from urllib3.exceptions import InsecureRequestWarning
from urllib.parse import urlparse
from bs4 import BeautifulSoup

# Suppress only the single warning from urllib3 needed.
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

DEFAULT_KEYWORDS = [
    "leafly", "greenbits", "flowhub", "indica online", "treez", "biotrack", 
    "mj freeway", "meadow", "blaze", "leaflogic", "growflow", "greenline", 
    "tech pos", "posabit", "bio track", "all leaves", "lightspeed", "bindo", 
    "vende", "dauntless", "alpineiq", "hoodie analytics", "surfside", 
    "google analytics", "mixpanel", "terpli", "dutchie"
]

POS_SYSTEMS = {
    "Treez": ["treez.io", "treezsoftware"],
    "Flowhub": ["flowhub.com", "flowhub.co"],
    "Greenbits": ["greenbits.com"],
    "BioTrack": ["biotrack.com"],
    "MJ Freeway": ["mjfreeway.com"],
    "Blaze": ["blaze.me"],
    "LeafLogix": ["leaflogix.com"],
    "GrowFlow": ["growflow.com"],
    "IndicaOnline": ["indicaonline.com"],
}

PAYMENT_PROCESSORS = {
    "Square": ["squareup.com"],
    "Stripe": ["stripe.com"],
    "PayPal": ["paypal.com"],
    "Authorize.Net": ["authorize.net"],
    "Merrco": ["merrco.com"],
    "CanPay": ["canpay.com"],
}

def add_https(url):
    if not urlparse(url).scheme:
        return 'https://' + url
    return url

def find_keywords_and_systems(url, keywords):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10, verify=False)
        response.raise_for_status()
        
        html_content = response.text.lower()
        soup = BeautifulSoup(html_content, 'html.parser')
        
        matches = {}
        for keyword in keywords:
            keyword_lower = keyword.lower()
            count = len(re.findall(r'\b' + re.escape(keyword_lower) + r'\b', html_content))
            if count > 0:
                matches[keyword] = count
        
        # Check for POS systems
        pos_system = "Unknown"
        for system, indicators in POS_SYSTEMS.items():
            if any(indicator.lower() in html_content for indicator in indicators):
                pos_system = system
                break
        
        # Check for payment processors
        payment_processor = "Unknown"
        for processor, indicators in PAYMENT_PROCESSORS.items():
            if any(indicator.lower() in html_content for indicator in indicators):
                payment_processor = processor
                break
        
        return matches, pos_system, payment_processor
    except requests.RequestException as e:
        st.error(f"Error fetching the webpage {url}: {e}")
        return None, "Error", "Error"
    except Exception as e:
        st.error(f"An unexpected error occurred for {url}: {e}")
        return None, "Error", "Error"

def main():
    st.title("Website Analyzer")
    st.write("Enter URLs to analyze for keywords, POS systems, and payment processors.")
    
    urls_input = st.text_area("Enter the URLs to inspect (one per line):", "")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.subheader("Select Keywords")
        all_selected = st.checkbox("Select All Keywords")
        selected_keywords = st.multiselect(
            "Choose keywords:",
            DEFAULT_KEYWORDS,
            default=DEFAULT_KEYWORDS if all_selected else []
        )
    
    with col2:
        st.subheader("Add Custom Keywords")
        custom_keywords = st.text_area("Enter custom keywords (one per line):", "")
    
    if st.button("Analyze Websites"):
        if urls_input and (selected_keywords or custom_keywords):
            urls = [add_https(url.strip()) for url in urls_input.split('\n') if url.strip()]
            keywords = selected_keywords + [k.strip() for k in custom_keywords.split('\n') if k.strip()]
            
            all_results = []
            
            for url in urls:
                st.subheader(url)
                keyword_results, pos_system, payment_processor = find_keywords_and_systems(url, keywords)
                if keyword_results is not None:
                    st.write(f"Detected POS System: {pos_system}")
                    st.write(f"Detected Payment Processor: {payment_processor}")
                    if keyword_results:
                        st.write("Keywords found:")
                        for keyword, count in keyword_results.items():
                            st.write(f"- {keyword}: {count} time{'s' if count > 1 else ''}")
                            all_results.append([url, keyword, count, pos_system, payment_processor])
                    else:
                        st.write("No keywords found on this page.")
                        all_results.append([url, "No keywords found", 0, pos_system, payment_processor])
                st.write("---")  # Add a separator between URLs
            
            if all_results:
                # Create CSV string
                csv_string = StringIO()
                csv_writer = csv.writer(csv_string)
                csv_writer.writerow(['URL', 'Keyword', 'Count', 'POS System', 'Payment Processor'])
                csv_writer.writerows(all_results)
                
                # Offer download button
                st.download_button(
                    label="Download results as CSV",
                    data=csv_string.getvalue(),
                    file_name="website_analysis_results.csv",
                    mime="text/csv"
                )

if __name__ == "__main__":
    main()
