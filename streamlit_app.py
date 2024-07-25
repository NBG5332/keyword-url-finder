import streamlit as st
import requests
import re
import pandas as pd
from io import BytesIO
from urllib3.exceptions import InsecureRequestWarning

# Suppress only the single warning from urllib3 needed.
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

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
    
    urls_input = st.text_area("Enter the URLs to inspect (one per line):", "")
    keywords_input = st.text_input("Enter keywords to search for (comma-separated):", "")
    
    if st.button("Search Keywords"):
        if urls_input and keywords_input:
            urls = [url.strip() for url in urls_input.split(',') if url.strip()]
            keywords = [k.strip() for k in keywords_input.replace(' ','').split(',')]
            
            results = []
            
            for url in urls:
                url_results = find_keywords(url, keywords)
                if url_results is not None:
                    results.append({'URL': url, **url_results})
            
            if results:
                df = pd.DataFrame(results)
                st.success("Keywords found:")
                st.dataframe(df)
                
                # Create Excel file
                output = BytesIO()
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    df.to_excel(writer, index=False, sheet_name='Keyword Results')
                
                # Offer download link
                st.download_button(
                    label="Download results as Excel",
                    data=output.getvalue(),
                    file_name="keyword_results.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            else:
                st.warning("No results found or all URL requests failed.")

if __name__ == "__main__":
    main()
