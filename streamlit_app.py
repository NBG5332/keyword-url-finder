import streamlit as st
import requests
import re
import pandas as pd
from io import BytesIO
from urllib3.exceptions import InsecureRequestWarning
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup

# Suppress only the single warning from urllib3 needed.
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

KEYWORD_CATEGORIES = {
    "POS": [
        "leaflogix", "cova", "flowhub", "treez", "greenline", "blaze","iheartjane",
        "greenbits", "indicaonline", "growflow", "helix biotrack", "meadow", "proteus420",
        "posabit", "techpos", "mj platform", "portal42", "seedsuite", "weave", "global till",
        "sweed", "ommpos", "anthea", "cannapoint", "krimzen", "thsuite", "hyve tech", "bloom",
        "cannasync", "island erp", "bud bytes", "klicktrack", "dataowl", "enlighten", "ranger pos",
        "cultivera", "alleaves", "dutchie","flourish"
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
        url_lower = url.lower()
        for keyword in keywords:
            keyword_lower = keyword.lower()
            url_count = url_lower.count(keyword_lower)
            content_count = len(re.findall(r'\b' + re.escape(keyword_lower) + r'\b', html_content))
            total_count = url_count + content_count
            if total_count > 0:
                matches[keyword] = total_count
        
        return matches, html_content
    except requests.RequestException as e:
        st.error(f"Error fetching the webpage {url}: {e}")
        return None, None
    except Exception as e:
        st.error(f"An unexpected error occurred for {url}: {e}")
        return None, None

def format_results_string(results_dict):
    if not results_dict:
        return ""
    return ", ".join(f"{keyword}: {count}" for keyword, count in results_dict.items())

def categorize_results(results):
    categorized = {category: {} for category in KEYWORD_CATEGORIES}
    if results:
        for keyword, count in results.items():
            for category, keywords in KEYWORD_CATEGORIES.items():
                if keyword.lower() in [k.lower() for k in keywords]:
                    categorized[category][keyword] = count
                    break
    return categorized

def process_urls(urls, keywords):
    results_data = []
    
    for url in urls:
        if not url or pd.isna(url):  # Handle NaN values in Excel
            continue
            
        url = add_https(str(url).strip())
        main_results, html_content = find_keywords(url, keywords)
        
        # Initialize result dictionary
        result_row = {
            'URL': url,
            'Main Page - POS': '',
            'Main Page - Online Marketplace': '',
            'Main Page - Analytics': '',
            'Shop URL': '',
            'Shop Page - POS': '',
            'Shop Page - Online Marketplace': '',
            'Shop Page - Analytics': ''
        }
        
        # Process main page results
        if main_results:
            categorized_main = categorize_results(main_results)
            for category in KEYWORD_CATEGORIES:
                result_row[f'Main Page - {category}'] = format_results_string(categorized_main[category])
        
        # Process shop page
        if html_content:
            shop_url = find_shop_link(html_content, url)
            if shop_url:
                result_row['Shop URL'] = shop_url
                shop_results, _ = find_keywords(shop_url, keywords)
                if shop_results:
                    categorized_shop = categorize_results(shop_results)
                    for category in KEYWORD_CATEGORIES:
                        result_row[f'Shop Page - {category}'] = format_results_string(categorized_shop[category])
        
        results_data.append(result_row)
    
    return pd.DataFrame(results_data)

def main():
    st.title("Keyword Finder in Multiple Web Pages")
    st.write("Enter URLs directly or upload an Excel file to find keywords.")
    
    input_method = st.radio("Choose input method:", ["Direct Input", "Excel File"])
    
    urls = []
    if input_method == "Direct Input":
        urls_input = st.text_area("Enter the URLs to inspect (one per line):", "")
        if urls_input:
            urls = [url.strip() for url in urls_input.split('\n') if url.strip()]
    else:
        uploaded_file = st.file_uploader("Upload Excel file", type=['xlsx', 'xls'])
        if uploaded_file:
            try:
                df = pd.read_excel(uploaded_file)
                url_column = st.selectbox("Select URL column:", df.columns)
                if url_column:
                    urls = df[url_column].tolist()
            except Exception as e:
                st.error(f"Error reading Excel file: {e}")
    
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
        if urls and (selected_keywords or custom_keywords):
            keywords = selected_keywords + [k.strip() for k in custom_keywords.split('\n') if k.strip()]
            
            with st.spinner('Processing URLs... This may take a few minutes.'):
                results_df = process_urls(urls, keywords)
            
            # Display results
            st.subheader("Results")
            st.dataframe(results_df)
            
            # Convert DataFrame to Excel
            buffer = BytesIO()
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                results_df.to_excel(writer, index=False, sheet_name='Results')
                
                # Auto-adjust columns width
                worksheet = writer.sheets['Results']
                for idx, col in enumerate(results_df.columns):
                    max_length = max(
                        results_df[col].astype(str).apply(len).max(),
                        len(col)
                    ) + 2
                    worksheet.column_dimensions[chr(65 + idx)].width = min(max_length, 50)  # limit to 50 characters
            
            st.download_button(
                label="Download Results as Excel",
                data=buffer.getvalue(),
                file_name="keyword_results.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

if __name__ == "__main__":
    main()
