import streamlit as st
import requests
import re
import csv
from io import StringIO
from urllib3.exceptions import InsecureRequestWarning
from urllib.parse import urlparse

# Suppress only the single warning from urllib3 needed.
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

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
    st.write("Enter URLs and keywords to find out how often each keyword appears on each webpage.")
    
    urls_have_https = st.checkbox("URLs already include 'https://'", value=True)
    
    urls_input = st.text_area("Enter the URLs to inspect (one per line):", "")
    keywords_input = st.text_input("Enter keywords to search for (comma-separated):", "")
    
    if st.button("Search Keywords"):
        if urls_input and keywords_input:
            urls = [url.strip() for url in urls_input.split('\n') if url.strip()]
            if not urls_have_https:
                urls = [add_https(url) for url in urls]
            keywords = [k.strip() for k in keywords_input.replace(' ','').split(',')]
            
            all_results = []
            
            for url in urls:
                st.subheader(url)
                url_results = find_keywords(url, keywords)
                if url_results is not None:
                    if url_results:
                        for keyword, count in url_results.items():
                            if count == 1:
                                st.write(f"{keyword}: {count} time")
                            else:
                                st.write(f"{keyword}: {count} times")
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
