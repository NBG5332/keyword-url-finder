import os
import streamlit as st
import re
from playwright.sync_api import sync_playwright

def setup_playwright():
    # Run the setup script to install Playwright browsers
    if not os.path.exists('/home/appuser/.cache/ms-playwright'):
        os.system("chmod +x setup.sh && ./setup.sh")

def find_keywords_playwright(url, keywords):
    setup_playwright()
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url, wait_until="networkidle")  # Ensures the page is fully loaded
            html_content = page.content().lower()
            browser.close()

        matches = {}
        for keyword in keywords:
            keyword_lower = keyword.lower()
            found = re.findall(r'(\S*' + re.escape(keyword_lower) + r'\S*)', html_content)
            if found:
                matches[keyword] = found
        
        return matches

    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")
        return None

def main():
    st.title("Keyword Finder in Web Pages")
    st.write("Enter a URL and a list of keywords to find out how often each keyword appears on the webpage.")
    
    url = st.text_input("Enter the URL to inspect:", "")
    keywords_input = st.text_input("Enter keywords to search for (comma-separated):", "")
    
    if st.button("Search Keywords"):
        if url and keywords_input:
            keywords = [k.strip() for k in keywords_input.split(',')]
            results = find_keywords_playwright(url, keywords)
            
            if results is not None:
                if results:
                    st.success("Keywords found:")
                    for keyword, matches in results.items():
                        st.write(f"'{keyword}': {len(matches)} occurrences")
                        st.write(f"Matches: {', '.join(matches)}")
                    
                    not_found = set(keywords) - set(results.keys())
                    if not_found:
                        st.info("Keywords not found:")
                        for keyword in not_found:
                            st.write(f"'{keyword}'")
                else:
                    st.warning("No keywords were found on the page.")
            else:
                st.error("Unable to process the page due to an error.")

            # Additional debugging information
            st.subheader("Additional Information:")
            try:
                import requests  # Ensure requests is imported
                response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10, verify=False)
                st.write(f"Status Code: {response.status_code}")
                st.write(f"Content Type: {response.headers.get('Content-Type', 'Not specified')}")
                st.write(f"Page Size: {len(response.text)} characters")
            except Exception as e:
                st.error(f"Failed to get additional information: {e}")

if __name__ == "__main__":
    main()
