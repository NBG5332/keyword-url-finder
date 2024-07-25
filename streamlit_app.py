import streamlit as st
import re
from playwright.sync_api import sync_playwright

def find_keywords_playwright(url, keywords):
    try:
        # Start Playwright and open a new browser context
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            # Visit the URL
            page.goto(url)

            # Get the full HTML content
            html_content = page.content().lower()

            # Close the browser
            browser.close()

        # Find matches for each keyword
        matches = {}
        for keyword in keywords:
            keyword_lower = keyword.lower()
            found = re.findall(r'(\S*' + re.escape(keyword_lower) + r'\S*)', html_content)
            count = len(found)
            if count > 0:
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
                response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10, verify=False)
                st.write(f"Status Code: {response.status_code}")
                st.write(f"Content Type: {response.headers.get('Content-Type', 'Not specified')}")
                st.write(f"Page Size: {len(response.text)} characters")
            except Exception as e:
                st.error(f"Failed to get additional information: {e}")

if __name__ == "__main__":
    main()
