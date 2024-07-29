import streamlit as st
import requests
import re
import csv
from io import StringIO
from urllib3.exceptions import InsecureRequestWarning
from urllib.parse import urlparse

# Suppress only the single warning from urllib3 needed.
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

DEFAULT_KEYWORDS = [
    "leafly", "greenbits", "flowhub", "indica online", "treez", "biotrack", 
    "mj freeway", "meadow", "blaze", "leaflogic", "growflow", "greenline", 
    "tech pos", "posabit", "bio track", "all leaves", "lightspeed", "bindo", 
    "vende", "dauntless", "alpineiq", "hoodie analytics", "surfside", 
    "google analytics", "mixpanel", "terpli", "dutchie"
]

def add_https(url):
    if not urlparse(url).scheme:
        return 'https://' + url
    return url

def find_keywords(url, keywords):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10, verify=False)
        response.raise_for_status()
        
        html_content = response.text.lower()
        
        matches = {}
        for keyword in keywords:
            keyword_lower = keyword.lower()
            count = len(re.findall(r'\b' + re.escape(keyword_lower) + r'\b', html_content))
            if count > 0:
                matches[keyword] = count
        
        return matches
    except requests.RequestException as e:
        st.error(f"Error fetching the webpage {url}: {e}")
        return None
    except Exception as e:
        st.error(f"An unexpected error occurred for {url}: {e}")
        return None

def main():
    st.title("Keyword Finder in Multiple Web Pages")
    st.write("Enter URLs and select keywords to find out how often each keyword appears on each webpage.")
    
    urls_input = st.text_area("Enter the URLs to inspect (one per line):", "")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.subheader("Select Keywords")
        all_selected = st.checkbox("Select All Keywords")
        selected_keywords = st.multiselect(
            "Choose keywords (all selected by default):",
            DEFAULT_KEYWORDS,
            default=DEFAULT_KEYWORDS
         )    
    with col2:
        st.subheader("Add Custom Keywords")
        custom_keywords = st.text_area("Enter custom keywords (one per line):", "")
    
    if st.button("Search Keywords"):
        if urls_input and (selected_keywords or custom_keywords):
            urls = [add_https(url.strip()) for url in urls_input.split('\n') if url.strip()]
            keywords = selected_keywords + [k.strip() for k in custom_keywords.split('\n') if k.strip()]
            
            all_results = []
            
            for url in urls:
                st.subheader(url)
                url_results = find_keywords(url, keywords)
                if url_results is not None:
                    if url_results:
                        for keyword, count in url_results.items():
                            st.write(f"{keyword}: {count} time{'s' if count > 1 else ''}")
                            all_results.append([url, keyword, count])
                    else:
                        st.write("No keywords found on this page.")
                st.write("---")  # Add a separator between URLs
            
            if all_results:
                # Create CSV string
                csv_string = StringIO()
                csv_writer = csv.writer(csv_string)
                csv_writer.writerow(['URL', 'Keyword', 'Count'])
                csv_writer.writerows(all_results)
                
                # Offer download button
                st.download_button(
                    label="Download results as CSV",
                    data=csv_string.getvalue(),
                    file_name="keyword_results.csv",
                    mime="text/csv"
                )

if __name__ == "__main__":
    main()
