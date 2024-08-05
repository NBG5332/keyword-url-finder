import streamlit as st
import requests
import re
import csv
from io import StringIO
from urllib3.exceptions import InsecureRequestWarning
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup

# Suppress only the single warning from urllib3 needed.
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

KEYWORD_CATEGORIES = {
    "POS": [
        "leaflogix", "cova", "flowhub", "treez", "greenline", "blaze", "jane", "iheartjane",
        "greenbits", "indicaonline", "growflow", "helix biotrack", "meadow", "proteus420",
        "posabit", "techpos", "mj platform", "portal42", "seedsuite", "weave", "global till",
        "sweed", "ommpos", "anthea", "cannapoint", "krimzen", "thsuite", "hyve tech", "bloom",
        "cannasync", "island erp", "bud bytes", "klicktrack", "dataowl", "enlighten", "ranger pos",
        "cultivera", "alleaves", "dutchie"
    ],
    "Online Marketplace": ["weedmaps", "surfside", "leafly"],
    "Analytics": ["alpineiq", "terpli"]
}

DEFAULT_KEYWORDS = [keyword for category in KEYWORD_CATEGORIES.values() for keyword in category]

def add_https(url):
    if not urlparse(url).scheme:
        return 'https://' + url
    return url

def find_shop_link(html_content, base_url):
    soup = BeautifulSoup(html_content, 'html.parser')
    shop_links = soup.find_all('a', href=True, text=re.compile(r'shop|store', re.I))
    if shop_links:
        return urljoin(base_url, shop_links[0]['href'])
    return None

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
        
        return matches, html_content
    except requests.RequestException as e:
        st.error(f"Error fetching the webpage {url}: {e}")
        return None, None
    except Exception as e:
        st.error(f"An unexpected error occurred for {url}: {e}")
        return None, None

def categorize_results(results):
    categorized = {category: {} for category in KEYWORD_CATEGORIES}
    for keyword, count in results.items():
        for category, keywords in KEYWORD_CATEGORIES.items():
            if keyword.lower() in keywords:
                categorized[category][keyword] = count
                break
    return categorized

def main():
    st.title("Keyword Finder in Multiple Web Pages")
    st.write("Enter URLs to find keywords related to POS, Online Marketplace, and Analytics.")
    
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
    
    if st.button("Search Keywords"):
        if urls_input and (selected_keywords or custom_keywords):
            urls = [add_https(url.strip()) for url in urls_input.split('\n') if url.strip()]
            keywords = selected_keywords + [k.strip() for k in custom_keywords.split('\n') if k.strip()]
            
            all_results = []
            
            for url in urls:
                st.subheader(url)
                url_results, html_content = find_keywords(url, keywords)
                if url_results is not None:
                    categorized_results = categorize_results(url_results)
                    st.write("Main page results:")
                    for category, results in categorized_results.items():
                        if results:
                            st.write(f"{category}:")
                            for keyword, count in results.items():
                                st.write(f"  {keyword}: {count} time{'s' if count > 1 else ''}")
                                all_results.append([url, "Main", category, keyword, count])
                    
                    if not any(categorized_results.values()):
                        st.write("No relevant keywords found on the main page.")
                    
                    # Find and process shop link
                    shop_link = find_shop_link(html_content, url)
                    if shop_link:
                        st.write(f"\nShop page: {shop_link}")
                        shop_results, _ = find_keywords(shop_link, keywords)
                        if shop_results:
                            categorized_shop_results = categorize_results(shop_results)
                            st.write("Shop page results:")
                            for category, results in categorized_shop_results.items():
                                if results:
                                    st.write(f"{category}:")
                                    for keyword, count in results.items():
                                        st.write(f"  {keyword}: {count} time{'s' if count > 1 else ''}")
                                        all_results.append([url, "Shop", category, keyword, count])
                        else:
                            st.write("No relevant keywords found on the shop page.")
                    else:
                        st.write("No shop link found on the main page.")
                st.write("---")  # Add a separator between URLs
            
            if all_results:
                # Create CSV string
                csv_string = StringIO()
                csv_writer = csv.writer(csv_string)
                csv_writer.writerow(['Main URL', 'Page Type', 'Category', 'Keyword', 'Count'])
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
